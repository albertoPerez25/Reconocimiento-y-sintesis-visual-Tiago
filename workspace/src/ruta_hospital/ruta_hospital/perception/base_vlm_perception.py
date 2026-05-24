from ruta_hospital.perception.base_perception import BasePerceptionNode

DEFAULT_OLLAMA_URL = 'http://localhost:11434/api/generate'
DEFAULT_WORD_LIMIT = 20

class BaseVLMPerceptionNode(BasePerceptionNode):
    '''Clase intermedia para agrupar configuración y parámetros de Modelos de Lenguaje Visual'''
    def __init__(self, node_name, start_service=True, default_model='moondream'):
        super().__init__(node_name, start_service=start_service)
        
        self.declare_parameter('vlm_model', default_model)
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        self.declare_parameter('word_limit', DEFAULT_WORD_LIMIT)
        
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        self.word_limit = self.get_parameter('word_limit').get_parameter_value().integer_value