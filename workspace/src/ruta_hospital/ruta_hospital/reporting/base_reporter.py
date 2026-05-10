import os
import csv
import json
import math
import datetime
from abc import ABC, abstractmethod
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from ament_index_python.packages import get_package_share_directory

from rclpy.action import ActionServer
from hospital_interfaces.action import GenerateReport
from workspace.src.ruta_hospital.ruta_hospital.utils.shared.semantic_map_utils import load_semantic_map, get_zone_name
from workspace.src.ruta_hospital.ruta_hospital.utils.commons.metrics_utils import save_metrics_to_file

# metricas
import datetime
import json

# Rutas por defecto
PKG_DIR = get_package_share_directory('ruta_hospital')

SEMANTIC_PATH_MAP = os.path.join(PKG_DIR, 'config', 'semantic_map.json')
METRICS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"
METADATA_PATH = os.path.join(PKG_DIR, 'config', 'hospital_metadata.json')
DEFAULT_MODEL = "llama3"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_WORD_LIMIT = 300
DEFAULT_SAVE_CONTEXT = False

class BaseReporterNode(Node, ABC):
    '''Clase abstracta para los nodos generadores de informes'''
    
    def __init__(self, node_name):
        super().__init__(node_name)
        
        # Parámetros comunes
        self.declare_parameter('semantic_map_path', SEMANTIC_PATH_MAP)
        self.declare_parameter('metrics_dir', METRICS_DIR)
        self.declare_parameter('metadata_path', METADATA_PATH)
        self.declare_parameter('llm_model', DEFAULT_MODEL)
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        self.declare_parameter('max_words', DEFAULT_WORD_LIMIT)
        self.declare_parameter('save_summary', DEFAULT_SAVE_CONTEXT = False)

        self.semantic_map_path = self.get_parameter('semantic_map_path').get_parameter_value().string_value
        self.metrics_dir = self.get_parameter('metrics_dir').get_parameter_value().string_value
        self.metadata_path = self.get_parameter('metadata_path').get_parameter_value().string_value
        self.llm_model = self.get_parameter('llm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        self.max_words = self.get_parameter('max_words').get_parameter_value().integer_value
        self.bool_save_summ = self.get_parameter('save_summary').get_parameter_value().bool_value

        self.hospital_zones, self.reception_zone = load_semantic_map(self.semantic_map_path, self.get_logger())
        self.hospital_metadata = self.load_hospital_metadata()
        self.latest_global_context = "" # para que el chatbot pueda obtener siempre el último contexto
        self.latest_final_summary = ""

        self.cb_group = ReentrantCallbackGroup()
        
        self.report_action_server = ActionServer(
            self,
            GenerateReport,
            'generate_patrol_report',
            execute_callback=self.execute_report_callback,
            callback_group=self.cb_group
        )

        self.current_metrics = self.init_metrics_dict()
        
        self.get_logger().info(f"Nodo de informe [{node_name}] listo. Se iniciará al llamar al servicio '/generate_patrol_report'")

    def init_metrics_dict(self):
        '''Inicializa o resetea el diccionario de métricas'''
        return {
            "fecha": str(datetime.datetime.now()),
            "modelo_reportero": self.get_name(),
            "total_imagenes_procesadas": 0,
            "zonas_despejadas": 0,
            "zonas_con_output": 0,
            "tiempo_percepcion_segundos": 0.0,
            "tiempo_llm_segundos": 0.0,
            "tiempo_total_segundos": 0.0,
            "caracteres_contexto_visual": 0,
            "caracteres_informe_final": 0
        }
    
    def get_zone_limits(self, zone_name):
        '''Busca los límites [x1, y1, x2, y2] de una zona por su nombre'''
        # habitaciones
        if zone_name in self.hospital_zones:
            c = self.hospital_zones[zone_name]
            return [c["esquina1"][0], c["esquina1"][1], c["esquina2"][0], c["esquina2"][1]]
        
        if "Recepción" in zone_name and self.reception_zone:
            c = self.reception_zone
            return [c["esquina1"][0], c["esquina1"][1], c["esquina2"][0], c["esquina2"][1]]
        
        # pasillos o zonas que no tengan una zona definida
        return [0.0, 0.0, 0.0, 0.0]
    
    def get_images_grouped_by_zone(self, photos_dir):
        ''' Lee el CSV y devuelve un diccionario con las imágenes agrupadas por zona '''
        zone_groups = {}
        csv_path = os.path.join(photos_dir, 'metadata.csv')

        if not os.path.isfile(csv_path):
            self.get_logger().warn(f"No se encontró el CSV en {csv_path}")
            return zone_groups

        with open(csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                img_path = os.path.join(photos_dir, row['filename'])
                if not os.path.isfile(img_path):
                    continue

                x, y = float(row['x']), float(row['y'])
                zone = get_zone_name((x,y), self.hospital_zones, self.reception_zone)
                
                if zone not in zone_groups:
                    zone_groups[zone] = []
                    
                zone_groups[zone].append({
                    'path': img_path,
                    'time': int(row['timestamp_sec'])
                })
                
        return zone_groups

    def save_metrics(self):
        '''Guarda las métricas usando la utilidad de commons'''
        save_metrics_to_file(self.metrics_dir, self.current_metrics, self.get_logger())
        
        self.current_metrics = self.init_metrics_dict() # para la siguiente vuelta empezar todo a 0

    def load_hospital_metadata(self):
        '''Carga las reglas y objetos comunes desde el JSON de metadatos (RAG)'''
        if not os.path.exists(self.metadata_path):
            self.get_logger().warn(f"No se encontró metadatos en {self.metadata_path}")
            return {}
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ZONAS", {})
        except Exception as e:
            self.get_logger().error(f"Error cargando metadatos: {e}")
            return {}
        
    def get_zone_metadata(self, zone_name):
        '''Busca metadatos de una zona '''
        if zone_name in self.hospital_metadata:
            return self.hospital_metadata[zone_name]
        
        # Búsqueda parcial para nombres compuestos como "Pasillo (cerca de X)"
        for key, data in self.hospital_metadata.items():
            if key in zone_name:
                return data
        return {}

    async def generate_report_callback(self, request, response):
        self.get_logger().error("ERROR: metodo deprecado \"generate_report_callback\" usado")
        exit(2)

    @abstractmethod
    async def execute_report_callback(self, goal_handle):
        '''Se ejecuta de manera asíncrona al llamar al servicio /generate_patrol_report'''
        pass