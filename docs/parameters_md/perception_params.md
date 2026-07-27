# Referencia de Parámetros: Módulo de Percepción (`perception`)

Este módulo implementa el pipeline de visión artificial. Utiliza un patrón *Strategy* para desacoplar la orquestación de la inferencia, permitiendo acoplar modelos posicionales (YOLO) y semánticos (VLMs) en tiempo de ejecución.

## Parámetros Base Compartidos

Todas las clases heredan de `BasePerceptionNode`, y se dividen en dos ramas: `BasePositionPerceptionNode` (geometría) y `BaseVLMPerceptionNode` (semántica multimodal).

| Parámetro | Aplicable a | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `metrics_dir` | Todos | `".../docs/autogenerate_metrics/"` | Ruta donde el nodo volcará su rendimiento de inferencia (latencia por frame) en un JSON al cerrarse. |
| `min_area_ratio` | Posicionales | `0.03` | Proporción mínima del área de la imagen que debe ocupar un *bounding box*. Filtra falsos positivos y descarta personas en la lejanía (ej. detrás de cristales). |
| `vlm_model` | VLMs | `moondream` (Seq) / `qwen3.5:4b` (Vid, Img) | Identificador exacto del modelo desplegado en la API de Ollama. |
| `ollama_url` | VLMs | `"http://localhost:11434/api/generate"` | Endpoint de la API REST local (o cloud) de inferencia. |
| `model_word_limit`| VLMs | `30` | Restricción sintética inyectada en el prompt del sistema para forzar respuestas telegráficas y reducir latencia. |
| `image_size` | VLMs | `[640, 480]` | Resolución de *downsampling* antes de codificar en Base64. Ahorra ancho de banda HTTP y acelera la inferencia del VLM. |

## Orquestador Híbrido (`hybrid_perception_node`)

Implementa una salida temprana (*Early Exit*). Si YOLO determina que la sala está vacía, no se invoca al VLM.

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `position_estimators` | `string_array` | `['...YoloPerceptionNode']` | Rutas completas a las clases de Python que actúan como estimadores posicionales. Instanciadas dinámicamente mediante `importlib`. |
| `vlm_estimators` | `string_array` | `['...VLMPerceptionNode']` | Rutas a las clases VLM a acoplar. Para modo vídeo debe sustituirse por `...VideoPerceptionNode`. |
| `save_debug_images` | `bool` | `False` | Si es `True`, guarda en el SO la imagen superpuesta con las cajas delimitadoras de YOLO y su tracking antes de enviarla al VLM. |
| `annotated_image_path`| `string` | `"/tmp/annotated_vlm_frame.jpg"` | Ruta efímera donde se guardan las capturas de debug si el parámetro anterior está activo. |
| `include_pose_output` | `bool` | `False` | Si es `True`, concatena el output crudo de YOLO ("2 personas sentadas") con la descripción narrativa del VLM. Si es `False`, el VLM absorbe el output, salvo condición de override de seguridad. |

## Estimador Posicional (`yolo_perception_node`)

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `yolo_model` | `string` | `"yolo26n-pose.pt"` | Modelo de Ultralytics a cargar en memoria (TensorRT/CUDA). |
| `min_confidence`| `double` | `0.5` | Umbral de confianza mínimo de los keypoints de YOLO para dar por válida una postura y calcular alertas. |

## Inferencia por Vídeo (`video_perception_node`)

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `sampled_frames` | `int` | `5` | Número de fotogramas clave a extraer de forma equidistante a lo largo de todo el clip `.avi` para dárselos como contexto al VLM. |
| `save_sampled_frames`| `bool` | `False` | Guarda los fotogramas clave extraídos del vídeo para auditoría manual. |
| `sampled_frames_dir` | `string` | `"/tmp/video_perception_debug/"`| Ruta efímera de volcado para la auditoría de *sampled frames*. |