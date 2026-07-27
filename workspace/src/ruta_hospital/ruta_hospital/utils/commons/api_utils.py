import base64
import requests
import cv2

def encode_image_to_base64(image_path: str) -> str:
    '''Lee una imagen de la ruta y la codifica en base64 para la API HTTP'''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def scale_and_encode_frame(img, image_size: list, logger) -> str:
    '''Redimensiona un frame de OpenCV y lo codifica en base64 para la API HTTP'''
    if img is None:
        logger.error("CV2 Error: La imagen proporcionada es None")
        return ""
        
    w_target, h_target = image_size[0], image_size[1]
    
    # Redimensionado a los parámetros
    img_resized = cv2.resize(img, (w_target, h_target), interpolation=cv2.INTER_AREA)
    
    # JPG en memoria con 85% de calidad y a base64
    _, buffer = cv2.imencode('.jpg', img_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode('utf-8')

def load_image_and_scale(image_path: str, image_size: list, logger) -> str:
    '''Lee una imagen de la ruta física y delega el redimensionado y codificación'''
    img = cv2.imread(image_path)

    if img is None:
        logger.error(f"CV2 Error: No se pudo leer la imagen en {image_path}")
        return ""
        
    return scale_and_encode_frame(img, image_size, logger)
        

def call_ollama_api(url: str, payload: dict) -> str:
    '''Realiza la petición POST a la API local de Ollama y devuelve el texto'''
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        # el nodo decide cómo imprimir el error
        raise RuntimeError(str(e))