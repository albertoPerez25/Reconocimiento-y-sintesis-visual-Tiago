# Referencia de Parámetros: Módulo Reportero (`reporting`)

Este módulo se encarga de recibir los datos visuales, mantener el historial de la patrulla en una base de datos vectorial y generar los resúmenes en lenguaje natural de forma asíncrona.

| Parámetro | Por Defecto | Descripción |
| :--- | :--- | :--- |
| `perception_mode` | `"image"` | Define cómo se consumen los datos visuales. Puede ser `"image"` (foto a foto), `"sequence"` (grupo de fotos al salir de la zona) o `"video"` (clips continuos). |
| `llm_model` | `"llama3"` | Modelo de lenguaje que redactará el informe global al final de cada patrulla. |
| `ollama_url` | `"http://localhost:11434/"` | Dirección de la API local o remota donde se aloja el modelo de lenguaje. |
| `max_words` | `300` | Límite máximo de palabras para el resumen global generado. |
| `max_stored_rounds` | `5` | Número de vueltas de patrulla que se conservan en la memoria a corto plazo antes de ir borrando las más antiguas. |
| `resume_session` | `True` | Indica si el sistema debe intentar recuperar el historial de patrullas anteriores al arrancar. |
| `keep_photos` | `False` | Si está activado, los archivos multimedia originales no se borrarán del disco tras ser analizados. Útil para depurar. |
| `enforce_zone_match` | `True` | Mecanismo de seguridad que obliga al sistema a recuperar los datos de una zona específica si el usuario pregunta por ella directamente en el chat. |
| `semantic_map_path` | `".../semantic_map.json"` | Ruta al archivo que define las coordenadas y geometría de las habitaciones del hospital. |
| `metadata_path` | `".../hospital_metadata.json"` | Ruta al archivo que indica qué actividades son normales en cada zona para dar contexto al modelo. |
| `rag_dir` | `"/tmp/.../rag_data/"` | Carpeta temporal donde se guarda el índice de la base de datos vectorial y los textos en bruto de las detecciones. |
| `evidence_dir` | `"/tmp/.../alarm_evidences"` | Ruta donde se copian y guardan de forma persistente los archivos multimedia que han disparado una alerta crítica. |
| `metrics_dir` | `".../autogenerate_metrics/"` | Directorio de salida para los archivos que registran el rendimiento y los tiempos de ejecución del módulo. |