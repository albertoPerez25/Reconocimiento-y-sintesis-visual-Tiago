# Referencia de Parámetros: Módulo de Capturas (`capturer`)

Este módulo orquesta la extracción de telemetría visual del entorno (imágenes estáticas, secuencias o clips de vídeo) sincronizada con la odometría de la plataforma y aplicando filtros de redundancia.

## Parámetros Compartidos (`BaseCaptureNode`)
Parámetros estructurales heredados por todas las estrategias de captura.

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `target_distance_meters` | `double` | `0.2` | Distancia euclidiana mínima (metros) que el robot debe desplazarse antes de habilitar una nueva captura. Mitiga la saturación de I/O cuando la plataforma está detenida. |
| `target_angle` | `double` | `0.785` | Desplazamiento angular mínimo (radianes) para forzar una captura durante giros estáticos. (`0.785 rad` ≈ `45°`). |
| `capture_mode` | `string` | `"image"` | Modo de orquestación y almacenamiento. Valores aceptados: `"image"` (streaming 1:1), `"sequence"` (agrupación temporal en buffer, enviada al cambiar de zona) o `"video"` (compilación de clip continuo). |
| `current_save_dir` | `string` | `""` | [Uso Interno] Ruta inyectada dinámicamente por la navegación (`patrol_node`) para la persistencia multimedia y del `metadata.csv`. |
| `current_zone` | `string` | `"Desconocida"` | [Uso Interno] Identificador semántico de la zona actual inyectado por el módulo de navegación. |

## Captura Fotográfica (`photos_node`)

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `similarity_threshold` | `double` | `5.0` | Umbral porcentual del Error Cuadrático Medio (MSE). Implementa un patrón *Early Exit* para descartar fotogramas visualmente redundantes, optimizando la carga computacional del perceptor aguas abajo. |

## Captura de Vídeo (`video_capturer_node`)

*Nota: Este nodo sobrescribe los valores base de distancia (`2.0 m`) y ángulo (`3.14 rad`) para adaptar la grabación a desplazamientos completos entre waypoints.*

| Parámetro | Tipo | Por Defecto | Descripción |
| :--- | :---: | :---: | :--- |
| `fps` | `double` | `10.0` | Tasa de muestreo (Frames Per Second) utilizada para codificar y compilar el clip final `.avi` (estándar XVID). |