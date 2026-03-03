#!/usr/bin/env python3
import os
import csv
import rclpy
from rclpy.executors import MultiThreadedExecutor
from hospital_interfaces.srv import AnalyzeActivity
from ruta_hospital.reporting.base_reporter import BaseReporterNode
from ruta_hospital.commons.api_utils import call_ollama_api

class LLMReporterNode(BaseReporterNode):
    def __init__(self):
        super().__init__('llm_reporter_node')
        self.vision_cli = self.create_client(AnalyzeActivity, 'analyze_image', callback_group=self.cb_group)

    async def generate_report_callback(self, request, response):
        '''Se ejecuta de manera asíncrona al llamar al servicio /generate_patrol_report'''
        self.get_logger().info("Iniciada generación del informe")
        if not self.vision_cli.wait_for_service(timeout_sec=5.0):
            response.success = False
            response.message = "Error: Nodo visual inactivo"
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
        response.message = f"Informe generado:\n{final_report}"
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
                req = AnalyzeActivity.Request()
                req.image_path = img_path
                result = await self.vision_cli.call_async(req)
                
                if "Despejado" in result.report: 
                    empty_count += 1
                else:
                    nombre_zona = self.get_zone_name(x, y)
                    if nombre_zona not in activity_by_zone: 
                        activity_by_zone[nombre_zona] = []

                    activity_by_zone[nombre_zona].append({'time': int(row['timestamp_sec']), 'report': result.report.strip()})
                    
        return activity_by_zone, empty_count

    async def get_context_text_async(self):
        ''' Itera sobre las fotos, llama al servicio visual y cruza con las zonas
            Asíncrono para evitar el congelamiento del hilo del nodo, 
            lo que provoca un deadlock al no consumir los datos de entrada
        '''        
        if not os.path.isfile(self.csv_path): 
            return f"Error: No se encontró {self.csv_path}"
        
        activity_by_zone, empty_count = await self.get_activity_by_zone()

        context_text = f"INFORME DE PATRULLA:\n\tTramos sin incidencias: {empty_count} fotos en áreas vacías.\n\n"
        if not activity_by_zone: 
            return context_text + "ESTADO: Todo en orden.\n"
            
        context_text += "\tREGISTRO DE INCIDENCIAS POR ZONA:\n"
        for zona, eventos in activity_by_zone.items():
            context_text += f"\n   UBICACIÓN: {zona}\n"
            for ev in eventos: 
                context_text += f"[{ev['time']}s] {ev['report'].replace('Estado: ', '')}\n"
        return context_text

    def call_ollama(self, context_text):
        '''Construye el prompt específico para este nodo y llama a la API'''
        prompt = f"""
        You are the security AI for a hospital patrol robot. 
        Below is the activity log organized by the various rooms and areas of the hospital.

        Your task is to write a professional summary for the Floor Manager. 
        Highlight any anomalies and risks, and summarize the general activity. 
        Use a formal, clear, and concise tone.

        Focus specifically on anomalies and life-safety risks within the hospital 
        (e.g., fires, live wires, overturned chairs, objects obstructing hallways/paths). 
        Do not hallucinate or invent data; report only what is explicitly stated in the log.

        {context_text}
        
        SECURITY SUMMARY:
        """
        
        payload = {"model": "llama3", "prompt": prompt, "stream": False}
        
        try:
            return call_ollama_api("http://localhost:11434/api/generate", payload)
        except Exception as e:
            return f"Error conectando con Ollama: {e}"

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