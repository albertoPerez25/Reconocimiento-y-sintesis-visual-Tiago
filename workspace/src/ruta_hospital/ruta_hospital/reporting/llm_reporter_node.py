#!/usr/bin/env python3
import time
import rclpy
import json
from rclpy.executors import MultiThreadedExecutor
from hospital_interfaces.srv import AnalyzeActivity
from ruta_hospital.reporting.base_reporter import BaseReporterNode
from ruta_hospital.commons.api_utils import call_ollama_api

class LLMReporterNode(BaseReporterNode):
    def __init__(self):
        super().__init__('llm_reporter_node')
        self.declare_parameter('perception_mode', 'image') # 'sequence' para VLM temporal, 'image' para YOLO foto a foto
        self.perception_mode = self.get_parameter('perception_mode').get_parameter_value().string_value
        self.vision_cli = self.create_client(AnalyzeActivity, 'analyze_image', callback_group=self.cb_group)
        
        if self.perception_mode == "sequence":
            self.get_logger().info("MODO SECUENCIA DE IMAGENES")
        else:
            self.get_logger().info("MODO IMAGENES INDIVIDUALES")


    async def generate_report_callback(self, request, response):
        '''Se ejecuta de manera asíncrona al llamar al servicio /generate_patrol_report'''
        self.abort_processing = False
        self.get_logger().info("Iniciada generación del informe")

        t_inicio_total = time.time()
        
        zone_groups = self.validate_data(response)
        if not zone_groups:
            return response
        
        global_context_json = await self.process_each_image(zone_groups, response)
        if not global_context_json or self.abort_processing:
            return response
        
        t_init_llm = time.time()

        global_sum = self.generate_global_summary(global_context_json, response)
        
        self.current_metrics["tiempo_llm_segundos"] = round(time.time() - t_init_llm, 2)
        self.current_metrics["tiempo_total_segundos"] = round(time.time() - t_inicio_total, 2)
        self.save_metrics()

        return global_sum
        

    def validate_data(self, response):
        if not self.vision_cli.wait_for_service(timeout_sec=5.0):
            response.success = False
            response.message = "Error: Nodo visual inactivo"
            return None
        
        zone_groups = self.get_images_grouped_by_zone()
        if not zone_groups:
            response.success = False
            response.message = "No hay datos"
            return response  
        
        self.current_metrics["total_imagenes_procesadas"] = sum(len(imgs) for imgs in zone_groups.values())
        return zone_groups
    

    async def process_each_image(self, zone_groups, response):
        hospital_data = {}
        t_init_perception = time.time()

        for zone, images in zone_groups.items():
            if self.abort_processing:
                self.get_logger().warn("Procesamiento abortado a petición del nodo de patrulla")
                response.success = False
                response.message = "Abortado por el usuario"
                return None

            zona_dict = await self.process_zone(zone, images)
            hospital_data[zone] = zona_dict

        global_context_json = json.dumps(hospital_data, ensure_ascii=False, indent=2)

        self.current_metrics["tiempo_percepcion_segundos"] = round(time.time() - t_init_perception, 2)
        self.current_metrics["caracteres_contexto_visual"] = len(global_context_json)
        return global_context_json
    

    async def process_zone(self, zona, images):
        '''Analiza las imágenes de una zona y devuelve su mini-reporte'''
        self.get_logger().info(f"Procesando zona: {zona} ({len(images)} imágenes)...")

        zone_data = {
            #"limites": self.get_zone_limits(zona),
            "eventos_recientes": []
        }
        
        if self.perception_mode == 'sequence':
            has_activity = await self.process_sequence_mode(images,zone_data)
        else:
            has_activity = await self.process_individual_mode(images,zone_data)

        if not has_activity:
            self.current_metrics["zonas_despejadas"] += 1
        else:
            self.current_metrics["zonas_con_output"] += 1
        return zone_data
    

    async def process_sequence_mode(self,images,zone_data,):
        '''Procesa una zona según la lógica de secuencia'''
        if not self.abort_processing and len(images) > 0:
            return False
        
        rutas_str = ",".join([img['path'] for img in images])
        req = AnalyzeActivity.Request()
        req.image_path = rutas_str
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
        
    
    async def process_individual_mode(self,images,zone_data):
        '''Procesa una zona según para el modo de imágenes sueltas'''
        has_activity = False
        for img in images:
            if self.abort_processing:
                break
            req = AnalyzeActivity.Request()
            req.image_path = img['path']
            result = await self.vision_cli.call_async(req) 
            
            try:
                vlm_dict = json.loads(result.report) # si no carga el formato estaba mal
            except:
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


    def generate_global_summary(self, global_context, response):
        '''Toma todos los mini reportes y genera el resumen final unificado'''
        self.get_logger().info("Generando informe global unificado con Llama-3...")
        self.get_logger().info(f"CONTEXTO:{global_context}")
        
        final_prompt = self.get_final_prompt(global_context)
        
        try:
            final_report = call_ollama_api(
                "http://localhost:11434/api/generate", 
                {"model": "llama3", "prompt": final_prompt, "stream": False}
            )
            self.get_logger().info(f"\n\n\tINFORME FINAL\n{final_report}\n")
            self.current_metrics["caracteres_informe_final"] = len(final_report)
            
            response.success = True
            response.message = f"Informe generado:\n{final_report}"
        except Exception as e:
            self.get_logger().error(f"Error conectando con Ollama: {e}")
            response.success = False
            response.message = str(e)

        return response 
    
    def get_final_prompt(self, global_context):
        '''Devuelve el prompt final del llm'''
        return f"""
            You are the security AI for a hospital patrol robot. 
            Below are the individual mini-reports for each zone of the hospital during the last patrol.

            Your task is to write a comprehensive and professional GLOBAL SUMMARY for the Floor Manager. 

            MINI REPORTES:
            {global_context}

            Focus specifically on anomalies and life-safety risks within the hospital 
            (e.g., fires, live wires, overturned chairs, objects obstructing hallways/paths). 
            You must analyze people activities and warn if someone is in need of help (like people who have
            fallen into the ground, running, yelling, fights...). People who need help and anything related to
            people (personnel, patients or visitors). Say clearly where each incident has happened.

            Do not hallucinate or invent any data, report only what is explicitly stated in the mini-reports. Give priority to 
            people fallen on the ground.

            Answer in spanish.
            
            RESUMEN DE SEGURIDAD GLOBAL:
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