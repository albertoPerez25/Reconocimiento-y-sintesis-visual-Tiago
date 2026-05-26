#!/usr/bin/env python3
import rclpy
import os

from ruta_hospital.utils.commons.api_utils import encode_image_to_base64, call_ollama_api, load_image_and_scale
from ruta_hospital.perception.base_perception import BasePerceptionNode
from ruta_hospital.perception.base_vlm_perception import BaseVLMPerceptionNode

#DEFAULT_MODEL = 'moondream'
#DEFAULT_MODEL = 'qwen2.5vl:3b'
DEFAULT_MODEL = 'gemma4:e2b'
DEFAULT_MODEL = 'qwen3.5:4b'

class VLMPerceptionNode(BaseVLMPerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('vlm_perception_node', start_service=start_service, default_model=DEFAULT_MODEL)
        #self.declare_parameter('vlm_model', 'llava') # No tengo tanta VRAM
        #self.ollama_url = self.ollama_url.replace("generate", "chat")

    def process_image(self, image_path, context):
        '''Interactua con el modelo y devuelve el reporte en forma de string'''
        payload = self.get_payload(image_path, context)
        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()

            alert = False
            
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people", "vacio", "sin personas", "no hay personas"]):
                descripcion = "Despejado" # Si dijo cualquier otra cosa, se asume que hay personas
            else:
                descripcion = vlm_text
                if any(term in vlm_text.lower() for term in ["urgente"]): #["caída","ayuda","urgente","alerta"]):
                    alert = True 
            
            json_str = {
                "descripcion_vlm": descripcion,
                "alerta": alert
            }

            self.get_logger().debug(f"RESPUESTA DEL VLM: {json_str}")
            return json_str
                
        except Exception as e:
            self.get_logger().error(f"Error conectando con el VLM: {e}")
            error_json = {
                "descripcion_vlm": f"Error de inferencia VLM: {e}", 
                "alerta": False
            }
            return error_json
        
    def get_payload(self, image_path, context):
        '''Crea el prompt y devuelve el payload completo para enviarle al modelo'''
        tracking_hist = getattr(context, 'tracking_history', '')
        prompt = f"""
Actúa como un analizador de seguridad con IA para un hospital.
Estás dentro de un hospital en {context.zone_name}, que es una zona de tipo {context.zone_type}. 
Aquí puedes ver personas {context.expected_activities}.

INSTRUCCIONES:
    - Describe brevemente las actividades que las personas en la imagen están realizando.
    - Si ves una situación que amenaza la vida (como una caída), escribe "URGENTE" y descríbela brevemente.
    - Si no hay personas en la imagen, escribe "Despejado"
"""
        
        if tracking_hist:
            prompt += f"""
DATOS DEL TRACKING YOLO:
---
    {tracking_hist}
---
        
RESPONDE SOLO EN ESPAÑOL
"""
            #TODO: Pasarle también el número de personas detectadas por YOLO, id, posicion...
        else:
            prompt += f"""
RESPONDE SOLO EN ESPAÑOL
"""
    
    
        self.get_logger().debug(f"PROMPT AL VLM: {prompt}")
        base64_img = load_image_and_scale(image_path, self.get_logger())
        payload = {
            "model": self.vlm_model, 
            "prompt": prompt, 
            "images": [base64_img],
            "think": False, 
            "stream": False,
            "keep_alive": "30s",
            "options": {
                "num_predict": self.word_limit * 2,
                "temperature": 0.01,  
                "num_ctx": 1024,
                #"num_gpu": 99  no es un parámetro estándar
                "stop": [
                    "Sujeto ID_", 
                    "Historial", 
                    "[DATOS", 
                    "Caja AZUL", 
                    "Caja VERDE"
                ]
            }   
        }

        return payload
    
    def check_path(self, path):
        '''Metodo para comprobar que el path es de una imagen que exista'''
        return os.path.isfile(path)
        #response.report = "Error: No se encontró la imagen en la ruta especificada."

def main(args=None):
    rclpy.init(args=args)
    try:
        rclpy.spin(VLMPerceptionNode())
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()