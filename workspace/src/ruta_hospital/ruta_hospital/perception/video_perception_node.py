#!/usr/bin/env python3
import rclpy
import os
import cv2
import base64
from ruta_hospital.utils.commons.api_utils import call_ollama_api
from ruta_hospital.perception.base_vlm_perception import BaseVLMPerceptionNode

# modelo con capacidades nativas de vídeo 
DEFAULT_MODEL = 'nemotron-3-nano:4b' 
DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'
DEFAULT_SAMPLED_FRAMES = 5

class VideoPerceptionNode(BaseVLMPerceptionNode):
    '''Nodo que analiza un clip de vídeo usando un VLM extrayendo frames clave'''
    def __init__(self, start_service=True):
        super().__init__('video_perception_node', 
                         start_service=start_service, 
                         default_model=DEFAULT_MODEL
                        )
        
        self.declare_parameter('sampled_frames', DEFAULT_SAMPLED_FRAMES)
        self.sampled_frames = self.get_parameter('sampled_frames').value

    def process_image(self, file_path, context): 
        '''Mantiene el nombre por herencia de BasePerceptionNode, pero recibe el video'''
        
        base64_images = self.extract_frames(file_path, self.sampled_frames)
        
        if not base64_images:
            return "Error extrayendo frames del clip de vídeo"

        prompt = f"""
        Analiza este clip de vídeo de la zona {context.zone_name} ({context.zone_type}).
        Actúa como una IA analizadora de actividades en el hospital. 
        Actividades esperadas aquí: {context.expected_activities}.
        
        INSTRUCCIONES:
        1. Describe la acción principal observada en MÁXIMO {self.word_limit} PALABRAS.
        2. Usa estilo de log directo (ej: 'Personal médico moviendo camilla').
        3. Si ves a alguien sufriendo una caída o tirado en el suelo, escribe la palabra clave 'URGENTE'.
        4. Responde con un JSON estricto:
        {{
           "descripcion_vlm": "Descripción compacta aquí",
           "alerta": true (solo si hay caídas o peligro inminente) o false
        }}
        """
        
        self.get_logger().debug(f"PROMPT AL VLM DE VÍDEO: {prompt}")
        
        # Se pasa el vídeo en el payload. 
    
        payload = {
            "model": self.vlm_model, 
            "prompt": prompt, 
            "images": base64_images,  
            "stream": False,
            "options": {
                "num_predict": self.word_limit * 2,
                "temperature": 0.1
            }
        }
        
        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()
            
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people"]):
                return "Despejado."
                
            return vlm_text
        except Exception as e:
            self.get_logger().error(f"Error llamando a la API: {e}")
            return "Error de inferencia en el modelo de vídeo"
        
    def extract_frames(self, video_path, num_frames):
        '''Lee el archivo de vídeo y devuelve una lista de imágenes en base64 equiespaciadas'''
        frames_b64 = []
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            self.get_logger().error(f"El vídeo {video_path} no tiene frames válidos.")
            return frames_b64
            
        # Calcular índices de los frames a extraer (equiespaciados)
        step = max(1, total_frames // num_frames)
        frame_indices = [min(i * step, total_frames - 1) for i in range(num_frames)]
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Comprimimos en JPEG para reducir el payload
                _, buffer = cv2.imencode('.jpg', frame)
                b64_str = base64.b64encode(buffer).decode('utf-8')
                frames_b64.append(b64_str)
                
        cap.release()
        return frames_b64

    def check_path(self, path):
        '''Verifica que el archivo exista y sea un vídeo avi'''
        return os.path.isfile(path) and path.lower().endswith('.avi')

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