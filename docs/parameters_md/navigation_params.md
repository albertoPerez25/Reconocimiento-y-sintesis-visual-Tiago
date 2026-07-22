# Referencia de Parámetros: Módulo de Navegación (`navigation`)

El nodo `patrol_node` es el orquestador principal del movimiento autónomo de TIAGo. Controla la máquina de estados del framework *Nav2*, monitorea transiciones semánticas de sala, y delega (mediante el patrón *Fire-and-Forget*) la captura visual y el reporte asíncrono.

## Nodo de Patrulla (`patrol_node`)

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `route_file_path` | `string` | `".../config/route_waypoints.json"` | Ruta absoluta o resolutiva al archivo JSON que lista los *waypoints* (x, y) cartesianos del ciclo de patrullaje. |
| `base_photos_dir` | `string` | `".../datasets/hospital_photos/"` | Directorio raíz donde el nodo genera automáticamente las jerarquías de volcado temporal (`vuelta_A`, `vuelta_B`, etc.) por cada iteración inyectando el path mediante parámetros al nodo capturador. |
| `keep_temp_folders` | `bool` | `False` | Si es `True`, inhibe la rutina de limpieza que borra los archivos multimedia del sistema de archivos local una vez que el Orquestador RAG los ha consumido (esencial para *debugging* o para testear el chatbot). |
| `capturer_node_name` | `string` | `"photos_node"` | Inyección de dependencia (Dependency Injection) del nombre de dominio del módulo responsable de la inferencia. Necesario para notificar vía RPC transiciones de sala al perceptor de turno. |
| `use_reranker` | `bool` | `False` | Parámetro ambiental inyectado mediante sub-proceso a la UI de *Streamlit* cuando se invoca interactivamente la consola (pulsando la tecla `c` en terminal) durante la patrulla. |