import base64
import requests
import cv2

def encode_image_to_base64(image_path: str) -> str:
    '''Lee una imagen de la ruta y la codifica en base64 para la API HTTP'''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def load_image_and_scale(image_path: str, logger) -> str:
    '''Lee una imagen de la ruta y la codifica en base64 para la API HTTP'''
    img = cv2.imread(image_path)

    if img is None:
        logger.error(f"CV2 Error: No se pudo leer la imagen en {image_path}")
        base64_img = ""
    else:
        # Estrategia de conservación de memoria: Limitar lado máximo a 224px
        max_size = 224
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            # INTER_AREA es el algoritmo matemático óptimo para hacer sub-muestreo
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        
        # Codificamos a JPG en memoria con 85% de calidad y lo pasamos a base64
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        base64_img = base64.b64encode(buffer).decode('utf-8')
        
    return base64_img
        

def call_ollama_api(url: str, payload: dict) -> str:
    '''Realiza la petición POST a la API local de Ollama y devuelve el texto'''
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        # el nodo decide cómo imprimir el error
        raise RuntimeError(str(e))