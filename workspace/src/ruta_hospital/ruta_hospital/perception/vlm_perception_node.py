#!/usr/bin/env python3
import rclpy
import os
import re
import json
from ruta_hospital.utils.commons.api_utils import encode_image_to_base64, call_ollama_api
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

    def process_image(self, image_path, context):
        '''Interactua con el modelo y devuelve el reporte en forma de string'''
        payload = self.get_payload(image_path, context)
        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()
            
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people"]):
                descripcion = "Despejado"
                alerta = False
            else:
                descripcion = vlm_text
                if ["caída","ayuda","urgente","alerta"] in vlm_text.lower:
                    alerta = True # Si dijo cualquier otra cosa, es que hay personas
            
            json_str = json.dumps({
                "descripcion_vlm": descripcion,
                "alerta": alerta
            }, ensure_ascii=False)

            self.get_logger().debug(f"RESPUESTA DEL VLM: {json_str}")
            return json_str
                
        except Exception as e:
            self.get_logger().error(f"Error conectando con el VLM: {e}")
            error_json = {
                "descripcion_vlm": f"Error de inferencia VLM: {e}", 
                "alerta": False
            }
            return json.dumps(error_json, ensure_ascii=False)
        
    def get_payload(self, image_path, context):
        '''Crea el prompt y devuelve el payload completo para enviarle al modelo'''
        tracking_hist = getattr(context, 'tracking_history', '')
        prompt = f"""
        Estás dentro de un hospital en {context.zone_name}, que es zona de tipo {context.zone_type}. 
        Aquí puede que veas gente {context.expected_activities}.
        """
        
        if tracking_hist:
            prompt += f"""
            [MEMORIA A CORTO PLAZO]:
            {tracking_hist}
            
            Instrucciones críticas (DE OBLIGADO CUMPLIMIENTO):
            - MÁXIMO 15 PALABRAS.
            - AGRUPA a las personas por su actividad. PROHIBIDO hacer listas individuales de sujetos o IDs.
            - Usa formato telegráfico de log de seguridad (ej: '3 pacientes sentados, 1 médico de pie').
            - Fíjate en las cajas dibujadas para confirmar las actividades basándote en la memoria.
            - Si ves una situación peligrosa para la vida (como una caída) que requiera enviar ayuda, añade al final "URGENTE".
            """
            #TODO: Pasarle también el número de personas detectadas por YOLO, id, posicion...
        else:
            prompt += """
            Describe BREVEMENTE QUÉ HACEN las personas de la imagen en MÁXIMO 15 PALABRAS. 
            Si no ves personas responde ÚNICA Y EXACTAMENTE con "Despejado."
            """
        
    
        self.get_logger().debug(f"PROMPT AL VLM: {prompt}")
        base64_img = encode_image_to_base64(image_path)
        payload = {"model": self.vlm_model, "prompt": prompt, "images": [base64_img], "stream": False}

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