# Referencia de Parámetros: Entorno de Evaluación (`evaluation`)

El módulo de evaluación automatiza la validación del sistema a través de la librería RAGAS, actuando sobre la percepción visual de forma aislada o sobre el sistema completo de generación de informes.

## Configuración General (Aplicable a ambos evaluadores)

| Parámetro | Por Defecto | Descripción |
| :--- | :--- | :--- |
| `ollama_url` | `http://localhost:11434` | Dirección de la API local o remota donde se alojan los modelos para la evaluación. |
| `evaluator_llm_model` | `llama3.1` | Modelo de lenguaje de gran tamaño que actuará como juez analizando y puntuando las respuestas del sistema. |
| `evaluator_embed_model` | `nomic-embed-text` | Modelo de embeddings empleado para calcular similitudes semánticas durante la evaluación. |
| `system_workers` | `1` | Cantidad de hilos simultáneos asignados a las tareas de evaluación del sistema completo. Permite acelerar el proceso si el hardware lo soporta. |
| `perceptor_workers` | `1` | Cantidad de hilos simultáneos permitidos para analizar imágenes de forma concurrente en la evaluación de la percepción aislada. |
| `system_timeout` | `1420` | Tiempo máximo de espera en segundos antes de cancelar una prueba del sistema por inactividad. |
| `perceptor_timeout` | `1420` | Límite de tiempo en segundos para procesar visualmente una escena antes de dar error. |
| `evaluation_name` | `generic` | Nombre que sirve como prefijo para identificar los archivos de resultados generados en las pruebas. |
| `evaluation_mode` | `full` | Modalidad de ejecución de la prueba. Los valores admitidos son `full` para ejecutar todo el proceso, `generate_only` para crear las respuestas sin juzgarlas, o `evaluate_only` para calificar datos previamente generados. |
| `answers_file` | `/tmp/...` | Archivo temporal donde se respaldan las respuestas del robot antes de ser evaluadas, útil para depuración o interrupciones. |
| `metrics_dir` | `.../autogenerate_metrics/` | Carpeta de salida física donde se almacenarán las puntuaciones y comparativas generadas en formato CSV y JSON. |
| `max_words` | `300` | Límite aproximado de extensión que se le exige al modelo a la hora de generar los resúmenes evaluados. |
| `max_stored_rounds` | `5` | Rondas de memoria retenidas en el gestor de conocimiento para comprobar si el sistema es capaz de olvidar información muy antigua. |

## Evaluador de Percepción (`perception_evaluator_node`)

Valida en exclusiva qué tan bien "ven" y describen los modelos acoplados ante el conjunto de datos estáticos.

| Parámetro | Por Defecto | Descripción |
| :--- | :--- | :--- |
| `dataset_path` | `.../perception_dataset.json` | Archivo donde se estructuran las respuestas correctas esperadas para cada escena. |
| `images_dir` | `.../test_dataset/` | Directorio con las fotografías y recursos visuales sobre los que se van a hacer las preguntas. |
| `tested_model_name` | `unknown_model` | Etiqueta para el reporte final que ayuda a diferenciar qué modelo exacto ha sido puesto a prueba. |

## Evaluador de Sistema (`system_evaluator_node`)

Comprueba la calidad integral: desde la capacidad del robot para navegar simuladamente un dataset, hasta el guardado en base de datos y la redacción del informe.

| Parámetro | Por Defecto | Descripción |
| :--- | :--- | :--- |
| `questions_path` | `.../quest.json` | Banco de pruebas con preguntas cortas y resúmenes para interrogar la memoria del sistema. |
| `eval_folder_path` | `.../vuelta_A/` | Carpeta que simula los resultados de una patrulla real, conteniendo imágenes y telemetría de ubicación. |
| `perception_mode` | `image` | Forma de procesar los datos de la carpeta. Se puede configurar para trabajar con capturas sueltas, secuencias o vídeos. |
| `use_reranker` | `True` | Activa el filtro avanzado de relevancia en la búsqueda de contexto para tratar de mejorar la precisión de las respuestas evaluadas. |
| `resume_session` | `True` | Indica al sistema que puede utilizar una base de conocimiento ya existente si la encuentra, saltándose la fase de ingesta de datos. |
| `evaluation_target` | `both` | Define si RAGAS debe corregir solo las preguntas directas (`short_only`), solo la narrativa final (`summary_only`) o todo el conjunto (`both`). |
| `use_context_compressor` | `False` | Aplica una técnica previa de resumen sobre los eventos registrados para comprimir el texto y no desbordar al modelo evaluador. |
| `enforce_zone_match` | `True` | Regla estricta que exige al buscador de datos localizar primero el nombre de la habitación antes de responder. |