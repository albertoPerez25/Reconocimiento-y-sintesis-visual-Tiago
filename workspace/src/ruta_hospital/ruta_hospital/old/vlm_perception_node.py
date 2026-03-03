#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import requests
import base64
import os

from hospital_interfaces.srv import AnalyzeActivity

class VLMPerceptionNode(Node):
    def __init__(self):
        super().__init__('vlm_perception_node')
        
        self.declare_parameter('vlm_model', 'llava')
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        
        # Servidor del servicio con el mismo nombre que el de YOLO para poder iniciarlo de la misma manera
        self.srv = self.create_service(
            AnalyzeActivity, 
            'analyze_image', 
            self.analyze_callback
        )
        
        self.get_logger().info(f"Nodo de Percepción VLM ({self.vlm_model}) listo y esperando imágenes.")

    def encode_image_to_base64(self, image_path):
        '''Lee la imagen y la codifica en base64 para la API HTTP'''
        
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_callback(self, request, response):
        '''Se ejecuta cada vez que el reportero pide analizar una imagen'''

        if not os.path.isfile(request.image_path):
            response.report = "Error: No se encontró la imagen en la ruta especificada."
            return response

        self.get_logger().info(f"Analizando imagen: {os.path.basename(request.image_path)}...")

        base64_image = self.encode_image_to_base64(request.image_path)

        # "Despejado" para que el LLM lo entienda
        prompt = """
        Eres una IA de seguridad analizando la cámara de un robot en un hospital.
        ¿Hay alguna persona en esta imagen? 
        - Si no hay nadie, responde EXACTAMENTE con la palabra: 'Despejado'.
        - Si hay personas, describe brevemente cuántas hay y su postura exacta (de pie, sentada en una silla, o caída en el suelo). Sé conciso.

        Adicionalmente, si encuentras algún suceso extraño o peligroso responde explicando dicho peligro, de manera concisa y clara.
        """

        payload = {
            "model": self.vlm_model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False
        }

        try:
            api_response = requests.post(self.ollama_url, json=payload)
            api_response.raise_for_status()
            
            # Respuesta textual de LLaVA
            vlm_text = api_response.json()['response'].strip()
            
            # Para mantener el estándar visual del log
            if "despejado" in vlm_text.lower():
                response.report = "Estado: Despejado. No se han detectado personas."
            else:
                response.report = f"Estado: {vlm_text}"
                
        except Exception as e:
            self.get_logger().error(f"Error conectando con el VLM: {e}")
            response.report = f"Error de inferencia VLM: {e}"

        return response

def main(args=None):
    rclpy.init(args=args)
    node = VLMPerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()