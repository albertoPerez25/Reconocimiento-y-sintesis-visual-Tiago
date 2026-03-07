#!/usr/bin/env python3
import rclpy
import os
import re
import json
from ruta_hospital.commons.api_utils import encode_image_to_base64, call_ollama_api
from ruta_hospital.perception.base_perception import BasePerceptionNode

DEFAULT_MODEL = 'moondream'
DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'

class VLMPerceptionNode(BasePerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('vlm_perception_node',start_service=start_service)
        #self.declare_parameter('vlm_model', 'llava') # No tengo tanta VRAM
        self.declare_parameter('vlm_model', DEFAULT_MODEL)
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    def process_image(self, image_path):
        '''Interactua con el modelo y devuelve el reporte en forma de string'''

        payload = self.get_payload(self, image_path)

        try:
            vlm_text = call_ollama_api(self.ollama_url, payload)
            
            # Limpiamos el output por si el LLM mete texto extra antes o después del JSON
            match = re.search(r'\{.*\}', vlm_text, re.DOTALL)
            
            if match:
                json_str = match.group(0)
                # para comprobar que realmente es un JSON antes de enviarlo
                json.loads(json_str) 
                return json_str
            else:
                self.get_logger().warn(f"El VLM no devolvió un JSON válido: {vlm_text}")
                return '{"descripcion_vlm": "Error de formato VLM", "alerta": false}'
                
        except Exception as e:
            self.get_logger().error(f"Error conectando con el VLM: {e}")
            return f"Error de inferencia VLM: {e}"
        
    def get_payload(self,image_path):
        '''Crea el prompt y devuelve el payload completo para enviarle al modelo'''
        prompt = """
        You are a security AI. Analyze the image and output ONLY a valid JSON.
        - If the room is empty and safe, the description must be exactly: "Despejado".
        - If there are people or danger, or someone has fallon on the ground, describe them briefly in SPANISH.
        - Set "alerta" to true ONLY if there is an emergency or danger.

        Example of expected output:
        {
          "descripcion_vlm": "Despejado",
          "alerta": false
        }
        """
        base64_img = encode_image_to_base64(image_path)
        payload = {"model": self.vlm_model, "prompt": prompt, "images": [base64_img], "stream": False, "format": "json"}
    
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