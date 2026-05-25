#!/usr/bin/env python3
import rclpy
import os
import re
import json
from ruta_hospital.utils.commons.api_utils import encode_image_to_base64, call_ollama_api, load_image_and_scale
from ruta_hospital.perception.base_perception import BasePerceptionNode
from ruta_hospital.perception.base_vlm_perception import BaseVLMPerceptionNode

#DEFAULT_MODEL = 'moondream'
DEFAULT_MODEL = 'qwen2.5vl:3b'

class VLMPerceptionNode(BaseVLMPerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('vlm_perception_node', start_service=start_service, default_model=DEFAULT_MODEL)
        #self.declare_parameter('vlm_model', 'llava') # No tengo tanta VRAM

    def process_image(self, image_path, context):
        '''Interactua con el modelo y devuelve el reporte en forma de string'''
        payload = self.get_payload(image_path, context)
        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()
            alert = False
            
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people"]):
                descripcion = "Despejado"
            else:
                descripcion = vlm_text
                if any(term in vlm_text.lower() for term in ["caída","ayuda","urgente","alerta"]):
                    alert = True # Si dijo cualquier otra cosa, es que hay personas
            
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
        Act as an AI security analyzer for a hospital.
        You are inside a hospital in {context.zone_name}, which is a zone of type {context.zone_type}. 
        Here you may see people {context.expected_activities}.

        INSTRUCTIONS:
            - Briefly describe the activities the people in the image are doing.
            - If you see a life-threatening situation (such as a fall), write "URGENT".
            - If there are no people in the image, write "Despejado"
        """
        
        if tracking_hist:
            prompt += f"""
        YOLO TRACKER DATA:
        ---
            {tracking_hist}
        ---
        
        ANSWER IN SPANISH ONLY
        DESCRIPCIÓN:
        """
            #TODO: Pasarle también el número de personas detectadas por YOLO, id, posicion...
        else:
            prompt += f"""
        ANSWER IN SPANISH ONLY
        DESCRIPCIÓN:
        """
        
        ''' - ESTÁ PROHIBIDO copiar o repetir el contexto y datos del tracker. Úsalos solo para confirmar la acción.
            - Describe brevemente las actividades que hacen las personas en la imagen.
            - Sé telegráfico, responde en MÁXIMO {self.word_limit} PALABRAS. 
            - Si ves una situación de peligro vital (como una caída), escribe "URGENTE".'''
    
        self.get_logger().debug(f"PROMPT AL VLM: {prompt}")
        base64_img = load_image_and_scale(image_path, self.get_logger())
        payload = {"model": self.vlm_model, 
                   "prompt": prompt, 
                   "images": [base64_img], 
                   "stream": False,
                   "options": {
                        "num_predict": self.word_limit * 2,  # Evitar que alucine infinitamente
                        "temperature": 0.0,  # Hace las respuestas menos creativas y más predecibles
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