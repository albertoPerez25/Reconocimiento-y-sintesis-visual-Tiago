from abc import ABC, abstractmethod
from rclpy.node import Node
from hospital_interfaces.srv import AnalyzeActivity
import datetime
from ruta_hospital.utils.commons.metrics_utils import save_metrics_to_file

DEFAULT_METRICS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/"

class RagContext:
    def __init__(self,request):
        self.zone_name = getattr(request, 'zone_name', 'Desconocida') # por si en alguna llamada faltan datos
        self.time_str = getattr(request, 'time', 'Desconocida')
        self.expected_activities = getattr(request, 'expected_activities', 'No especificadas')
        self.zone_type = getattr(request, 'zone_type', 'Desconocida')

class BasePerceptionNode(Node, ABC):
    '''Clase abstracta para los nodos de percepción visual'''
    def __init__(self, node_name, start_service=True):
        super().__init__(node_name)

        self.declare_parameter('metrics_dir', DEFAULT_METRICS_DIR)
        self.metrics_dir = self.get_parameter('metrics_dir').get_parameter_value().string_value
        
        self.perception_metrics = {
            "fecha": str(datetime.datetime.now()),
            "nodo_ejecutor": self.get_name(),
            "modelo_usado": "unknown", # Se sobrescribirá en los nodos hijos
            "modelos_acoplados": {},   # Exclusivo para el nodo híbrido
            "tiempos_procesado": []    # Tiempos por cada frame/inferencia
        }
        
        # Servidor del servicio que recibe imágenes y devuelve un reporte
        # de posiciones
        if start_service:
            self.srv = self.create_service(
                AnalyzeActivity, 
                'analyze_image', 
                self.analyze_callback
            )
            self.get_logger().info(f"Servidor de percepción [{node_name}] listo y esperando imágenes.")
        else:
            self.get_logger().info(f"Lógica de [{node_name}] cargada internamente como módulo.")

    def save_perception_metrics(self):
        '''Guarda las métricas de rendimiento en un archivo JSON específico para este nodo'''
        filename = f"{self.get_name()}_metrics.json"
        save_metrics_to_file(self.metrics_dir, self.perception_metrics, self.get_logger(), filename)

    @abstractmethod
    def analyze_callback(self, request, response):
        '''Se ejecuta cada vez que recibe una imagen por el servicio'''
        pass

    @abstractmethod
    def process_image(self, image_path, context):
        '''Método que implementa cada nodo hijo. Devuelve el reporte en forma de string '''
        pass

    @abstractmethod
    def check_path(self, path):
        '''Metodo para comprobar que el tipo de path es el adecuado para el tipo de perceptor'''
        pass