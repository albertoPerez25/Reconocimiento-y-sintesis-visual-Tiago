import time
import json
import os
import shutil
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
    
    def save_evidence(self, paths_str, zone, time_str, desc, captured_round):
        '''Copia los archivos y genera un ticket .txt en subcarpetas jerárquicas'''
        safe_zone = zone.replace(" ", "_").replace("/", "_")
        alarm_id = self.reporter.get_next_alarm_id(captured_round)
        
        # Construcción de la jerarquía: .../evidence_dir/vuelta_X/alarma_Y_ZONA/
        round_dir = os.path.join(self.reporter.evidence_dir, f"vuelta_{captured_round}")
        alarm_dir = os.path.join(round_dir, f"alarma_{alarm_id}_{safe_zone}")
        
        try:
            os.makedirs(alarm_dir, exist_ok=True)
            
            # Separar rutas (sirve para un archivo único o para secuencias)
            paths = [p.strip() for p in paths_str.split(',') if p.strip()]
            
            # Copiar todos los archivos multimedia DENTRO de la carpeta de la alarma
            for idx, p in enumerate(paths):
                if os.path.exists(p):
                    ext = os.path.splitext(p)[1]
                    # Si es secuencia, les pone frame_0, frame_1... Si es foto única: evidencia.jpg
                    filename = f"frame_{idx}{ext}" if len(paths) > 1 else f"evidencia{ext}"
                    shutil.copy(p, os.path.join(alarm_dir, filename))
            
            # Generar Ticket de Texto explicativo junto a las fotos
            txt_path = os.path.join(alarm_dir, "informe_alarma.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"VUELTA LÓGICA: {captured_round}\n")
                f.write(f"ZONA: {zone}\n")
                f.write(f"TIEMPO: {time_str}\n\n")
                f.write(f"EVALUACIÓN DEL MODELO:\n{desc}\n")
                
            self.reporter.get_logger().info(f"Evidencia guardada en: {alarm_dir}")
        except Exception as e:
            self.reporter.get_logger().error(f"Fallo al guardar subcarpeta de evidencia: {e}")

    def parse_and_append_event(self, result_report, time_str, zone_data):
        '''Parsea el resultado, filtra nulos y devuelve (actividad_detectada, es_alerta, descripcion)'''
        try:
            vlm_dict = json.loads(result_report)
            if not isinstance(vlm_dict, dict):
                vlm_dict = {
                    "descripcion_vlm": str(vlm_dict).strip(), 
                    "alerta": ("ATENCIÓN" in str(vlm_dict).upper() or "PELIGRO" in str(vlm_dict).upper())
                }
        except Exception:
            vlm_dict = {
                "descripcion_vlm": result_report.strip(), 
                "alerta": ("ATENCIÓN" in result_report.upper() or "PELIGRO" in result_report.upper())
            }
        
        desc = vlm_dict.get("descripcion_vlm", "")
        is_alert = vlm_dict.get("alerta", False)
        
        if "despejado" not in desc.lower() and "(ignorar)" not in desc.lower() and "no se han detectado personas" not in desc.lower():
            zone_data["eventos_recientes"].append({
                "tiempo": time_str, 
                "descripcion_vlm": desc,
                "alerta": is_alert
            })
            return True, is_alert, desc
            
        return False, False, ""

    @abstractmethod
    async def process(self, items, zone, zone_data, goal_handle=None):
        '''Ejecuta la inferencia de la cámara/clip, devuelve True si detecta actividad.
        Ejecuta la inferencia. goal_handle es opcional para soportar streaming en vivo'''
        pass

class SequencePerceptionStrategy(BasePerceptionStrategy):
    '''Procesa una zona según la lógica de secuencia (varias fotos en una llamada de modelo)'''
    async def process(self, images, zone, zone_data, captured_round, goal_handle=None):
        if (goal_handle and goal_handle.is_cancel_requested) or len(images) == 0:
            return False
        
        rutas_str = ",".join([img['path'] for img in images])
        req = AnalyzeActivity.Request()
        req.image_path = rutas_str

        time_str = f"{images[-1]['time']}s" # Tiempo aproximado para eventos de secuencia
        req.zone_name = zone
        req.time = f"{images[0]['time']}s - {images[-1]['time']}s"
        req.expected_activities = self.get_expected_activities(zone)
        req.zone_type = zone_data["tipo_zona"]

        has_activity = False
        t_start_inference = time.time()

        try:
            result = await self.vision_cli.call_async(req)
            t_inference = time.time() - t_start_inference

            with self.reporter.data_lock:
                self.reporter.current_metrics["tiempo_percepcion_segundos"] = round(
                    self.reporter.current_metrics.get("tiempo_percepcion_segundos", 0.0) + t_inference, 2
                )
                self.reporter.current_metrics["total_imagenes_procesadas"] = self.reporter.current_metrics.get("total_imagenes_procesadas", 0) + len(images)

            has_activity, is_alert, desc = self.parse_and_append_event(result.report, time_str, zone_data)

            if is_alert:
                self.save_evidence(rutas_str, zone, time_str, desc, captured_round)

        except Exception as e:
            t_inference = time.time() - t_start_inference
            with self.reporter.data_lock:
                self.reporter.current_metrics["tiempo_percepcion_segundos"] = round(
                    self.reporter.current_metrics.get("tiempo_percepcion_segundos", 0.0) + t_inference, 2
                )
                self.reporter.current_metrics["total_imagenes_procesadas"] = self.reporter.current_metrics.get("total_imagenes_procesadas", 0) + len(images)
            
            self.reporter.get_logger().error(f"Error llamando a visión para la secuencia {rutas_str}: {e}")

        if not self.reporter.keep_photos:
            paths_to_delete = [p.strip() for p in rutas_str.split(',') if p.strip()]
            for file_path in paths_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except OSError as e:
                    self.reporter.get_logger().error(f"Error borrando archivo {file_path}: {e}")

        return has_activity

class ImagePerceptionStrategy(BasePerceptionStrategy):
    '''Procesa una zona iterando foto a foto individualmente'''
    async def process(self, images, zone, zone_data, captured_round, goal_handle=None):
        has_activity = False
        for img in images:
            if goal_handle and goal_handle.is_cancel_requested:
                break

            req = AnalyzeActivity.Request()
            req.image_path = img['path']

            req.zone_name = zone
            req.time = f"{img['time']}s"
            req.expected_activities = self.get_expected_activities(zone)
            req.zone_type = zone_data["tipo_zona"]

            t_start_inference = time.time()
            result = await self.vision_cli.call_async(req) 
            t_inference = time.time() - t_start_inference

            with self.reporter.data_lock:
                self.reporter.current_metrics["tiempo_percepcion_segundos"] = round(
                    self.reporter.current_metrics.get("tiempo_percepcion_segundos", 0.0) + t_inference, 2
                )
                self.reporter.current_metrics["total_imagenes_procesadas"] = self.reporter.current_metrics.get("total_imagenes_procesadas", 0) + 1 
            
            has_activity, is_alert, desc = self.parse_and_append_event(result.report, req.time, zone_data)
                
            if is_alert:
                self.save_evidence(img['path'], zone, req.time, desc, captured_round,)

            if not self.reporter.keep_photos:
                try:
                    if os.path.exists(img['path']):
                        os.remove(img['path'])
                except OSError as e:
                    self.reporter.get_logger().error(f"Error borrando archivo {img['path']}: {e}")
                
        return has_activity

class VideoPerceptionStrategy(BasePerceptionStrategy):
    '''Procesa una zona mandando clips de vídeo'''
    async def process(self, files, zone, zone_data, captured_round, goal_handle=None):
        has_activity = False
        
        for video_file in files:
            if goal_handle and goal_handle.is_cancel_requested:
                break
            self.reporter.current_metrics["total_imagenes_procesadas"] += 1

            req = AnalyzeActivity.Request()
            req.image_path = video_file['path']
            req.zone_name = zone
            req.time = f"{video_file['time']}s"
            req.expected_activities = self.get_expected_activities(zone)
            req.zone_type = zone_data["tipo_zona"]

            try:
                result = await self.vision_cli.call_async(req) 
                
                has_activity, is_alert, desc = self.parse_and_append_event(result.report, req.time, zone_data)
                    
                if is_alert:
                    self.save_evidence(video_file['path'], zone, req.time, desc, captured_round)

            except Exception as e:
                self.reporter.get_logger().error(f"Error llamando a visión para {video_file['path']}: {e}")

            if not self.reporter.keep_photos:
                try:
                    if os.path.exists(video_file['path']):
                        os.remove(video_file['path'])
                except OSError as e:
                    self.reporter.get_logger().error(f"Error borrando archivo {video_file['path']}: {e}")
                
        return has_activity