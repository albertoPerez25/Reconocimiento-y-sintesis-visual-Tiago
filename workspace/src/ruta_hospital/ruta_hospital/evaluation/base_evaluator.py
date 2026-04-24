from rclpy.node import Node
from ruta_hospital.evaluation.utils.ragas_evaluator import OllamaParams, EvaluatorRunParams

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_EVALUATOR_LLM_MODEL = "llama3"
DEFAULT_EVALUATOR_EMBED_MODEL = "nomic-embed-text"

DEFAULT_SYSTEM_WORKERS = 4
DEFAULT_SYSTEM_TIMEOUT = 1420
DEFAULT_PERCEPTOR_WORKERS = DEFAULT_SYSTEM_WORKERS
DEFAULT_PERCEPTOR_TIMEOUT = DEFAULT_SYSTEM_TIMEOUT

DEFAULT_EVALUATION_NAME = "generic"

class BaseEvaluatorNode(Node):
    '''Clase padre que gestiona la configuración común de IA y Ragas para los evaluadores'''
    def __init__(self, node_name):
        super().__init__(node_name)

        # Declaración de parámetros
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        self.declare_parameter('evaluator_llm_model', DEFAULT_EVALUATOR_LLM_MODEL)
        self.declare_parameter('evaluator_embed_model', DEFAULT_EVALUATOR_EMBED_MODEL)
        self.declare_parameter('system_workers', DEFAULT_SYSTEM_WORKERS)
        self.declare_parameter('perceptor_workers', DEFAULT_PERCEPTOR_WORKERS)
        self.declare_parameter('system_timeout', DEFAULT_SYSTEM_TIMEOUT)
        self.declare_parameter('perceptor_timeout', DEFAULT_PERCEPTOR_TIMEOUT)
        self.declare_parameter('evaluation_name', DEFAULT_EVALUATION_NAME)

        # Extracción de valores
        ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        llm_model = self.get_parameter('evaluator_llm_model').get_parameter_value().string_value
        embed_model = self.get_parameter('evaluator_embed_model').get_parameter_value().string_value

        sys_workers = self.get_parameter('system_workers').get_parameter_value().integer_value
        perc_workers = self.get_parameter('perceptor_workers').get_parameter_value().integer_value
        sys_timeout = self.get_parameter('system_timeout').get_parameter_value().integer_value
        perc_timeout = self.get_parameter('perceptor_timeout').get_parameter_value().integer_value

        self.evaluation_name = self.get_parameter('evaluation_name').get_parameter_value().string_value

        # Configuración para RAGAS
        self.ollama_params = OllamaParams(
            ollama_url=ollama_url, 
            evaluator_llm_model=llm_model, 
            evaluator_embed_model=embed_model
        )
        self.run_params = EvaluatorRunParams(
            system_workers=sys_workers, 
            system_timeout=sys_timeout, 
            perceptor_workers=perc_workers, 
            perceptors_timeout=perc_timeout
        )