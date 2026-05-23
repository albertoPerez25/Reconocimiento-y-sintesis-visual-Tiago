import base64
import requests

def encode_image_to_base64(image_path: str) -> str:
    '''Lee una imagen de la ruta y la codifica en base64 para la API HTTP'''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_ollama_api(url: str, payload: dict) -> str:
    '''Realiza la petición POST a la API local de Ollama y devuelve el texto'''
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        # el nodo decide cómo imprimir el error
        raise RuntimeError(str(e))