# Referencia de Parámetros: Interfaz de Usuario (`chatbot`)

La interfaz web está desarrollada en Streamlit. Al no operar como un nodo nativo de ROS 2, su configuración no depende del sistema de parámetros estándar, sino que se realiza mediante variables de entorno o argumentos de línea de comandos. 

| Variable de Entorno | Argumento CLI | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `RAG_DIR` | - | `"/tmp/.../rag_data/"` | Directorio donde el sistema busca los archivos del índice vectorial y los reportes en texto de la patrulla para poder contestar a las preguntas. |
| `OLLAMA_URL` | - | `"http://localhost:11434"` | Dirección del servicio de inferencia que proporcionará las respuestas durante la conversación. |
| `LLM_MODEL` | - | `"llama3"` | Identificador del modelo de lenguaje encargado de procesar el contexto y redactar las respuestas al usuario. |
| `MAX_STORED_ROUNDS` | - | `5` | Define cuántas vueltas de patrulla previas se listarán en el menú lateral de la interfaz. |
| `USE_RERANKER` | `--use-reranker` | `False` | Habilita un paso extra en la búsqueda de información, ordenando los datos relevantes mediante un modelo especializado antes de dárselos al chatbot. |

*Nota: Para pasar argumentos CLI a un script de Streamlit como este, es necesario prefijar "--" seguido del argumento. Ej. script_de_streamlit.py -- --use-reranker*.