import os
import streamlit as st
from ruta_hospital.utils.shared.vector_manager import VectorManager

import langchain
langchain.debug = True

# Configuración inicial de Streamlit
st.set_page_config(page_title="Chatbot de patrulla", page_icon="🤖", layout="wide")

# Rutas de directorios basadas en la misma configuración del sistema
RAG_DIR = "/tmp/ruta_hospital_rag_data/"

@st.cache_resource
def get_vector_manager():
    # Inicializa el gestor y lo cachea para no recargarlo en cada interacción de Streamlit
    return VectorManager(
        base_dir=RAG_DIR,
        # Asume la URL por defecto de Ollama, si se cambia en ROS, deberá ajustarse aquí
        ollama_url="http://localhost:11434", 
        llm_model="llama3",
        max_stored_rounds=5 # Para evitar errores de lectura
    )

vector_manager = get_vector_manager()

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
            
            # Cargar el resumen general más reciente si la seleccionada es la última
            # Si no, podría generar uno, pero por simplicidad solo leemos el general
            if vuelta_seleccionada == vueltas_disponibles[0]:
                st.info(vector_manager.get_latest_summary())
            else:
                st.warning(f"Los datos crudos de la Vuelta {vuelta_seleccionada} están disponibles en FAISS. Pregúntale al chatbot para más detalles.")
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

    # Comprobar si hay cadena (si el índice FAISS existe)
    if not st.session_state.rag_chain:
        st.error("No se pudo iniciar el sistema de IA. Asegúrate de que el robot ha terminado al menos una patrulla para generar la base de datos.")
        st.stop()

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
