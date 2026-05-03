#!/usr/bin/env python3
import rclpy
import os
import base64
from ruta_hospital.commons.api_utils import call_ollama_api
from ruta_hospital.perception.base_perception import BasePerceptionNode

# modelo con capacidades nativas de vídeo 
DEFAULT_MODEL = 'llava-video' 
DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'

class VideoPerceptionNode(BasePerceptionNode):
    '''Nodo que analiza un clip de vídeo usando un Video-VLM nativo'''
    def __init__(self, start_service=True):
        super().__init__('video_perception_node', start_service=start_service)
        
        self.declare_parameter('vlm_model', DEFAULT_MODEL)
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    def process_image(self, file_path, context): 
        '''Mantiene el nombre por herencia de BasePerceptionNode, pero recibe un .mp4'''
        
        # Leemos el archivo de vídeo directamente a base64
        try:
            with open(file_path, "rb") as video_file:
                base64_video = base64.b64encode(video_file.read()).decode('utf-8')
        except Exception as e:
            self.get_logger().error(f"Error leyendo el archivo de vídeo: {e}")
            return "Error de lectura del archivo de vídeo."

        prompt = f"""
        Eres un sistema de seguridad analizando un clip corto de vídeo del hospital.
        Observa la evolución temporal en el clip e indica BREVEMENTE QUÉ HACEN las personas.
        Contexto (Zona: {context.zone_name}, Tipo: {context.zone_type}).
        Actividades esperadas aquí: {context.expected_activities}.
        Si no ves personas en ninguna parte del clip, responde única y exactamente con "Despejado."
        """
        
        self.get_logger().debug(f"PROMPT AL VLM DE VÍDEO: {prompt}")
        
        # Pasamos el vídeo en el payload. 
        # NOTA: La sintaxis exacta ("images" o "videos") depende de la implementación específica 
        # del modelo en Ollama. Aquí usamos "images" asumiendo que la API lo unifica.
        payload = {
            "model": self.vlm_model, 
            "prompt": prompt, 
            "images": [base64_video], 
            "stream": False
        }
        
        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()
            
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people"]):
                return "Despejado."
                
            return vlm_text
        except Exception as e:
            self.get_logger().error(f"Error llamando a la API: {e}")
            return "Error de inferencia en el modelo de vídeo."

    def check_path(self, path):
        '''Verifica que el archivo exista y sea un vídeo MP4'''
        return os.path.isfile(path) and path.lower().endswith('.mp4')

def main(args=None):
    rclpy.init(args=args)
    try:
        rclpy.spin(VideoPerceptionNode())
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()