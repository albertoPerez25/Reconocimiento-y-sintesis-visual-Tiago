#!/usr/bin/env python3
import rclpy
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
        
        if not self.vision_cli.wait_for_service(timeout_sec=5.0):
            response.success = False
            response.message = "Error: Nodo visual inactivo"
            return response
        
        zone_groups = self.get_images_grouped_by_zone()
        if not zone_groups:
            response.success = False
            response.message = "No hay datos."
            return response

        # Mapear cada zona independiantemente para evitar saturar la ventana de contexto (Map-Reduce Prompting)
        global_context = ""
        for zone, images in zone_groups.items():
            if self.abort_processing:
                self.get_logger().warn("Procesamiento abortado a petición del nodo de patrulla")
                response.success = False
                response.message = "Abortado por el usuario"
                return response

            zone_summary = await self.process_zone(zone, images)
            global_context += zone_summary

        if self.abort_processing:
            response.success = False
            return response
        
        return self.generate_global_summary(global_context, response)
    
    async def process_zone(self, zona, images):
        '''Analiza las imágenes de una zona y devuelve su mini-reporte'''
        self.get_logger().info(f"Procesando zona: {zona} ({len(images)} imágenes)...")
        zona_context = f"REGISTRO BRUTO DE {zona}:\n"
        has_activity = False
        
        if self.perception_mode == 'sequence':
            if not self.abort_processing and len(images) > 0:
                rutas_str = ",".join([img['path'] for img in images])
                
                req = AnalyzeActivity.Request()
                req.image_path = rutas_str
                result = await self.vision_cli.call_async(req)
                
                if "Despejado" not in result.report:
                    has_activity = True
                    zona_context += f"[SECUENCIA DE CÁMARA] {result.report.strip()}\n"
        else:
            for img in images:
                if self.abort_processing:
                    break
                req = AnalyzeActivity.Request()
                req.image_path = img['path']
                result = await self.vision_cli.call_async(req) 
                
                if "Despejado" not in result.report:
                    has_activity = True
                    zona_context += f"[{img['time']}s] {result.report.strip()}\n"

        if not has_activity:
            return f"    {zona.upper()}     \nSin incidencias. Zona despejada.\n\n"
            
        prompt = f"""
        You are the security AI for a hospital patrol robot. You are receiving the summary
        obtained by a basic YOLO-Pose model and a general VLM model. Your job is to SUMMARIZE both reports
        in one BRIEF report. If only one of those is available, use that one.

        Focus specifically on anomalies and life-safety risks within the hospital 
        (e.g., fires, live wires, overturned chairs, objects obstructing hallways/paths). 
        Prioritize the YOLO summary, output the VLM only if it detects something
        DANGEROUS to any person. If the YOLO summary has Todo correcto, then you won't print the YOLO output.

        You must analyze people activities and warn if someone is in need of help (like people who have
        fallen into the ground, running, yelling, fights...). People who need help and anything related to
        people (personnel, patients or visitors). Be brief and don't give any recommendations. 
        Answer briefly in Spanish, and if there's nothing to worry about, answer briefly with "Todo correcto.". If 
        there's an incident, start with "ATENCIÓN:". Avoid printing unnecessary events.
        
        Resume MUY BREVEMENTE las incidencias importantes en la siguiente zona.\n{zona_context}\n. Si no hay incidencias
        relevantes, responde únicamente con "Todo correcto.". Si hay incidencias, agrega un ATENCIÓN: al inicio. Evita imprimir
        eventos no importantes.
        

        MINI-REPORTE MUY BREVE:"""
        try:
            zone_summary = call_ollama_api(
                "http://localhost:11434/api/generate",
                {"model": "llama3", "prompt": prompt, "stream": False}
            )
            self.get_logger().info(zone_summary)
            return f"    {zona.upper()}     \n{zone_summary}\n\n"

        except Exception as e:
            self.get_logger().warn(f"Error resumiendo la zona {zona}: {e}")
            return f"    {zona.upper()}     \nError de procesamiento al resumir.\n\n"
        
    def generate_global_summary(self, global_context, response):
        '''Toma todos los mini reportes y genera el resumen final unificado'''
        self.get_logger().info("Generando informe global unificado con Llama-3...")
        self.get_logger().info(f"CONTEXTO:{global_context}")
        
        final_prompt = f"""
        You are the security AI for a hospital patrol robot. 
        Below are the individual mini-reports for each zone of the hospital during the last patrol.

        Your task is to write a comprehensive and professional GLOBAL SUMMARY for the Floor Manager. 

        MINI REPORTES:
        {global_context}

        Focus specifically on anomalies and life-safety risks within the hospital 
        (e.g., fires, live wires, overturned chairs, objects obstructing hallways/paths). 
        You must analyze people activities and warn if someone is in need of help (like people who have
        fallen into the ground, running, yelling, fights...). People who need help and anything related to
        people (personnel, patients or visitors).

        Do not hallucinate or invent any data, report only what is explicitly stated in the mini-reports. Give priority to 
        people fallen on the ground.

        Answer in spanish.
        
        RESUMEN DE SEGURIDAD GLOBAL:
        """
        
        try:
            final_report = call_ollama_api(
                "http://localhost:11434/api/generate", 
                {"model": "llama3", "prompt": final_prompt, "stream": False}
            )
            self.get_logger().info(f"\n\n\tINFORME FINAL\n{final_report}\n")
            
            response.success = True
            response.message = f"Informe generado:\n{final_report}"
        except Exception as e:
            self.get_logger().error(f"Error conectando con Ollama: {e}")
            response.success = False
            response.message = str(e)

        return response       

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