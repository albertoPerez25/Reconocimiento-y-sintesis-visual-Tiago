import os
import sys
import time
import streamlit as st
from ruta_hospital.utils.shared.vector_manager import VectorManager

# Configuración inicial de Streamlit
st.set_page_config(page_title="Chatbot de patrulla", page_icon="🤖", layout="wide")

# Rutas de directorios basadas en la misma configuración del sistema
RAG_DIR = "/tmp/ruta_hospital_rag_data/"

# Reranker
use_reranker_env = os.environ.get("USE_RERANKER", "False").lower() in ("true", "1", "yes")
use_reranker_arg = "--use-reranker" in sys.argv
USE_RERANKER = use_reranker_env or use_reranker_arg

def get_index_mtime(base_dir):
    """
    Lee el timestamp de modificación del índice FAISS físico.
    Si el archivo no existe (ej: inicio de la patrulla), devuelve 0.0.
    """
    index_path = os.path.join(base_dir, "patrol_faiss_index", "index.faiss")
    if os.path.exists(index_path):
        return os.path.getmtime(index_path)
    return 0.0

@st.cache_resource
def get_vector_manager(use_reranker=False, index_timestamp=0.0):
    # Inicializa el gestor y lo cachea. 
    # Streamlit reinicializará la función automáticamente si 'index_timestamp' cambia.
    return VectorManager(
        base_dir=RAG_DIR,
        ollama_url="http://localhost:11434", 
        llm_model="llama3",
        max_stored_rounds=5, 
        use_reranker=use_reranker
    )

current_index_mtime = get_index_mtime(RAG_DIR)
vector_manager = get_vector_manager(USE_RERANKER, current_index_mtime) # Inyección del timestamp


def main():
    st.title("Chatbot de patrulla")

    # BARRA LATERAL: Visor de resúmenes 
    with st.sidebar:
        st.header("Resúmenes Anteriores")
        
        # Encontrar todas las vueltas disponibles en el disco
        docs_dir = os.path.join(RAG_DIR, "db_docs")
        vueltas_disponibles = []
        if os.path.exists(docs_dir):
            for d in os.listdir(docs_dir):
                if d.startswith("vuelta_"):
                    # Extraer número
                    num = d.split("_")[1]
                    vueltas_disponibles.append(int(num))
        
        vueltas_disponibles.sort(reverse=True) # Mostrar la última primero

        if vueltas_disponibles:
            vuelta_seleccionada = st.selectbox("Selecciona una vuelta para ver su resumen:", vueltas_disponibles)
            
            # Carga dinámica del resumen solicitado
            resumen_texto = vector_manager.get_summary_for_round(vuelta_seleccionada)
            st.info(resumen_texto)
        else:
            st.info("No hay vueltas registradas aún en el sistema.")


    # CHAT PRINCIPAL
    # Inicializar el historial del chat y la cadena RAG en el estado de la sesión
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Mostrar el resumen automáticamente al inicio
        latest_summary = vector_manager.get_latest_summary()
        if latest_summary and "No hay un resumen" not in latest_summary:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**RESUMEN DE LA ÚLTIMA PATRULLA:**\n\n{latest_summary}"
            })
            
    if "rag_chain" not in st.session_state:
        with st.spinner("Conectando con la base de conocimientos (FAISS)..."):
            st.session_state.rag_chain = vector_manager.get_conversational_chain()

    # Mostrar mensajes guardados
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Comprobar si hay cadena (si el índice FAISS existe) y pantalla de espera
    if not st.session_state.rag_chain:
        # Comprobamos silenciosamente si FAISS acaba de ser creado en disco
        faiss_file = os.path.join(vector_manager.faiss_path, "index.faiss")
        
        if os.path.exists(faiss_file):
            # Cargamos la cadena y recargamos la web
            st.session_state.rag_chain = vector_manager.get_conversational_chain()
            st.rerun()
        else:
            # Pantalla de espera amigable que se actualiza cada 3 segundos
            st.info("⏳ **Esperando telemetría...**")
            time.sleep(3)
            st.rerun() # Fuerza a Streamlit a volver a comprobar

    # Input del usuario
    if prompt := st.chat_input("Pregúntame sobre las rondas de patrulla..."):
        # Añadir mensaje del usuario a la interfaz
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta de la IA
        with st.chat_message("assistant"):
            with st.spinner("Analizando registros..."):
                try:
                    # En LangChain la clave 'question' depende de tu prompt. 
                    # Normalmente ConversationalRetrievalChain usa 'question'.
                    response_dict = st.session_state.rag_chain.invoke({"question": prompt})
                    
                    # La salida depende de si output_key="answer" está configurado.
                    # Si no, por defecto puede ser 'answer'.
                    answer = response_dict.get("answer", "No se generó respuesta.")
                    source_docs = response_dict.get("source_documents", [])
                    
                    st.markdown(answer)
                    with st.expander("🔍 Ver contexto que FAISS le pasó al LLM (Debug)"):
                        if not source_docs:
                            st.warning("FAISS no encontró ningún documento que coincidiera con tu pregunta.")
                        else:
                            for i, doc in enumerate(source_docs):
                                source_name = doc.metadata.get("source", "Desconocido")
                                st.write(f"**Documento {i+1} | Archivo:** `{source_name}`")
                                st.text(doc.page_content)

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"Hubo un error al procesar tu petición: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == '__main__':
    main()
