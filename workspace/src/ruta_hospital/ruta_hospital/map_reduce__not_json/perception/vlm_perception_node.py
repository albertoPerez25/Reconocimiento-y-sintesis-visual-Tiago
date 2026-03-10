#!/usr/bin/env python3
import rclpy
import os
from ruta_hospital.commons.api_utils import encode_image_to_base64, call_ollama_api
from ruta_hospital.perception.base_perception import BasePerceptionNode

class VLMPerceptionNode(BasePerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('vlm_perception_node',start_service=start_service)
        #self.declare_parameter('vlm_model', 'llava') # No tengo tanta VRAM
        self.declare_parameter('vlm_model', 'moondream')
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    def process_image(self, image_path: str) -> str:
        '''Interactua con el modelo y devuelve el reporte en forma de string'''
        prompt = """
        You are a security AI analyzing a robot's camera feed in a hospital.
        Is there anyone in this image?

        If there is no one, respond EXACTLY with the word: 'Despejado'.

        If there are people, briefly describe how many there are and their exact posture. Be concise.
        Additionally, if you find any strange or dangerous occurrence, respond by explaining said danger.
        You must analyze people activities and warn if someone is in need of help (like people who have fallen into the ground
        , running, yelling, fights...). Focus on anomalies, people who need help and life-threatening risks in the hospital 
        (fires, live wires, overturned chairs, objects obstructing the hallway/path...). 
        Do not make up data; report only what you are certain of BRIEFLY. Answer in SPANISH.
        """
        base64_img = encode_image_to_base64(image_path)
        payload = {"model": self.vlm_model, "prompt": prompt, "images": [base64_img], "stream": False}

        try:
            vlm_text = call_ollama_api(self.ollama_url, payload)
            
            if "despejado" in vlm_text.lower():
                return "Estado: Despejado. No se han detectado personas."
            
            return f"Estado: {vlm_text}"
                
        except Exception as e:
            self.get_logger().error(f"Error conectando con el VLM: {e}")
            return f"Error de inferencia VLM: {e}"
    
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