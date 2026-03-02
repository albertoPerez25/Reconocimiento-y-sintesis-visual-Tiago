import os
import csv
import json
import math
import glob
from abc import ABC, abstractmethod
from rclpy.node import Node
from std_srvs.srv import Trigger
from rclpy.callback_groups import ReentrantCallbackGroup

# Rutas por defecto
CSV_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/hospital_photos/metadata.csv"
PHOTOS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/hospital_photos/"
SEMANTIC_PATH_MAP = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/config/semantic_map.json"

class BaseReporterNode(Node, ABC):
    '''Clase abstracta para los nodos generadores de informes'''
    
    def __init__(self, node_name):
        super().__init__(node_name)
        
        # Parámetros comunes
        self.declare_parameter('csv_path', CSV_PATH)
        self.declare_parameter('photos_dir', PHOTOS_DIR)
        self.declare_parameter('semantic_map_path', SEMANTIC_PATH_MAP)

        self.csv_path = self.get_parameter('csv_path').get_parameter_value().string_value
        self.photos_dir = self.get_parameter('photos_dir').get_parameter_value().string_value
        self.semantic_map_path = self.get_parameter('semantic_map_path').get_parameter_value().string_value

        self.load_semantic_map()
        self.abort_processing = False 

        self.cb_group = ReentrantCallbackGroup()
        
        self.report_srv = self.create_service(
            Trigger, 
            'generate_patrol_report', 
            self.generate_report_callback, 
            callback_group=self.cb_group
        )

        self.clean_srv = self.create_service(
            Trigger,
            'clean_patrol_data',
            self.clean_data_callback,
            callback_group=self.cb_group
        )
        
        self.get_logger().info(f"Nodo de informe [{node_name}] listo. Se iniciará al llamar al servicio '/generate_patrol_report'")

    def load_semantic_map(self):
        '''Carga las zonas del hospital desde un archivo JSON externo'''
        try:
            with open(self.semantic_map_path, 'r') as f:
                data = json.load(f)
                self.hospital_zones = data.get("HOSPITAL_ZONES", {})
                self.reception_zone = data.get("RECEPTION_ZONE", {})
        except Exception as e:
            self.get_logger().error(f"Error cargando mapa: {e}")
            self.hospital_zones = {}
            self.reception_zone = {"esquina1": [0,0], "esquina2": [0,0]}

    def get_nearest_room(self, x, y):
        ''' Obtiene la sala más cercana a x,y '''
        nearest_room = "Desconocida"
        min_dist = float('inf')
        for room_name, coords in self.hospital_zones.items():
            cx = (coords["esquina1"][0] + coords["esquina2"][0]) / 2.0
            cy = (coords["esquina1"][1] + coords["esquina2"][1]) / 2.0
            dist = math.hypot(x - cx, y - cy)
            if dist < min_dist:
                min_dist = dist
                nearest_room = room_name
        return nearest_room

    def get_zone_name(self, x, y):
        ''' Obtiene el nombre de las coordenadas x,y '''
        for nombre_zona, coords in self.hospital_zones.items():
            x1, y1 = coords["esquina1"]
            x2, y2 = coords["esquina2"]
            if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
                return nombre_zona
                
        nearest_room = self.get_nearest_room(x, y)
        if self.reception_zone:
            rx1, ry1 = self.reception_zone["esquina1"]
            rx2, ry2 = self.reception_zone["esquina2"]
            if min(rx1, rx2) <= x <= max(rx1, rx2) and min(ry1, ry2) <= y <= max(ry1, ry2):
                return f"Recepción (cerca de {nearest_room})"
        return f"Pasillo (cerca de {nearest_room})"
    
    def get_images_grouped_by_zone(self):
        ''' Lee el CSV y devuelve un diccionario con las imágenes agrupadas por zona '''
        zone_groups = {}
        if not os.path.isfile(self.csv_path):
            self.get_logger().warn(f"No se encontró el CSV en {self.csv_path}")
            return zone_groups

        with open(self.csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                img_path = os.path.join(self.photos_dir, row['filename'])
                if not os.path.isfile(img_path):
                    continue

                x, y = float(row['x']), float(row['y'])
                zona = self.get_zone_name(x, y)
                
                if zona not in zone_groups:
                    zone_groups[zona] = []
                    
                zone_groups[zona].append({
                    'path': img_path,
                    'time': int(row['timestamp_sec'])
                })
                
        return zone_groups
    
    def clean_data_callback(self, request, response):
        '''Callback para abortar el proceso actual y limpiar la carpeta'''
        self.get_logger().info("Petición de limpieza, se parará el informe")
        self.abort_processing = True # Avisa a los bucles asíncronos de que paren
        self.clean_processed_files()
        
        response.success = True
        response.message = "Datos limpiados correctamente."
        return response

    def clean_processed_files(self):
        '''Borra las fotos y el CSV'''
        try:
            if os.path.isfile(self.csv_path):
                os.remove(self.csv_path)
            
            files = glob.glob(os.path.join(self.photos_dir, '*'))
            for file in files:
                if os.path.isfile(file) and (file.endswith('.jpg') or file.endswith('.png')):
                    os.remove(file)
                    
            self.get_logger().info("Carpeta de fotos reseteada")
        except Exception as e:
            self.get_logger().error(f"Error durante la limpieza: {e}")

    @abstractmethod
    async def generate_report_callback(self, request, response):
        '''Se ejecuta de manera asíncrona al llamar al servicio /generate_patrol_report'''
        pass