#!/usr/bin/env python3
import os
import csv
import math
import requests
import rclpy
import json
from rclpy.node import Node
from std_srvs.srv import Trigger
from hospital_interfaces.srv import AnalyzeActivity

from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

# Rutas por defecto
CSV_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/hospital_photos/metadata.csv"
PHOTOS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/hospital_photos/"
SEMANTIC_PATH_MAP = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/config/semantic_map.json"

class LLMReporterNode(Node):
    def __init__(self):
        super().__init__('llm_reporter_node')

        # Rutas como parámetros configurados en un .yaml en /config/reporter_config.yaml
        self.declare_parameter('csv_path', CSV_PATH)
        self.declare_parameter('photos_dir', PHOTOS_DIR)
        self.declare_parameter('semantic_map_path', SEMANTIC_PATH_MAP)

        self.csv_path = self.get_parameter('csv_path').get_parameter_value().string_value
        self.photos_dir = self.get_parameter('photos_dir').get_parameter_value().string_value
        self.semantic_map_path = self.get_parameter('semantic_map_path').get_parameter_value().string_value

        self.load_semantic_map()
        
        # para permitir el multihilo y así evitar deadlocks
        self.cb_group = ReentrantCallbackGroup()
        
        # Para pedir al nodo de yolo que procese una imagen
        self.vision_cli = self.create_client(
            AnalyzeActivity, 
            'analyze_image', 
            callback_group=self.cb_group
        )
        
        # Para que otro nodo inicie la generación del informe
        self.report_srv = self.create_service(
            Trigger, 
            'generate_patrol_report', 
            self.generate_report_callback, 
            callback_group=self.cb_group
        )
        
        self.get_logger().info("Nodo de informe LLM listo. Se iniciará al llamar al servicio '/generate_patrol_report'")

    def load_semantic_map(self):
        '''Carga las zonas del hospital desde un archivo JSON externo'''
        try:
            with open(self.semantic_map_path, 'r') as f:
                data = json.load(f)
                self.hospital_zones = data.get("HOSPITAL_ZONES", {})
                self.reception_zone = data.get("RECEPTION_ZONE", {})
            self.get_logger().info(f"Mapa semántico cargado correctamente desde {self.semantic_map_path}")
        except Exception as e:
            self.get_logger().error(f"Error al cargar el mapa semántico: {e}")

            # Valores por defecto
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
        
        # Validación extra por si falla la carga del JSON
        if self.reception_zone:
            rx1, ry1 = self.reception_zone["esquina1"]
            rx2, ry2 = self.reception_zone["esquina2"]
            if min(rx1, rx2) <= x <= max(rx1, rx2) and min(ry1, ry2) <= y <= max(ry1, ry2):
                return f"Recepción (cerca de {nearest_room})"
            
        return f"Pasillo (cerca de {nearest_room})"

    async def generate_report_callback(self, request, response):
        '''Se ejecuta de manera asíncrona al llamar al servicio /generate_patrol_report'''

        self.get_logger().info("Iniciada generación del informe")
        
        if not self.vision_cli.wait_for_service(timeout_sec=5.0):
            response.success = False
            response.message = "Error: El nodo de percepción visual no está activo"
            return response
        
        context_text = await self.get_context_text_async()
        
        if "Todo en orden" not in context_text:
            self.get_logger().info("Generando informe con Llama-3...")
            final_report = self.call_ollama(context_text)
            self.get_logger().info(f"\n\n\tINFORME FINAL\n{final_report}\n")
        else:
            final_report = "Ruta completada sin incidencias"
            self.get_logger().info(final_report)

        response.success = True
        response.message = f"Informe generado correctamente: \n{final_report}"
        return response

    async def get_activity_by_zone(self):
        ''' Devuelve la actividad de las personas detectadas por zonas'''

        activity_by_zone = {}
        empty_count = 0

        with open(self.csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                img_path = os.path.join(self.photos_dir, row['filename'])
                if not os.path.isfile(img_path):
                    continue

                x, y = float(row['x']), float(row['y'])
                time_sec = int(row['timestamp_sec'])

                # Llamada asíncrona al nodo de percepción de poses YOLO
                req = AnalyzeActivity.Request()
                req.image_path = img_path
                future_response = self.vision_cli.call_async(req)
                result = await future_response
                
                yolo_report = result.report
                
                if "Despejado" in yolo_report:
                    empty_count += 1
                    continue
                
                nombre_zona = self.get_zone_name(x, y)
                if nombre_zona not in activity_by_zone:
                    activity_by_zone[nombre_zona] = []
                    
                activity_by_zone[nombre_zona].append({
                    'time': time_sec,
                    'filename': row['filename'],
                    'report': yolo_report.strip()
                })

        return activity_by_zone,empty_count

    async def get_context_text_async(self):
        ''' Itera sobre las fotos, llama al servicio visual y cruza con las zonas
            Asíncrono para evitar el congelamiento del hilo del nodo, 
            lo que provoca un deadlock al no consumir los datos de entrada
        '''

        if not os.path.isfile(self.csv_path):
            return f"No se encontró el archivo de metadatos de las capturas: {self.csv_path}"

        activity_by_zone,empty_count = await self.get_activity_by_zone()

        # Construcción del string de contexto
        context_text = f"INFORME DE PATRULLA:\n\tTramos sin incidencias: {empty_count} fotos en áreas vacías.\n\n"
        if not activity_by_zone:
            return context_text + "ESTADO: Todo en orden. No se ha detectado actividad.\n"
            
        context_text += "\tREGISTRO DE INCIDENCIAS POR ZONA:\n"
        for zona, eventos in activity_by_zone.items():
            context_text += f"\n   UBICACIÓN: {zona}\n"
            for ev in eventos:
                texto_limpio = ev['report'].replace('Estado: ', '')
                context_text += f"[{ev['time']}s] {texto_limpio}\n"
                
        return context_text

    def call_ollama(self, context_text):
        '''Conexión HTTP con el servidor local de Llama-3'''

        prompt = f"""
        Eres la IA de seguridad de un robot patrulla en un hospital. 
        A continuación tienes el registro de actividad organizado por las diferentes habitaciones y zonas del hospital.
        
        Tu tarea es redactar un informe profesional para el responsable de planta. 
        Destaca las anomalías y riesgos, y resume la actividad. Infiere qué actividad realizan.
        Usa un tono formal, claro y conciso. No inventes datos.

        {context_text}
        
        INFORME DE SEGURIDAD:
        """
        payload = {"model": "llama3", "prompt": prompt, "stream": False}
        try:
            response = requests.post("http://localhost:11434/api/generate", json=payload)
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error conectando con Ollama: {e}"

def main(args=None):
    rclpy.init(args=args)
    node = LLMReporterNode()
    
    # Es necesario el multihilo para esperar sin bloquear
    # la recepción del nodo
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