#!/usr/bin/env python3
import time
import rclpy
import json
from rclpy.executors import MultiThreadedExecutor
from hospital_interfaces.srv import AnalyzeActivity
from hospital_interfaces.action import GenerateReport
from ruta_hospital.reporting.base_reporter import BaseReporterNode
from ruta_hospital.reporting.utils.recursive_summarizer import RecursiveSummarizer

DEFAULT_PERCEPTION_MODE = 'image' # 'sequence' para VLM temporal, 'image' para YOLO foto a foto, 'video' para clips de video

class LLMReporterNode(BaseReporterNode):
    def __init__(self):
        super().__init__('llm_reporter_node')
        self.declare_parameter('perception_mode', DEFAULT_PERCEPTION_MODE) 
        self.perception_mode = self.get_parameter('perception_mode').get_parameter_value().string_value     
        self.vision_cli = self.create_client(AnalyzeActivity, 'analyze_image', callback_group=self.cb_group)
        
        if self.perception_mode == "sequence":
            self.get_logger().info("MODO SECUENCIA DE IMAGENES")
        elif self.perception_mode == "video":
            self.get_logger().info("MODO CLIPS DE VIDEO")
        else:
            self.get_logger().info("MODO IMAGENES INDIVIDUALES")


    async def execute_report_callback(self, goal_handle):
        '''Se ejecuta de manera asíncrona de la accion /generate_patrol_report'''
        folder_path = goal_handle.request.folder_path
        self.get_logger().info("Iniciada generación del informe")

        t_inicio_total = time.time()
        result = GenerateReport.Result()
        
        zone_groups = self.validate_data(folder_path, result)
        if not zone_groups:
            goal_handle.abort()
            return result
        
        global_context_json = await self.process_each_image(zone_groups, goal_handle, result)
        
        if goal_handle.is_cancel_requested:
            self.get_logger().warn("Proceso cancelado por el nodo patrulla")
            goal_handle.canceled()
            result.success = False
            result.final_report = "Cancelado por el usuario"
            return result
            
        if not global_context_json:
            goal_handle.abort()
            return result
        
        t_init_llm = time.time()

        global_sum = self.generate_global_summary(global_context_json, result)
        
        self.current_metrics["tiempo_llm_segundos"] = round(time.time() - t_init_llm, 2)
        self.current_metrics["tiempo_total_segundos"] = round(time.time() - t_inicio_total, 2)
        self.save_metrics()

        goal_handle.succeed()
        return global_sum
        

    def validate_data(self, folder_path, result):
        if not self.vision_cli.wait_for_service(timeout_sec=5.0):
            result.success = False
            result.final_report = "Error: Nodo visual inactivo"
            return None
        
        zone_groups = self.get_images_grouped_by_zone(folder_path)
        if not zone_groups:
            result.success = False
            result.message = "No hay datos"
            return result  
        
        self.current_metrics["total_imagenes_procesadas"] = sum(len(imgs) for imgs in zone_groups.values())
        return zone_groups
    

    async def process_each_image(self, zone_groups, goal_handle, result):
        hospital_data = {}
        t_init_perception = time.time()
        total_zones = len(zone_groups)

        for i, (zone, images) in enumerate(zone_groups.items()):
            if goal_handle.is_cancel_requested:
                return None
            
            feedback_msg = GenerateReport.Feedback()
            feedback_msg.current_zone = zone
            feedback_msg.percentage_complete = float((i / total_zones) * 100.0)
            goal_handle.publish_feedback(feedback_msg)

            zona_dict = await self.process_zone(zone, images, goal_handle)
            hospital_data[zone] = zona_dict

        global_context_json = json.dumps(hospital_data, ensure_ascii=False, indent=2)

        self.current_metrics["tiempo_percepcion_segundos"] = round(time.time() - t_init_perception, 2)
        self.current_metrics["caracteres_contexto_visual"] = len(global_context_json)
        return global_context_json
    

    async def process_zone(self, zone, images, goal_handle):
        '''Analiza las imágenes de una zona y devuelve su mini-reporte'''
        self.get_logger().info(f"Procesando zona: {zone} ({len(images)} imágenes)...")

        times = [img['time'] for img in images]
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0

        zone_info = self.get_zone_metadata(zone)

        zone_data = {
            #"limites": self.get_zone_limits(zona),
            "nombre_zona": zone,
            "tipo_zona": zone_info.get("tipo_zona", "Desconocida"),
            #"reglas_horarias": zona_info.get("reglas_horarias", "No hay reglas específicas."),
            "rango_temporal": f"{min_time}s - {max_time}s",
            "eventos_recientes": []
        }
        
        if self.perception_mode == 'sequence':
            has_activity = await self.process_sequence_mode(images, zone, zone_data, goal_handle)
        elif self.perception_mode == 'video':
            has_activity = await self.process_video_mode(images, zone, zone_data, goal_handle)
        else:
            has_activity = await self.process_individual_mode(images, zone, zone_data, goal_handle)

        if not has_activity:
            self.current_metrics["zonas_despejadas"] += 1
        else:
            self.current_metrics["zonas_con_output"] += 1
        return zone_data
    

    async def process_sequence_mode(self, images, zone, zone_data, goal_handle):
        '''Procesa una zona según la lógica de secuencia'''
        if goal_handle.is_cancel_requested or len(images) == 0:
            return False
        
        rutas_str = ",".join([img['path'] for img in images])
        req = AnalyzeActivity.Request()
        req.image_path = rutas_str

        req.zone_name = zone
        req.time = f"{images[0]['time']}s - {images[-1]['time']}s"
        activities = self.get_zone_metadata(zone).get("actividades_comunes", [])
        req.expected_activities = ", ".join(activities) if activities else "No especificados"
        req.zone_type = zone_data["tipo_zona"] # TODO: Cambiar todo para que sea coherente con el nuevo json de metadatos de hospital

        result = await self.vision_cli.call_async(req)
        
        try:
            vlm_dict = json.loads(result.report)
        except:
            vlm_dict = {"descripcion_vlm": result.report, "alerta": False}
        
        has_activity = False
        desc = vlm_dict.get("descripcion_vlm", "").lower()
        if "despejado" not in desc:
            has_activity = True
            aprox_time = f"{images[-1]['time']}s"
            zone_data["eventos_recientes"].append({
                "tiempo": aprox_time, 
                "descripcion_vlm": vlm_dict.get("descripcion_vlm", ""),
                "alerta": vlm_dict.get("alerta", False)
            })
        return has_activity
        
    
    async def process_individual_mode(self, images, zone, zone_data, goal_handle):
        '''Procesa una zona según para el modo de imágenes sueltas'''
        has_activity = False
        for img in images:
            if goal_handle.is_cancel_requested:
                break

            req = AnalyzeActivity.Request()
            req.image_path = img['path']

            req.zone_name = zone
            req.time = f"{img['time']}s"
            activities = self.get_zone_metadata(zone).get("actividades_comunes", [])
            req.expected_activities = ", ".join(activities) if activities else "No especificados"
            req.zone_type = zone_data["tipo_zona"]

            result = await self.vision_cli.call_async(req) 
            
            try:
                vlm_dict = json.loads(result.report) # si no carga el formato estaba mal
            except json.JSONDecodeError:
                vlm_dict = {
                    "descripcion_vlm": result.report.strip(), 
                    "alerta": ("ATENCIÓN" in result.report.upper() or "PELIGRO" in result.report.upper())
                }
            
            desc = vlm_dict.get("descripcion_vlm", "").lower()
            # Filtra datos irrelevantes para simplificar el output
            if "despejado" not in desc and "(ignorar)" not in desc and "no se han detectado personas" not in desc:
                has_activity = True
                zone_data["eventos_recientes"].append({
                    "tiempo": f"{img['time']}s", 
                    "descripcion_vlm": vlm_dict.get("descripcion_vlm", ""),
                    "alerta": vlm_dict.get("alerta", False)
                })
        return has_activity
    
    async def process_video_mode(self, files, zone, zone_data, goal_handle):
        '''Procesa una zona para el modo de vídeo (un clip = una llamada al modelo)'''
        has_activity = False
        
        for video_file in files:
            if goal_handle.is_cancel_requested:
                break

            req = AnalyzeActivity.Request()
            req.image_path = video_file['path'] # El video
            req.zone_name = zone
            req.time = f"{video_file['time']}s"
            
            activities = self.get_zone_metadata(zone).get("actividades_comunes", [])
            req.expected_activities = ", ".join(activities) if activities else "No especificados"
            req.zone_type = zone_data["tipo_zona"]

            result = await self.vision_cli.call_async(req) 
            
            # Formatear la salida asegurando consistencia con el reportero
            try:
                vlm_dict = json.loads(result.report)
            except json.JSONDecodeError:
                vlm_dict = {
                    "descripcion_vlm": result.report.strip(), 
                    "alerta": ("ATENCIÓN" in result.report.upper() or "PELIGRO" in result.report.upper())
                }
            
            desc = vlm_dict.get("descripcion_vlm", "").lower()
            
            if "despejado" not in desc and "(ignorar)" not in desc and "no se han detectado personas" not in desc:
                has_activity = True
                zone_data["eventos_recientes"].append({
                    "tiempo": f"{video_file['time']}s", 
                    "descripcion_vlm": vlm_dict.get("descripcion_vlm", ""),
                    "alerta": vlm_dict.get("alerta", False)
                })
                
        return has_activity


    def generate_global_summary(self, global_context, result):
        '''Toma todos los mini reportes y genera el resumen final unificado'''
        self.get_logger().info("Iniciando generación del resumen...")
        self.get_logger().debug(f"CONTEXTO:{global_context}")

        try:
            hospital_data = json.loads(global_context)
        except json.JSONDecodeError:
            result.success = False
            result.final_report = "Error: El contexto global no es un JSON válido."
            return result
        
        zone_texts = self.json_preprocessing(hospital_data)

        summarizer = RecursiveSummarizer(
            ollama_url=self.ollama_url,
            model_name=self.llm_model,
            logger=self.get_logger(),
            max_words=self.max_words  # Límite para el map reduce iterativo
        )

        try:
            final_report = summarizer.recursive_summarize(zone_texts, self.get_final_prompt)
            self.last_reduced_context = summarizer.final_context
            
            self.get_logger().info(f"\n\n\tINFORME FINAL\n{final_report}\n")
            self.current_metrics["caracteres_informe_final"] = len(final_report)
            
            result.success = True
            result.final_report = f"Informe generado:\n{final_report}"
        except Exception as e:
            self.get_logger().error(f"Error en resumen recursivo: {e}")
            result.success = False
            result.final_report = str(e)

        return result
    

    def json_preprocessing(self, hospital_data):
        '''Convierte el diccionario de datos del hospital en una lista de strings formateados por zona'''
        zone_texts = []
        for zone, info in hospital_data.items():
            if info.get("eventos_recientes"):
                zone_texts.append(f"ZONA: {zone}\n{json.dumps(info, ensure_ascii=False)}")
            else:
                zone_texts.append(f"ZONA: {zone}\n{json.dumps(info, ensure_ascii=False)}") # TODO
        
        if not zone_texts:
            zone_texts = ["Todas las zonas patrulladas se encuentran despejadas, sin incidentes ni personas detectadas"]
        
        return zone_texts
    

    def get_final_prompt(self, global_context):
        '''Devuelve el prompt final del llm'''
        return f"""
            You are the security AI for a hospital patrol robot. 
            Below are the individual mini-reports for each zone of the hospital during the last patrol.
            Each zone includes temporal data and specific safety rules (RAG context).

            Your task is to write a comprehensive and professional GLOBAL SUMMARY for the Floor Manager. 

            MINI REPORTES:
            {global_context}

            Focus specifically on anomalies, life-safety risks, and PROTOCOL VIOLATIONS based on the rules provided for each zone
            (e.g., people in restricted areas, activities outside allowed hours, fires, overturned chairs).
            You must analyze people activities and warn if someone is in need of help (like people who have fallen).
            Say clearly where and WHEN (using the temporal range) each incident has happened.

            Do not hallucinate or invent any data, report only what is explicitly stated in the mini-reports. Give priority to 
            people fallen on the ground.

            Answer in spanish.
            
            RESUMEN DE ACTIVIDADES EN EL HOSPITAL:
        """
    

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor() 
    executor.add_node(LLMReporterNode())
    try: 
        executor.spin()
    except KeyboardInterrupt: 
        pass
    finally: 
        rclpy.shutdown()

if __name__ == '__main__': 
    main()