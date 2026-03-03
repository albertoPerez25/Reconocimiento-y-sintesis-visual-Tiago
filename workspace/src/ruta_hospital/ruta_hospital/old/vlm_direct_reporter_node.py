#!/usr/bin/env python3
import os
import csv
import math
import json
import base64
import requests
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class VLMDirectReporterNode(Node):
    def __init__(self):
        super().__init__('vlm_direct_reporter_node')
        
        self.declare_parameter('csv_path', 'default_metadata.csv')
        self.declare_parameter('photos_dir', 'default_photos/')
        self.declare_parameter('semantic_map_path', 'default_map.json')
        self.declare_parameter('vlm_model', 'llava') 
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')

        self.csv_path = self.get_parameter('csv_path').get_parameter_value().string_value
        self.photos_dir = self.get_parameter('photos_dir').get_parameter_value().string_value
        self.semantic_map_path = self.get_parameter('semantic_map_path').get_parameter_value().string_value
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

        self.load_semantic_map()

        self.cb_group = ReentrantCallbackGroup()
        
        self.report_srv = self.create_service(
            Trigger, 
            'generate_patrol_report', 
            self.generate_report_callback, 
            callback_group=self.cb_group
        )
        
        self.get_logger().info(f"Nodo VLM directo {self.vlm_model} listo, se iniciará al llamar al servicio '/generate_patrol_report' ")

    def load_semantic_map(self):
        try:
            with open(self.semantic_map_path, 'r') as f:
                data = json.load(f)
                self.hospital_zones = data.get("HOSPITAL_ZONES", {})
                self.reception_zone = data.get("RECEPTION_ZONE", {})
        except Exception as e:
            self.get_logger().error(f"Error cargando mapa: {e}")
            self.hospital_zones = {}
            self.reception_zone = {}

    def get_nearest_room(self, x, y):
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

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_report_callback(self, request, response):
        if not os.path.isfile(self.csv_path):
            response.success = False
            response.message = "No hay datos de patrulla"
            return response

        base64_images = []
        metadata_context = "METADATOS DE LAS IMÁGENES PROPORCIONADAS (En orden):\n"
        img_counter = 1

        # Leer CSV y empaquetar todo
        with open(self.csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                img_path = os.path.join(self.photos_dir, row['filename'])
                if not os.path.isfile(img_path):
                    continue

                x, y = float(row['x']), float(row['y'])
                time_sec = int(row['timestamp_sec'])
                zona = self.get_zone_name(x, y)

                base64_images.append(self.encode_image(img_path))
                metadata_context += f"- Imagen {img_counter}: Tomada a los {time_sec}s en {zona}.\n"
                img_counter += 1

        if not base64_images:
            response.success = True
            response.message = "Ruta completada sin fotos tomadas"
            return response

        self.get_logger().info(f"Enviando {len(base64_images)} imágenes al modelo {self.vlm_model}. Esto puede tardar MUCHO...")

        prompt = f"""
        Eres la IA de seguridad de un robot patrulla en un hospital. 
        Te he adjuntado {len(base64_images)} imágenes tomadas durante tu última ronda.
        
        Aquí tienes el contexto espacial y temporal de cada imagen:
        {metadata_context}
        
        Tu tarea es analizar visualmente todas las imágenes adjuntas y redactar un único INFORME FINAL DE SEGURIDAD profesional para el responsable de planta.
        Ignora las imágenes donde el pasillo esté vacío. Céntrate solo en destacar las anomalías y riesgos (personas caídas, sentadas en el suelo, etc.) indicando en qué zona ocurrieron según los metadatos.
        
        INFORME DE SEGURIDAD:
        """

        payload = {
            "model": self.vlm_model,
            "prompt": prompt,
            "images": base64_images,
            "stream": False
        }

        try:
            api_response = requests.post(self.ollama_url, json=payload)
            api_response.raise_for_status()
            final_report = api_response.json()['response'].strip()
            
            self.get_logger().info(f"\n\n\tINFORME FINAL VLM\n{final_report}\n")
            response.success = True
            response.message = f"Informe generado por VLM: \n{final_report}"
            
        except Exception as e:
            error_msg = f"Error conectando con Ollama: {e}"
            self.get_logger().error(error_msg)
            response.success = False
            response.message = error_msg

        return response

def main(args=None):
    rclpy.init(args=args)
    node = VLMDirectReporterNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()