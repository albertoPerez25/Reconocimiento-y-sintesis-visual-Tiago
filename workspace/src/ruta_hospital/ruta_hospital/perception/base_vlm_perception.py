import os
import json
import time
from ruta_hospital.perception.base_perception import BasePerceptionNode, RagContext

DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'
DEFAULT_MODEL_WORD_LIMIT = 30
DEFAULT_IMAGE_SIZE = [640, 480]

class BaseVLMPerceptionNode(BasePerceptionNode):
    '''Clase intermedia para agrupar configuración y parámetros de Modelos de Lenguaje Visual'''
    def __init__(self, node_name, start_service=True, default_model='moondream'):
        super().__init__(node_name, start_service=start_service)
        
        self.declare_parameter('vlm_model', default_model)
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        self.declare_parameter('model_word_limit', DEFAULT_MODEL_WORD_LIMIT)
        self.declare_parameter('image_size', DEFAULT_IMAGE_SIZE)
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        self.model_word_limit = self.get_parameter('model_word_limit').get_parameter_value().integer_value
        self.image_size = list(self.get_parameter('image_size').get_parameter_value().integer_array_value)

    def analyze_callback(self, request, response):
        '''Se ejecuta cada vez que recibe una imagen por el servicio'''
        if not self.check_path(request.image_path):
            self.get_logger().error("No se encontró la imagen en la ruta especificada")
            response.report = "Error: No se encontró la imagen en la ruta especificada."
            return response 
                    
        self.get_logger().info(f"Analizando imagen: {os.path.basename(request.image_path)}...")
        
        context = RagContext(request)

        t_init = time.time()
        
        report_dict = self.process_image(request.image_path, context)
        
        t_process = round(time.time() - t_init, 3)
        self.perception_metrics["tiempos_procesado"].append(t_process)
        self.save_perception_metrics()

        response.report = json.dumps(report_dict, ensure_ascii=False) # evita que se rompan los acentos
        return response