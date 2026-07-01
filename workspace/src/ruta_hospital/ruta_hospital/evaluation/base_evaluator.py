from abc import ABC, abstractmethod
import json
import datetime
import os
from rclpy.node import Node
from rclpy.action import CancelResponse, GoalResponse
from hospital_interfaces.action import GenerateReport
from ruta_hospital.evaluation.utils.ragas_evaluator import OllamaParams, EvaluatorRunParams
from ruta_hospital.utils.commons.metrics_utils import save_metrics_to_file
import logging

# --- ACTIVAR DEBUG PROFUNDO DE RAGAS Y LANGCHAIN ---
logging.getLogger("ragas").setLevel(logging.DEBUG)
logging.getLogger("langchain").setLevel(logging.DEBUG)

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_EVALUATOR_LLM_MODEL = "llama3.1" #falla en fix_output_format en las preguntas summary, por dar un contexto enorme
#DEFAULT_EVALUATOR_LLM_MODEL = 'qwen3.5:4b'
DEFAULT_EVALUATOR_EMBED_MODEL = "nomic-embed-text"

DEFAULT_SYSTEM_WORKERS = 1
DEFAULT_SYSTEM_TIMEOUT = 1420
DEFAULT_PERCEPTOR_WORKERS = DEFAULT_SYSTEM_WORKERS
DEFAULT_PERCEPTOR_TIMEOUT = DEFAULT_SYSTEM_TIMEOUT

DEFAULT_EVALUATION_NAME = "generic"
DEFAULT_EVALUATION_MODE = "full" # "generate_only", "full", "evaluate_only"

DEFAULT_ANSWERS_FILE = "/tmp/ragas_intermediate_answers.json"
DEFAULT_METRICS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/"

DEFAULT_WORD_LIMIT = 300
DEFAULT_MAX_STORED_ROUNDS = 5

class InferencePipelineError(Exception):
    """Excepción cuando falla un paso en el pipeline de inferencia."""
    pass

class BaseEvaluatorNode(Node, ABC):
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
        self.declare_parameter('evaluation_mode', DEFAULT_EVALUATION_MODE)
        self.declare_parameter('answers_file', DEFAULT_ANSWERS_FILE)
        self.declare_parameter('metrics_dir', DEFAULT_METRICS_DIR)
        self.declare_parameter('max_words', DEFAULT_WORD_LIMIT)
        self.declare_parameter('max_stored_rounds', DEFAULT_MAX_STORED_ROUNDS)

        # Extracción de valores
        ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        llm_model = self.get_parameter('evaluator_llm_model').get_parameter_value().string_value
        embed_model = self.get_parameter('evaluator_embed_model').get_parameter_value().string_value

        sys_workers = self.get_parameter('system_workers').get_parameter_value().integer_value
        perc_workers = self.get_parameter('perceptor_workers').get_parameter_value().integer_value
        sys_timeout = self.get_parameter('system_timeout').get_parameter_value().integer_value
        perc_timeout = self.get_parameter('perceptor_timeout').get_parameter_value().integer_value

        self.evaluation_name = self.get_parameter('evaluation_name').get_parameter_value().string_value
        self.evaluation_mode = self.get_parameter('evaluation_mode').get_parameter_value().string_value
        self.answers_file = self.get_parameter('answers_file').get_parameter_value().string_value
        self.metrics_dir = self.get_parameter('metrics_dir').get_parameter_value().string_value
        max_words = self.get_parameter('max_words').get_parameter_value().integer_value
        max_stored_rounds = self.get_parameter('max_stored_rounds').get_parameter_value().integer_value


        self.current_metrics = self.init_metrics_dict()

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
            perceptors_timeout=perc_timeout,
            max_words=max_words,
            max_stored_rounds=max_stored_rounds
        )

    def init_metrics_dict(self):
        '''Inicializa o resetea el diccionario de métricas de forma genérica'''
        return {
            "fecha": str(datetime.datetime.now()),
            "nodo_ejecutor": self.get_name(),
            "evaluacion_nombre": self.evaluation_name,
            "total_imagenes_procesadas": 0,
            "tiempo_percepcion_segundos": 0.0,
            "tiempo_llm_segundos": 0.0,
            "tiempo_inferencia_total_segundos": 0.0, # Tiempo de inferencia (sin Ragas)
            "tiempo_ragas_evaluacion_segundos": 0.0, # Tiempo solo de Ragas
            "tiempo_total_ejecucion_segundos": 0.0,  # Media/Suma del sistema (Inferencia + Ragas)
            "caracteres_contexto_visual": 0,         
            "caracteres_informe_final": 0            
        }

    def save_metrics(self, custom_metrics_dict=None):
        '''Wrapper para usar la utilidad de commons y limpiar las variables'''
        data_to_save = custom_metrics_dict if custom_metrics_dict else self.current_metrics
        save_metrics_to_file(self.metrics_dir, data_to_save, self.get_logger(), 'comparativa_evaluadores.json')
        self.current_metrics = self.init_metrics_dict()

    def save_intermediate_answers(self, data_dict):
        '''Guarda los diccionarios de respuestas en un JSON persistente'''
        try:
            with open(self.answers_file, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)
            self.get_logger().info(f"Respuestas intermedias guardadas en {self.answers_file}")
            return True
        except Exception as e:
            self.get_logger().error(f"Error guardando respuestas intermedias: {e}")
            return False

    def load_intermediate_answers(self):
        '''Carga los diccionarios de respuestas desde un JSON persistente'''
        if not os.path.exists(self.answers_file):
            self.get_logger().error(f"Archivo de respuestas no encontrado: {self.answers_file}")
            return None
        try:
            with open(self.answers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.get_logger().info(f"Respuestas cargadas desde {self.answers_file}")
                return data
        except Exception as e:
            self.get_logger().error(f"Error cargando respuestas intermedias: {e}")
            return None
        
    def goal_callback(self, goal_request):
        '''Acepta la petición de evaluación al instante de forma genérica'''
        self.get_logger().info("Recibida petición de evaluación a través de Acción.")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        '''Permite cancelar la evaluación de forma genérica si se solicita'''
        self.get_logger().info("Petición de cancelación de evaluación recibida.")
        return CancelResponse.ACCEPT
        
    @abstractmethod
    async def evaluate_callback(self, goal_handle):
        pass