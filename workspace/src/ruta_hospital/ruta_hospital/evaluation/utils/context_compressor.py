import logging
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.summarize.chain import load_summarize_chain

class ContextCompressor:
    """
    Motor de compresión semántica para evaluación RAG (Patrón Map-Reduce).
    Principio SOLID (SRP): Única responsabilidad de transformar documentos brutos en una lista de viñetas densa.
    """
    
    def __init__(self, llm):
        """
        Inyección de dependencias: Recibe el modelo de lenguaje ya instanciado (Principio DRY).
        """
        self.llm = llm
        self.logger = logging.getLogger("ContextCompressor")
        self.logger.setLevel(logging.INFO)

        # PROMPT 1: FASE MAP (Extracción atómica)
        map_template = """Extrae de forma exhaustiva los eventos, detecciones de personas y anomalías de este fragmento de telemetría.
Devuelve estrictamente una lista de hechos cortos y objetivos.

REGLAS ESTRICTAS DE FORMATO:
- Cada viñeta debe ser una frase simple, natural y plana.
- PROHIBIDO usar desgloses gramaticales o sub-listas.
- PROHIBIDO usar etiquetas analíticas como "Sujeto:", "Verbo:", "Predicado:" o "Tiempo:".

Ejemplo de salida correcta:
- Una persona de pie mirando hacia la pared en Recepción
- Un hombre corriendo en el pasillo del Quirófano 2

Fragmento de telemetría:
{text}

Hechos extraídos:"""
        self.map_prompt = PromptTemplate(template=map_template, input_variables=["text"])

        # =====================================================================
        # PROMPT 2: FASE REDUCE (Consolidación)
        # =====================================================================
        reduce_template = """Combina los siguientes hechos extraídos en una única lista de viñetas consolidadas.
Elimina cualquier redundancia o repetición temporal, pero MANTÉN todos los detalles críticos únicos (personas, posturas, alarmas y tiempos exactos).

REGLAS ESTRICTAS DE FORMATO:
- Devuelve ÚNICAMENTE la lista de viñetas finales. No incluyas introducciones, ni comentarios, ni conclusiones.
- Cada viñeta debe ser una frase de texto plano.
- PROHIBIDO ABSOLUTAMENTE usar estructuras anidadas, tabulaciones o etiquetas como "Sujeto:", "Acción:" o similares.

Hechos recopilados:
{text}

Lista final consolidada:"""
        self.reduce_prompt = PromptTemplate(template=reduce_template, input_variables=["text"])

    def compress_documents(self, docs):
        """
        Ejecuta el pipeline de LangChain sobre una lista de documentos de FAISS.
        
        Args:
            docs (list[Document]): Lista de documentos recuperados.
            
        Returns:
            str: Un string masivo comprimido en formato viñetas.
        """
        if not docs:
            self.logger.warning("No se recibieron documentos para comprimir. Devolviendo contexto vacío.")
            return "Sin contexto disponible."

        self.logger.info(f"Iniciando compresión Map-Reduce de {len(docs)} documentos...")

        # Instanciamos la cadena nativa de LangChain asegurando nuestros prompts estrictos
        compress_chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            map_prompt=self.map_prompt,
            combine_prompt=self.reduce_prompt,
            verbose=False  # Ponlo a True temporalmente si el LLM local alucina y quieres ver las trazas
        )

        try:
            # Ejecución asíncrona/hilos manejada internamente por LangChain
            resultado = compress_chain.invoke(docs)
            
            # Extracción segura del texto resultante según la versión de LangChain
            if isinstance(resultado, dict) and 'output_text' in resultado:
                compressed_text = resultado['output_text'].strip()
            elif isinstance(resultado, str):
                compressed_text = resultado.strip()
            else:
                compressed_text = str(resultado).strip()

            self.logger.info("Contexto comprimido exitosamente.")
            return compressed_text

        except Exception as e:
            self.logger.error(f"Error crítico durante la compresión de contexto: {e}")
            # Fallback de seguridad: Si el LLM falla, devolvemos al menos algo de texto bruto
            # para no romper el pipeline completo de evaluación
            return f"[ERROR DE COMPRESIÓN] Contexto parcial: {docs[0].page_content[:500]}..."