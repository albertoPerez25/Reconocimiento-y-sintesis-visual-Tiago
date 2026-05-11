import json
from abc import ABC, abstractmethod
from hospital_interfaces.srv import AnalyzeActivity

class BasePerceptionStrategy(ABC):
    '''Estrategia base abstracta para el procesamiento de datos visuales'''
    def __init__(self, vision_cli, reporter_node):
        self.vision_cli = vision_cli
        self.reporter = reporter_node

    def get_expected_activities(self, zone):
        '''Extrae las actividades comunes de la zona directamente de los metadatos del reportero'''
        activities = self.reporter.get_zone_metadata(zone).get("actividades_comunes", [])
        return ", ".join(activities) if activities else "No especificados"

    def parse_and_append_event(self, result_report, time_str, zone_data):
        '''Parsea el resultado del LLM/VLM, filtra respuestas nulas y añade el evento si procede'''
        try:
            vlm_dict = json.loads(result_report)
        except Exception:
            vlm_dict = {
                "descripcion_vlm": result_report.strip(), 
                "alerta": ("ATENCIÓN" in result_report.upper() or "PELIGRO" in result_report.upper())
            }
        
        desc = vlm_dict.get("descripcion_vlm", "").lower()
        if "despejado" not in desc and "(ignorar)" not in desc and "no se han detectado personas" not in desc:
            zone_data["eventos_recientes"].append({
                "tiempo": time_str, 
                "descripcion_vlm": vlm_dict.get("descripcion_vlm", ""),
                "alerta": vlm_dict.get("alerta", False)
            })
            return True
        return False

    @abstractmethod
    async def process(self, items, zone, zone_data, goal_handle):
        '''Ejecuta la inferencia de la cámara/clip, devuelve True si detecta actividad'''
        pass

class SequencePerceptionStrategy(BasePerceptionStrategy):
    '''Procesa una zona según la lógica de secuencia (varias fotos en una llamada de modelo)'''
    async def process(self, images, zone, zone_data, goal_handle):
        if goal_handle.is_cancel_requested or len(images) == 0:
            return False
        
        rutas_str = ",".join([img['path'] for img in images])
        req = AnalyzeActivity.Request()
        req.image_path = rutas_str

        time_str = f"{images[-1]['time']}s" # Tiempo aproximado para eventos de secuencia
        req.zone_name = zone
        req.time = f"{images[0]['time']}s - {images[-1]['time']}s"
        req.expected_activities = self.get_expected_activities(zone)
        req.zone_type = zone_data["tipo_zona"]

        result = await self.vision_cli.call_async(req)
        
        return self.parse_and_append_event(result.report, time_str, zone_data)

class ImagePerceptionStrategy(BasePerceptionStrategy):
    '''Procesa una zona iterando foto a foto individualmente'''
    async def process(self, images, zone, zone_data, goal_handle):
        has_activity = False
        for img in images:
            if goal_handle.is_cancel_requested:
                break

            req = AnalyzeActivity.Request()
            req.image_path = img['path']

            req.zone_name = zone
            req.time = f"{img['time']}s"
            req.expected_activities = self.get_expected_activities(zone)
            req.zone_type = zone_data["tipo_zona"]

            result = await self.vision_cli.call_async(req) 
            
            if self.parse_and_append_event(result.report, req.time, zone_data):
                has_activity = True
                
        return has_activity

class VideoPerceptionStrategy(BasePerceptionStrategy):
    '''Procesa una zona mandando clips de vídeo'''
    async def process(self, files, zone, zone_data, goal_handle):
        has_activity = False
        
        for video_file in files:
            if goal_handle.is_cancel_requested:
                break

            req = AnalyzeActivity.Request()
            req.image_path = video_file['path']
            req.zone_name = zone
            req.time = f"{video_file['time']}s"
            req.expected_activities = self.get_expected_activities(zone)
            req.zone_type = zone_data["tipo_zona"]

            result = await self.vision_cli.call_async(req) 
            
            if self.parse_and_append_event(result.report, req.time, zone_data):
                has_activity = True
                
        return has_activity