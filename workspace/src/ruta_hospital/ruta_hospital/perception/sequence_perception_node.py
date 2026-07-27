#!/usr/bin/env python3
import os
import rclpy
import json
import re # extraer el json
from ruta_hospital.perception.base_perception import BasePerceptionNode
from ruta_hospital.utils.commons.api_utils import load_image_and_scale, call_ollama_api
from ruta_hospital.perception.base_vlm_perception import BaseVLMPerceptionNode

DEFAULT_MODEL = 'moondream'

class SequencePerceptionNode(BaseVLMPerceptionNode):
    def __init__(self, start_service=True):
        super().__init__('sequence_perception_node', start_service=start_service, default_model=DEFAULT_MODEL)    
        self.perception_metrics["modelo_usado"] = self.vlm_model 

    def process_image(self, image_paths_str, context):
        '''Recibe múltiples rutas de frames separadas por coma y los manda al VLM'''
        
        paths = image_paths_str.split(',')
        ok_paths = [r.strip() for r in paths if os.path.isfile(r.strip())]
        
        if not ok_paths:
            return {"descripcion_vlm": "Error: No se encontraron imágenes válidas en la secuencia.", "alerta": False}
        payload = self.get_payload(ok_paths, context)

        try:
            vlm_text = call_ollama_api(self.ollama_url, payload).strip()
            
            alert = False
            if any(term in vlm_text.lower() for term in ["despejado", "empty", "no people", "vacio", "sin personas", "no hay personas"]):
                descripcion = "Despejado."
            else:
                descripcion = vlm_text
                # Evaluar alerta
                if "urgente" in vlm_text.lower():
                    alert = True
                    
            return {
                "descripcion_vlm": descripcion,
                "alerta": alert
            }
                
        except Exception as e:
            self.get_logger().error(f"Error procesando secuencia: {e}")
            return {"descripcion_vlm": f"Error en inferencia de secuencia: {e}", "alerta": False}

    def get_payload(self, ok_paths, context):
        '''Crea el prompt y devuelve el payload completo para enviarle al modelo'''
        base64_frames = self.extract_key_frames(ok_paths, max_frames=40) 

        prompt = f"""
        Actúa como un analizador telegráfico de actividades humanas para un hospital
        Estás dentro de un hospital en {context.zone_name}, que es una zona de tipo {context.zone_type}.
        Aquí puedes ver personas {context.expected_activities}

        INSTRUCCIONES:
            - Describe en un máximo de {self.model_word_limit} PALABRAS las actividades que las personas en esta secuencia temporal de imágenes están realizando
            - Dentro del límite incluye una MUY BREVE descripción de la persona o personas a las que te refieres
            - Si ves una situación que amenaza la vida (como una caída o alguien fumando), escribe "URGENTE" y descríbela brevemente
            - IGNORA a cualquier persona que se vea a lo lejos a través de una puerta o cristal. Describe ÚNICAMENTE lo que esté físicamente DENTRO de tu misma habitación
            - Si no hay personas en la secuencia, escribe "Despejado"

        EJEMPLO DE SALIDAS:
            - "Una mujer con sombrero sentada en una silla"
            - "Un niño con camiseta amarilla corriendo"
            - "Varios médicos de pie al lado de una camilla con una persona tumbada, posiblemente una operación a un paciente"
        """
        
        payload = {
            "model": self.vlm_model, 
            "prompt": prompt, 
            "images": base64_frames, 
            "stream": False,
            #"format": "json",
            "options": {
                "num_predict": self.model_word_limit * 2,
                "temperature": 0.0,  # Hace las respuestas menos creativas y más predecibles
                "seed": 42,
                "stop": [
                    "Sujeto ID_", 
                    "Historial", 
                    "[DATOS", 
                    "Caja AZUL", 
                    "Caja VERDE"
                ]
            }
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
            frames_b64.append(load_image_and_scale(ruta, self.image_size, self.get_logger()))
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
