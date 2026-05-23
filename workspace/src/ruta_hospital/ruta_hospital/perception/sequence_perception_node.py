#!/usr/bin/env python3
import os
import rclpy
import json
import re # extraer el json
from ruta_hospital.perception.base_perception import BasePerceptionNode
from ruta_hospital.utils.commons.api_utils import encode_image_to_base64, call_ollama_api

DEFAULT_MODEL = 'moondream'
DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'

class SequencePerceptionNode(BasePerceptionNode):
    def __init__(self):
        super().__init__('sequence_perception_node')
        self.declare_parameter('vlm_model', DEFAULT_MODEL)
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    def process_image(self, image_paths_str, context):
        '''Recibe múltiples rutas de frames separadas por coma y los manda al VLM'''
        
        paths = image_paths_str.split(',')
        ok_paths = [r.strip() for r in paths if os.path.isfile(r.strip())]
        
        if not ok_paths:
            return json.dumps({"descripcion_vlm": "Error: No se encontraron imágenes válidas en la secuencia.", "alerta": False}, ensure_ascii=False)
        payload = self.get_payload(ok_paths, context)

        try:
            vlm_text = call_ollama_api(self.ollama_url, payload)
            match = re.search(r'\{.*\}', vlm_text, re.DOTALL)
            
            if match:
                json_str = match.group(0)
                json.loads(json_str) 
                return json_str
            else:
                self.get_logger().warn(f"El VLM de secuencia no devolvió un JSON válido: {vlm_text}")
                return json.dumps({"descripcion_vlm": "Error de formato VLM temporal", "alerta": False}, ensure_ascii=False)
                
        except json.JSONDecodeError:
            self.get_logger().warn(f"El JSON generado en la secuencia está malformado: {vlm_text}")
            return json.dumps({"descripcion_vlm": "Error de sintaxis JSON en secuencia", "alerta": False}, ensure_ascii=False)
        except Exception as e:
            self.get_logger().error(f"Error procesando secuencia: {e}")
            return json.dumps({"descripcion_vlm": f"Error en inferencia de secuencia: {e}", "alerta": False}, ensure_ascii=False)

    def get_payload(self, ok_paths, context):
        '''Crea el prompt y devuelve el payload completo para enviarle al modelo'''
        base64_frames = self.extract_key_frames(ok_paths, max_frames=40) 

        prompt = f"""
        Actúa como una IA analizadora de actividades en el hospital.
        Analiza esta secuencia temporal  en la zona {context.zone_name} (zona {context.zone_type}).
        Actividades esperadas aquí: {context.expected_activities}.
        
        INSTRUCCIONES CRÍTICAS (DE OBLIGADO CUMPLIMIENTO):
        1. Responde con un resumen telegráfico en MÁXIMO 15 PALABRAS.
        2. Formato estricto de log de seguridad (ej: 'Secuencia muestra 2 pacientes paseando').
        3. Si detectas una emergencia médica evidente (como alguien tirado en el suelo), incluye obligatoriamente la palabra 'URGENTE'.
        4. Devuelve un JSON con esta estructura exacta:
        {{
           "descripcion_vlm": "Tu resumen de max 15 palabras aquí",
           "alerta": true (solo si hay caídas o peligro inminente) o false
        }}
        """
        
        payload = {
            "model": self.vlm_model, 
            "prompt": prompt, 
            "images": base64_frames, 
            "stream": False,
            #"format": "json"
        }
        self.get_logger().info(f"Visualizando secuencia... ({len(base64_frames)} imágenes procesadas)")
        return payload

    def extract_key_frames(self, rutas, max_frames=40):
        '''Selecciona imágenes para no saturar la ventana de contexto'''
        total_images = len(rutas)
        if total_images <= max_frames:
            seleccionadas = rutas
        else:
            # Si hay 10 fotos y se quiere 4, selecciona la 0, 2, 5 y 7
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