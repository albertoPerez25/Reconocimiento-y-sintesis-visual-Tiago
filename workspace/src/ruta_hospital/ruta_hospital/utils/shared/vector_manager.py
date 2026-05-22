import os
import json
import shutil

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

CROSS_ENCODER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

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
        self.summary_path = os.path.join(base_dir, "latest_summary.txt")
        
        self.ollama_url = ollama_url
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.max_stored_rounds = max_stored_rounds
        self.use_reranker = use_reranker
        self.logger = logger

        self.reranker_model = None
        if self.use_reranker:
            try:
                from langchain_community.cross_encoders import HuggingFaceCrossEncoder
                # Modelo ultraligero especializado en relevancia de pares (Pregunta -> Contexto)
                self.reranker_model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2") # Se descarga/carga en memoria 1 sola vez en el ciclo de vida del nodo o Streamlit
                if self.logger:
                    self.logger.info("Modelo Cross-Encoder cargado correctamente en memoria.")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Fallo cargando el Cross-Encoder: {e}")
        
        # Inicialización de los motores locales
        self.embeddings = OllamaEmbeddings(model=self.embed_model, base_url=self.ollama_url)
        # Temperatura a 0.0 para evitar alucinaciones
        self.llm = ChatOllama(model=self.llm_model, base_url=self.ollama_url, temperature=0.0) 
        
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)

    def clear_all_data(self):
        '''Elimina los datos y la base vectorial de sesiones anteriores'''
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
            self.log_info(f"Limpiados datos temporales RAG en {self.base_dir}")
        os.makedirs(self.docs_dir, exist_ok=True)

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

    # INGESTIÓN Y GESTIÓN DE LA BASE DE DATOS (FAISS)
    def ingest_and_update_index(self, round_number, zone_data_dict):
        '''
        Recibe el diccionario de la vuelta actual, lo vuelca a texto plano,
        aplica la política de retención y reconstruye el índice FAISS.
        '''
        self.log_debug(f"Ingestando documentos para la vuelta {round_number}...")
        
        # Volcado a Disco
        round_dir = os.path.join(self.docs_dir, f"vuelta_{round_number}")
        os.makedirs(round_dir, exist_ok=True)
        
        for zone_name, data in zone_data_dict.items():
            file_path = os.path.join(round_dir, f"{zone_name}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Reporte de la Zona: {zone_name}\n")
                f.write(f"Vuelta: {round_number}\n")
                # Se guarda el JSON para que LangChain lo asimile como texto
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
                
        # Limpieza de vueltas antiguas
        self.apply_retention_policy()
        
        # Recreación del faiss de forma atómica
        self.rebuild_faiss_index()

    def apply_retention_policy(self):
        '''Elimina las carpetas de vueltas antiguas si superan max_stored_rounds'''
        if self.max_stored_rounds <= 0:
            return # 0 significa retención ilimitada
            
        folders = [f for f in os.listdir(self.docs_dir) if f.startswith("vuelta_")]
        folders.sort(key=lambda x: int(x.split("_")[1])) # Orden cronológico
        
        while len(folders) > self.max_stored_rounds:
            oldest = folders.pop(0)
            oldest_path = os.path.join(self.docs_dir, oldest)
            shutil.rmtree(oldest_path)
            self.log_debug(f"Política de retención: Eliminada carpeta antigua {oldest}")

    def rebuild_faiss_index(self):
        '''Lee los documentos restantes, inyecta metadatos y crea el VectorStore'''
        documents = []
        folders = [f for f in os.listdir(self.docs_dir) if f.startswith("vuelta_")]
        
        for folder in folders:
            round_num = int(folder.split("_")[1])
            folder_path = os.path.join(self.docs_dir, folder)
            
            loader = DirectoryLoader(folder_path, glob="*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
            folder_docs = loader.load()
            
            # Inyección de metadatos para el RAG temporal
            for doc in folder_docs:
                doc.metadata["vuelta"] = round_num
                basename = os.path.basename(doc.metadata["source"])
                doc.metadata["zona"] = os.path.splitext(basename)[0]
                
            documents.extend(folder_docs)
            
        if not documents:
            self.log_error("No hay documentos para indexar en FAISS.")
            return

        # Particionado estándar para RAG
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        # FAISS y BM25 es mejor que lean el nombre exacto de la sala, insertado en todos los chunks
        # para siempre poder recuperarlos por sala y evitar perder info
        chunks = [
            Document(
                page_content=f"[Zona: {c.metadata.get('zona', 'N/A')} | Vuelta: {c.metadata.get('vuelta', 'N/A')}]\n{c.page_content}",
                metadata=c.metadata
            )
            for c in text_splitter.split_documents(documents)
        ] # TODO: Quitar repeticion de estos metadatos, a través de eliminarlos en la creacion de los documentos o al cargarlos en RAM
        
        # Indexación en memoria y guardado a disco
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        vectorstore.save_local(self.faiss_path)
        self.log_debug(f"Índice FAISS reconstruido con {len(chunks)} fragmentos.")

    # GENERACIÓN DEL REPORTE (sustituye a RecursiveSummarizer)
    def generate_global_summary(self, round_number):
        '''Usa LangChain para generar el resumen narrativo de la última vuelta'''
        self.log_info(f"Generando resumen global para la vuelta {round_number}...")
        
        folder_path = os.path.join(self.docs_dir, f"vuelta_{round_number}")
        if not os.path.exists(folder_path):
            self.log_error(f"No hay datos para la vuelta {round_number}")
            return "Error: No hay datos registrados."
            
        loader = DirectoryLoader(folder_path, glob="*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
        docs = loader.load()
        
        if not docs:
            return "Todas las zonas patrulladas se encuentran despejadas."

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
        
        with open(self.summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
            
        self.log_info(f"Resumen guardado correctamente.")
        return summary_text

    def get_latest_summary(self):
        '''Utilidad para que el Chatbot Web cargue el último resumen rápidamente'''
        if os.path.exists(self.summary_path):
            with open(self.summary_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "No hay un resumen global disponible aún."


    # INTERFAZ CHATBOT Y EVALUADOR (LangChain RAG)
    def get_conversational_chain(self, memory_k=5, top_k_docs=3):
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
        lexic_retriever = BM25Retriever.from_documents(docs_in_faiss)
        lexic_retriever.k = top_k_docs
        
        # Fusión Híbrida (Reciprocal Rank Fusion - 50% peso léxico, 50% peso semántico)
        base_retriever = EnsembleRetriever(
            retrievers=[lexic_retriever, semantic_retriever],
            weights=[0.7, 0.3]
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