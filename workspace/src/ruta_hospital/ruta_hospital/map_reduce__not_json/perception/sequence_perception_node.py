#!/usr/bin/env python3
import os
import rclpy
from ruta_hospital.perception.base_perception import BasePerceptionNode
from workspace.src.ruta_hospital.ruta_hospital.utils.commons.api_utils import encode_image_to_base64, call_ollama_api

class SequencePerceptionNode(BasePerceptionNode):
    def __init__(self):
        super().__init__('sequence_perception_node')
        self.declare_parameter('vlm_model', 'moondream')
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    def process_image(self, image_paths_str: str) -> str:
        '''Recibe múltiples rutas de frames separadas por coma y los manda al VLM'''
        
        rutas = image_paths_str.split(',')
        rutas_validas = [r for r in rutas if os.path.isfile(r)]
        
        if not rutas_validas:
            return "Error: No se encontraron imágenes válidas en la secuencia."

        # Codificación Base64
        base64_frames = self.extract_key_frames(rutas_validas, max_frames=40)

        prompt = """
        Eres una IA de seguridad analizando una SECUENCIA TEMPORAL de una cámara de vigilancia. 
        Te he adjuntado fotogramas clave en orden cronológico.
        Analiza la secuencia visual de manera global:
        - Si no hay nadie y todo está en orden, responde EXACTAMENTE con: 'Despejado'.
        - Si hay personas, describe qué están haciendo a lo largo de la secuencia. Atento a peleas, personas caidas en el suelo o emergencias.
        Sé muy directo y conciso. No analices las imágenes por separado, únelas en una sola acción temporal.
        """

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
        Sé muy directo y conciso. No analices las imágenes por separado, únelas en una sola acción temporal.
        """
        
        payload = {"model": self.vlm_model, "prompt": prompt, "images": base64_frames, "stream": False}

        try:
            self.get_logger().info(f"Visualizando secuencia... ({len(base64_frames)} imágenes procesadas)")
            vlm_text = call_ollama_api(self.ollama_url, payload)
            
            if "despejado" in vlm_text.lower()[:15]:
                return "Despejado. Zona sin actividad."
            
            return f"{vlm_text.strip()}"
                
        except Exception as e:
            self.get_logger().error(f"Error procesando secuencia: {e}")
            return f"Error en inferencia de secuencia: {e}"

    def extract_key_frames(self, rutas, max_frames=20):
        '''Selecciona imágenes para no saturar la ventana de contexto'''
        total_images = len(rutas)
        if total_images <= max_frames:
            seleccionadas = rutas
        else:
            # Si hay 10 fotos y se quiere 4, selecciona la 0, 2, 5 y 7.
            step = total_images / max_frames
            seleccionadas = [rutas[int(i * step)] for i in range(max_frames)]

        frames_b64 = []
        for ruta in seleccionadas:
            frames_b64.append(encode_image_to_base64(ruta))
        return frames_b64

    def check_path(self, path):
        '''Verifica que la cadena tenga al menos una ruta de imagen válida'''
        if not path:
            return False
            
        rutas = path.split(',')
        return any(os.path.isfile(r.strip()) for r in rutas) # con que uno sea valido ya sirve

def main(args=None):
    rclpy.init(args=args)
    node = SequencePerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()