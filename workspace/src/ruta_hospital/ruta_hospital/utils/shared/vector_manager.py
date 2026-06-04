import os
import re
import json
import shutil
import unicodedata

# ECOSISTEMA COMUNITARIO 
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings

# BÚSQUEDA HÍBRIDA
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document

# IMPORTACIONES PROFUNDAS 
from langchain_classic.chains.summarize.chain import load_summarize_chain
from langchain_classic.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_classic.memory.buffer_window import ConversationBufferWindowMemory
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
from langchain_classic.chains.query_constructor.base import AttributeInfo

# PROMPTS
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

#CROSS_ENCODER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2" # este NO es multilingual
CROSS_ENCODER_MODEL_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

class VectorManager:
    '''
    Clase encargada de orquestar la ingesta de documentos, la gestión del almacenamiento
    (FAISS), y la creación de cadenas de inferencia RAG utilizando LangChain y Ollama.
    '''
    def __init__(self, base_dir, ollama_url="http://localhost:11434", 
                 llm_model="llama3", embed_model="nomic-embed-text",
                 max_stored_rounds=5, use_reranker=False, logger=None):
        
        self.base_dir = base_dir
        self.docs_dir = os.path.join(base_dir, "db_docs")
        self.faiss_path = os.path.join(base_dir, "patrol_faiss_index")
        
        self.ollama_url = ollama_url
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.max_stored_rounds = max_stored_rounds
        self.use_reranker = use_reranker
        self.logger = logger

        self.reranker_model = None
        self.load_reranker_model_if_needed()
        
        # Inicialización de los motores locales
        self.embeddings = OllamaEmbeddings(model=self.embed_model, base_url=self.ollama_url)
        # Temperatura a 0.0 para evitar alucinaciones
        self.llm = ChatOllama(model=self.llm_model, base_url=self.ollama_url, temperature=0.0) 
        
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)

        self.last_saved_zone = None

    def load_reranker_model_if_needed(self):
        '''Carga el modelo de reranking en memoria solo si no estaba cargado previamente.'''
        if self.use_reranker and self.reranker_model is None:
            try:
                from langchain_community.cross_encoders import HuggingFaceCrossEncoder
                # Modelo ultraligero especializado en relevancia de pares (Pregunta -> Contexto)
                self.reranker_model = HuggingFaceCrossEncoder(model_name=CROSS_ENCODER_MODEL_NAME)
                if self.logger:
                    self.logger.info("Modelo Cross-Encoder cargado en memoria")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Fallo cargando el Cross-Encoder: {e}")

    
    def atomic_save_faiss(self, vectorstore):
        '''
        Guarda el índice vectorial de forma atómica para evitar lecturas sucias
        (Stale Reads / EOFErrors) por parte de Streamlit
        '''
        temp_dir = self.faiss_path + "_temp"
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(self.faiss_path, exist_ok=True)
        
        # Langchain guarda en la carpeta temporal de forma estándar (no atómica)
        vectorstore.save_local(temp_dir)
        
        # Rutas de la transacción
        pkl_temp = os.path.join(temp_dir, "index.pkl")
        faiss_temp = os.path.join(temp_dir, "index.faiss")
        
        pkl_target = os.path.join(self.faiss_path, "index.pkl")
        faiss_target = os.path.join(self.faiss_path, "index.faiss")
        
        # El Chatbot vigila el mtime de 'index.faiss'. 
        # Movemos 'index.pkl' primero de forma silenciosa.
        if os.path.exists(pkl_temp):
            os.replace(pkl_temp, pkl_target)
        
        # Al mover 'index.faiss', el SO actualiza el mtime y dispara la recarga de Streamlit.
        # Como index.pkl ya está actualizado, la lectura es 100% segura.
        if os.path.exists(faiss_temp):
            os.replace(faiss_temp, faiss_target)


    def clear_all_data(self, force_clear=True):
        '''
        Elimina los datos y la base vectorial de sesiones anteriores si force_clear es True.
        Si es False, solo se asegura de que los directorios existan.
        '''
        if force_clear:
            if os.path.exists(self.base_dir):
                shutil.rmtree(self.base_dir)
                self.log_info(f"Limpiados datos temporales RAG en {self.base_dir} (Arranque Limpio)")
        else:
            self.log_info(f"Modo Resume Session ON: Conservando datos previos en {self.base_dir}")
            
        os.makedirs(self.docs_dir, exist_ok=True)

    def get_highest_round_in_disk(self):
        '''Busca en los metadatos de FAISS la vuelta lógica más alta registrada'''
        faiss_file = os.path.join(self.faiss_path, "index.faiss")
        
        # Si FAISS no está en RAM pero existe en disco, rehidratacion
        if getattr(self, 'vector_store', None) is None and os.path.exists(faiss_file):
            try:
                self.vector_store = FAISS.load_local(
                    self.faiss_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                self.log_info("FAISS rehidratado exitosamente para comprobar la sesión.")
            except Exception as e:
                self.log_error(f"No se pudo cargar FAISS para rehidratar: {e}")
                return 0
                
        # Si no hay base de datos, empieza en 0
        if getattr(self, 'vector_store', None) is None:
            return 0
            
        # Extraer la vuelta máxima registrada en los vectores
        highest_round = 0
        for doc in self.vector_store.docstore._dict.values():
            doc_round = doc.metadata.get("vuelta", 0)
            if doc_round > highest_round:
                highest_round = doc_round
                
        return highest_round

    def log_info(self, msg):
        if self.logger: 
            self.logger.info(msg)
        else: 
            print(f"[INFO] {msg}")

    def log_error(self, msg):
        if self.logger: 
            self.logger.error(msg)
        else: 
            print(f"[ERROR] {msg}")

    def log_debug(self, msg):
        if self.logger: 
            self.logger.debug(msg)
        else: 
            print(f"[DEBUG] {msg}")

    def preprocess_spanish_text(self, text: str) -> str:
        """Elimina acentos y pasa todo a minusculas para mejorar la recuperación"""
        if not text: return ""
        text = text.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', text) 
                        if unicodedata.category(c) != 'Mn')

   
    # GENERACIÓN DEL REPORTE (sustituye a RecursiveSummarizer)
    def generate_global_summary(self, hospital_data_dict, round_number):
        '''Usa LangChain para generar el resumen narrativo directamente desde el dict en memoria (Cero I/O)'''
        self.log_info(f"Generando resumen global para la vuelta {round_number} con LangChain...")
        
        if not hospital_data_dict:
            summary_text = "Todas las zonas patrulladas se encuentran despejadas"
        else:

            # Convertir diccionario en una lista de Documents de LangChain al vuelo
            docs = []
            for zone, info in hospital_data_dict.items():
                if info.get("eventos_recientes"):
                    content = f"ZONA: {zone}\n{json.dumps(info, ensure_ascii=False)}"
                else:
                    content = f"ZONA: {zone}\nSin eventos detectados, despejada."
                
                docs.append(Document(page_content=content, metadata={"zona": zone}))

            # Plantillas en español para la cadena Map-Reduce
            map_prompt = PromptTemplate(
                template="Resume brevemente las actividades de este reporte de zona. Mantén detalles de personas, horas y anomalías.\nReporte:\n{text}\nResumen:",
                input_variables=["text"]
            )
            combine_prompt = PromptTemplate(
                template="Eres la IA de reconocimiento de actividades y humanos del hospital. Escribe un RESUMEN GLOBAL profesional combinando los siguientes reportes.\nReportes:\n{text}\nRESUMEN GLOBAL EN ESPAÑOL:",
                input_variables=["text"]
            )

            chain = load_summarize_chain(
                self.llm, 
                chain_type="map_reduce",
                map_prompt=map_prompt,
                combine_prompt=combine_prompt
            )
            
            summary = chain.invoke(docs)
            summary_text = summary["output_text"].strip()

        round_dir = os.path.join(self.docs_dir, f"vuelta_{round_number}")
        os.makedirs(round_dir, exist_ok=True) 
        summary_path = os.path.join(round_dir, "resumen.txt")
        
        # Persistir el último resumen para la UI del Chatbot
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
            
        self.log_info(f"Resumen LangChain de la vuelta {round_number} generado y guardado correctamente.")
        return summary_text

    def get_summary_for_round(self, round_number):
        '''Carga el resumen específico de una vuelta desde su carpeta'''
        summary_path = os.path.join(self.docs_dir, f"vuelta_{round_number}", "resumen.txt")
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"No hay un resumen disponible para la vuelta {round_number}."

    def get_latest_summary(self):
        '''Utilidad para que el Chatbot Web cargue el último resumen rápidamente'''
        highest_round = self.get_highest_round_in_disk()
        # FAISS puede decir que esta en la vuelta 3 (porque ya hay fotos), 
        # pero si el resumen de la 3 aún no se ha generado, busca en la 2, luego en la 1...
        for round_num in range(highest_round, 0, -1):
            summary_path = os.path.join(self.docs_dir, f"vuelta_{round_num}", "resumen.txt")
            if os.path.exists(summary_path):
                self.log_debug(f"Último resumen validado y cargado desde la vuelta {round_num}")
                return self.get_summary_for_round(round_num)
        return "No hay un resumen global disponible aún."


    # INTERFAZ CHATBOT Y EVALUADOR (LangChain RAG)
    def get_conversational_chain(self, memory_k=5, top_k_docs=3): # TODO: Dividir
        '''Construye la cadena RAG con memoria de ventana y SelfQuerying para el Chatbot'''
        if not os.path.exists(self.faiss_path):
            self.log_error("No se encontró el índice FAISS. Necesitas completar una patrulla primero.")
            return None
            
        # allow_dangerous_deserialization=True es requerido por FAISS en versiones modernas para cargar archivos locales
        vectorstore = FAISS.load_local(self.faiss_path, self.embeddings, allow_dangerous_deserialization=True)

        # Con reranker (opcional) usar el doble o 9, pues se filtrara luego
        initial_k = max(9, top_k_docs * 2) if self.use_reranker else top_k_docs
        
        # Buscador Denso (Semántico FAISS)
        semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": initial_k})
        
        # Buscador Disperso (Léxico BM25)
        docs_in_faiss = list(vectorstore.docstore._dict.values())
        lexic_retriever = BM25Retriever.from_documents(
            docs_in_faiss,
            preprocess_func=self.preprocess_spanish_text
        )
        lexic_retriever.k = top_k_docs
        
        # Fusión Híbrida (Reciprocal Rank Fusion, 50% peso léxico, 50% peso semántico)
        base_retriever = EnsembleRetriever(
            retrievers=[lexic_retriever, semantic_retriever],
            weights=[0.5, 0.5]
        )

        # Configuración de la memoria
        memory = ConversationBufferWindowMemory(
            k=memory_k,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer" # Crítico para que LangChain guarde solo la respuesta final y no los documentos fuente
        )

        # Compresión y Re-Clasificación (Cross-Encoder)
        if self.use_reranker:
            # Importación Lazy: No consume memoria ni tiempo si el nodo lo tiene desactivado   
            from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
            from langchain_classic.retrievers import ContextualCompressionRetriever  
                
            compressor = CrossEncoderReranker(model=self.reranker_model, top_n=top_k_docs)
            retriever = ContextualCompressionRetriever(
                base_compressor=compressor, base_retriever=base_retriever
            )
            self.log_debug("Retriever configurado: Híbrido + Cross-Encoder Reranker")
        else:
            retriever = base_retriever
            self.log_debug("Retriever configurado: Híbrido Estándar")

        valid_zones = set()
        if os.path.exists(self.docs_dir):
            for folder in os.listdir(self.docs_dir):
                folder_path = os.path.join(self.docs_dir, folder)
                if os.path.isdir(folder_path):
                    for f in os.listdir(folder_path):
                        if f.endswith(".txt"):
                            valid_zones.add(f.replace(".txt", ""))
        zones_str = ", ".join(valid_zones) if valid_zones else "Zonas desconocidas"

        condense_template = f"""Dada la siguiente conversación y una nueva pregunta, reformula la nueva pregunta para que sea una búsqueda independiente en ESPAÑOL.
        
        IMPORTANTE: El mapa del sistema tiene EXACTAMENTE estas zonas válidas: [{zones_str}].
        Si el usuario pregunta por un lugar, usa el NOMBRE EXACTO de la lista anterior que más se le parezca.
        
        Historial del chat:
        {{chat_history}}
        
        Nueva pregunta: {{question}}
        Búsqueda independiente en español:"""

        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_template)

        # Prompt del asistente
        system_template = """Eres una IA de reconocimiento de actividades y humanos de un hospital.
Responde de forma concisa basándote ÚNICAMENTE en el siguiente contexto extraído de los sensores.
Si no sabes la respuesta basándote en este contexto, di que no hay información registrada. No inventes datos.

CONTEXTO DE SENSORES RECUPERADO:
{context}"""

        qa_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{question}")
        ])

        # Ensamblaje de la cadena
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True, #para que RAGAS pueda evaluar la fidelidad exacta
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            condense_question_prompt=CONDENSE_QUESTION_PROMPT
        )
        
        return chain
    
    def add_single_event_to_index(self, zone_name, event_data, round_num):
        '''
        Añade un evento individual al índice FAISS en tiempo real y persiste en disco.
        (Arquitectura Streaming / Real-Time RAG)
        '''
        # Recuperar la inyección dura de metadatos en el texto para ayudar a BM25
        zone_type = event_data.get("tipo_zona", "Desconocida") 
        content = f"[Zona: {zone_name} | Tipo: {zone_type} | Vuelta: {round_num}]\nEvento detectado:\n{json.dumps(event_data, ensure_ascii=False)}"
        
        # Crear documento atómico con metadatos de trazabilidad (Alineado con esquema antiguo)
        doc = Document(
            page_content=content,
            metadata={
                "zona": zone_name,
                "tipo_zona": zone_type,
                "vuelta": round_num,
                "source": zone_name, # Mantenido por compatibilidad con cadenas RAG base
                "timestamp": event_data.get("tiempo", "")
            }
        )

        try:
            if getattr(self, 'vector_store', None) is None:
                # Comprobar si el disco ya tiene un índice guardado (Rehidratación)
                if os.path.exists(os.path.join(self.faiss_path, "index.faiss")):
                    self.logger.debug(f"Recuperando índice FAISS del disco antes de inyectar evento de {zone_name}")
                    self.vector_store = FAISS.load_local(
                        self.faiss_path, 
                        self.embeddings, 
                        allow_dangerous_deserialization=True
                    )
                    self.vector_store.add_documents([doc])
                else:
                    # Si no hay nada en RAM ni en disco, desde cero
                    self.logger.debug(f"Inicializando FAISS en memoria con primer evento en {zone_name}")
                    self.vector_store = FAISS.from_documents([doc], self.embeddings)
            else:
                # Flujo normal en tiempo real
                self.logger.debug(f"Añadiendo evento de {zone_name} a FAISS existente")
                self.vector_store.add_documents([doc])

                # Semantic Checkpointing (Guardar solo al cambiar de zona)
                if self.last_saved_zone is not None and self.last_saved_zone != zone_name:
                    self.atomic_save_faiss(self.vector_store)
                    self.logger.debug(f"Transición de zona ({self.last_saved_zone} -> {zone_name}). Índice FAISS persistido en disco.")
                    self.last_saved_zone = zone_name
                elif self.last_saved_zone is None:
                    self.last_saved_zone = zone_name
            
        except Exception as e:
            self.logger.error(f"Error fatal insertando evento en FAISS: {e}")

            
    def dump_round_data_to_disk(self, round_number, hospital_data_dict):
        '''
        Vuelca el diccionario de la vuelta a archivos .txt físicos.
        Uso exclusivo para Debugging y poblar la UI de Streamlit.
        No afecta a FAISS (que ya se actualiza en streaming).
        '''
        self.log_debug(f"Guardando snapshot en disco para la vuelta {round_number} (Debug/UI)...")
        
        round_dir = os.path.join(self.docs_dir, f"vuelta_{round_number}")
        os.makedirs(round_dir, exist_ok=True)
        
        for zone_name, data in hospital_data_dict.items():
            file_path = os.path.join(round_dir, f"{zone_name}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Reporte de la Zona: {zone_name}\n")
                f.write(f"Vuelta: {round_number}\n")
                f.write(json.dumps(data, ensure_ascii=False, indent=2))

        # Guardado final forzado para asegurar los datos de la última zona patrullada
        if getattr(self, 'vector_store', None) is not None:
            self.atomic_save_faiss(self.vector_store)
            self.log_debug(f"Índice FAISS persistido en disco (Fin de la vuelta {round_number}).")
                
        # Limpieza de carpetas antiguas para no saturar el disco y FAISS
        self.apply_file_retention_policy()
        self.apply_faiss_retention_policy(round_number)

    def apply_file_retention_policy(self):
        '''Elimina las carpetas txt antiguas si superan max_stored_rounds'''
        if self.max_stored_rounds <= 0:
            return 
            
        folders = [f for f in os.listdir(self.docs_dir) if f.startswith("vuelta_")]
        folders.sort(key=lambda x: int(x.split("_")[1])) 
        
        while len(folders) > self.max_stored_rounds:
            oldest = folders.pop(0)
            oldest_path = os.path.join(self.docs_dir, oldest)
            shutil.rmtree(oldest_path)
            self.log_debug(f"Política de retención (Archivos): Eliminada carpeta {oldest}")

    def apply_faiss_retention_policy(self, current_round):
        '''Elimina del índice vectorial en memoria los documentos de vueltas muy antiguas'''
        if self.max_stored_rounds <= 0 or getattr(self, 'vector_store', None) is None:
            return

        threshold_round = current_round - self.max_stored_rounds
        ids_to_delete = []

        # Acceso profundo al almacén de documentos subyacente de LangChain/FAISS
        for doc_id, doc in self.vector_store.docstore._dict.items():
            doc_round = doc.metadata.get("vuelta", current_round)
            if doc_round <= threshold_round:
                ids_to_delete.append(doc_id)

        if ids_to_delete:
            self.vector_store.delete(ids_to_delete)
            self.log_debug(f"Política de retención (FAISS): Eliminados {len(ids_to_delete)} vectores antiguos.")
            self.atomic_save_faiss(self.vector_store)