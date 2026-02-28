#!/usr/bin/env python3
import rclpy
from ruta_hospital.commons.api_utils import encode_image_to_base64, call_ollama_api
from ruta_hospital.perception.base_perception import BasePerceptionNode

class VLMPerceptionNode(BasePerceptionNode):
    def __init__(self):
        super().__init__('vlm_perception_node')
        #self.declare_parameter('vlm_model', 'llava') # No tengo tanta VRAM
        self.declare_parameter('vlm_model', 'moondream')
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    def process_image(self, image_path: str) -> str:
        '''Interactua con el modelo y devuelve el reporte en forma de string'''
        prompt = """
        Eres una IA de seguridad analizando la cámara de un robot en un hospital.
        ¿Hay alguna persona en esta imagen? 
        - Si no hay nadie, responde EXACTAMENTE con la palabra: 'Despejado'.
        - Si hay personas, describe brevemente cuántas hay y su postura exacta. Sé conciso.
        Adicionalmente, si encuentras algún suceso extraño o peligroso responde explicando dicho peligro.
        Céntrate en anomalías y riesgos para la vida en el hospital (incendios, cables con corriente, sillas tiradas, 
        objetos obstruyendo el pasillo/camino...). No te inventes datos, di unicamente de lo que este seguro.
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