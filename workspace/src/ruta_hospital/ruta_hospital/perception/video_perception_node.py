#!/usr/bin/env python3
import rclpy
import os
import cv2
import base64
from ruta_hospital.utils.commons.api_utils import call_ollama_api
from ruta_hospital.perception.base_vlm_perception import BaseVLMPerceptionNode

# modelo con capacidades nativas de vídeo 
#DEFAULT_MODEL = 'nemotron-3-nano:4b' 
DEFAULT_MODEL = 'qwen3.5:4b'
DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'
DEFAULT_SAMPLED_FRAMES = 5
DEFAULT_SAVE_FRAMES = False
DEFAULT_FRAMES_DIR = '/tmp/video_perception_debug/'

class VideoPerceptionNode(BaseVLMPerceptionNode):
    '''Nodo que analiza un clip de vídeo usando un VLM extrayendo frames clave'''
    def __init__(self, start_service=True):
        super().__init__('video_perception_node', 
                         start_service=start_service, 
                         default_model=DEFAULT_MODEL
                        )
        
        self.declare_parameter('sampled_frames', DEFAULT_SAMPLED_FRAMES)
        self.declare_parameter('save_sampled_frames', DEFAULT_SAVE_FRAMES)
        self.declare_parameter('sampled_frames_dir', DEFAULT_FRAMES_DIR)

        self.sampled_frames = self.get_parameter('sampled_frames').value
        self.save_sampled_frames = self.get_parameter('save_sampled_frames').value
        self.sampled_frames_dir = self.get_parameter('sampled_frames_dir').value

        # Crear el directorio de debug si se solicita
        if self.save_sampled_frames:
            os.makedirs(self.sampled_frames_dir, exist_ok=True)
            self.get_logger().info(f"Los frames se guardarán en: {self.sampled_frames_dir}")

        self.perception_metrics["modelo_usado"] = self.vlm_model

    def process_image(self, file_path, context): # TODO: Dividir
        '''Mantiene el nombre por herencia de BasePerceptionNode, pero recibe el video'''
        
        base64_images = self.extract_frames(file_path, self.sampled_frames)
        
        if not base64_images:
            return "Error extrayendo frames del clip de vídeo"
        
        tracking_hist = getattr(context, 'tracking_history', '')

        prompt = f"""
Actúa como un analizador telegráfico de actividades humanas para un hospital
Estás dentro de un hospital en {context.zone_name}, que es una zona de tipo {context.zone_type}.
Aquí puedes ver personas {context.expected_activities}

INSTRUCCIONES:
    - Describe en un máximo de {self.word_limit} PALABRAS las actividades que las personas en el clip de vídeo están realizando
    - Dentro del límite incluye una MUY BREVE descripción de la persona o personas a las que te refieres
    - Si ves una situación que amenaza la vida (como una caída o alguien fumando), escribe "URGENTE" y descríbela brevemente
    - IGNORA a cualquier persona que se vea a lo lejos a través de una puerta o cristal. Describe ÚNICAMENTE lo que esté físicamente DENTRO de tu misma habitación
    - Si no hay personas en el clip de vídeo, escribe "Despejado"

EJEMPLO DE SALIDAS:
    - "Una mujer con sombrero sentada en una silla"
    - "Un niño con camiseta amarilla corriendo"
    - "Varios médicos de pie al lado de una camilla con una persona tumbada, posiblemente una operación a un paciente"
"""
        
        if tracking_hist:
            prompt += f"""
DATOS DE TRACKING YOLO:
---
    {tracking_hist}
---
        
RESPONDE SOLO EN ESPAÑOL
"""
        else:
            prompt += f"""
RESPONDE SOLO EN ESPAÑOL
"""
        
        self.get_logger().debug(f"PROMPT AL VLM DE VÍDEO: {prompt}")
        
        # Se pasa el vídeo en el payload. 
    
        payload = {
            "model": self.vlm_model, 
            "prompt": prompt, 
            "images": base64_images,  
            "think": False,
            "stream": False,
            "keep_alive": "30s",
            "options": {
                "num_predict": self.word_limit * 2,
                "temperature": 0.01,  # respuestas menos creativas y mas predecibles
                "num_ctx": 1024,
                "stop": [
                    "Sujeto ID_", 
                    "Historial", 
                    "[DATOS", 
                    "Caja AZUL", 
                    "Caja VERDE"
                ]
            }
        }
        
        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()
            
            alert = False
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people"]):
                descripcion = "Despejado."
            else:
                descripcion = vlm_text
                # Evaluar alerta de seguridad según la instrucción del prompt
                if "urgente" in vlm_text.lower():
                    alert = True
            self.get_logger().error(f"Output video: {descripcion}")
                    
            return {
                "descripcion_vlm": descripcion,
                "alerta": alert
            }
            
        except Exception as e:
            self.get_logger().error(f"Error llamando a la API: {e}")
            return {
                "descripcion_vlm": f"Error de inferencia VLM de vídeo: {e}",
                "alerta": False
            }
        
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
                # Escalar imagen
                frame = cv2.resize(frame, (640, 480)) # TODO: Cambiarlo a la funcion estándar de utilidades
                
                # guardado de frames
                if self.save_sampled_frames:
                    base_name = os.path.basename(video_path).split('.')[0]
                    debug_path = os.path.join(self.sampled_frames_dir, f"{base_name}_frame_{idx}.jpg")
                    cv2.imwrite(debug_path, frame)
                    self.get_logger().debug(f"Frame {idx} guardado en: {debug_path}")

                # COmprimir en JPEG para reducir el payload
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                b64_str = base64.b64encode(buffer.tobytes()).decode('utf-8')
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