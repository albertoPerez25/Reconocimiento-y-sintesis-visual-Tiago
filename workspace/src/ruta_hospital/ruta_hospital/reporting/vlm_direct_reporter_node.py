#!/usr/bin/env python3
import rclpy
from rclpy.executors import MultiThreadedExecutor
from ruta_hospital.commons.api_utils import encode_image_to_base64, call_ollama_api
from ruta_hospital.reporting.base_reporter import BaseReporterNode

class VLMDirectReporterNode(BaseReporterNode):
    def __init__(self):
        super().__init__('vlm_direct_reporter_node')
        #self.declare_parameter('vlm_model', 'llava') # No tengo tanta VRAM
        self.declare_parameter('vlm_model', 'moondream')
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')
        self.vlm_model = self.get_parameter('vlm_model').get_parameter_value().string_value
        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value

    async def generate_report_callback(self, request, response):
        '''Gestiona las llamadas para obtener mini reportes y generar el informe final'''
        self.get_logger().info("Iniciada generación del informe VLM (Map-Reduce)")
        
        zone_groups = self.get_images_grouped_by_zone()
        if not zone_groups:
            response.success = False
            response.message = "No hay datos."
            return response

        global_context = ""
        for zone, images in zone_groups.items():
            zone_summary = self.process_visual_zone(zone, images)
            global_context += zone_summary

        return self.generate_global_summary(global_context, response)
    
    def process_visual_zone(self, zone, images):
        '''Usa el VLM para analizar visualmente todas las fotos de una zona'''
        self.get_logger().info(f"VLM analizando zona: {zone} ({len(images)} imágenes)...")
        
        base64_images = []
        metadata_context = f"ZONE: {zone}\n"
        
        for i, img in enumerate(images):
            base64_images.append(encode_image_to_base64(img['path']))
            metadata_context += f"- Image {i+1}: Taken at {img['time']}s.\n"

        zone_prompt = f"""
        You are a security AI. I have attached {len(base64_images)} IMAGES from the {zone}.
        {metadata_context}
        VISUALLY ANALYZE these attached images and write a brief summary of anomalies or risks detected.

        Focus specifically on anomalies and life-safety risks within the hospital 
        (e.g., fires, live wires, overturned chairs, objects obstructing hallways/paths). 
        You must analyze people activities and warn if someone is in need of help (like people who have 
        fallen on the ground, running, yelling, aggressive movements, fights...). Anything related to
        people (personnel, patients or visitors).

        Do not just repeat the metadata. Rely ONLY on the visual content.
        """
        
        try:
            zone_summary = call_ollama_api(
                self.ollama_url,
                {"model": self.vlm_model, "prompt": zone_prompt, "images": base64_images, "stream": False}
            )
            return f"--- {zone.upper()} ---\n{zone_summary}\n\n"
        except Exception as e:
            self.get_logger().warn(f"Fallo al procesar visualmente la zona {zone}: {e}")
            return f"--- {zone.upper()} ---\nError de procesamiento visual.\n\n"
        
    def generate_global_summary(self, global_context, response):
        '''Genera el informe final a partir de los reportes por zonas '''
        self.get_logger().info("Generando informe global unificado con Llama-3...")
        
        final_prompt = f"""
        You are the security AI for a hospital patrol robot. 
        Below are the individual visual mini-reports for each zone of the hospital during the last patrol.

        Your task is to write a comprehensive and professional GLOBAL SUMMARY for the Floor Manager. 
        Highlight anomalies and life-safety risks. 
        
        Focus specifically on anomalies and life-safety risks within the hospital 
        (e.g., fires, live wires, overturned chairs, objects obstructing hallways/paths). 
        You must analyze people activities and warn if someone is in need of help (like people who have 
        fallen on the ground, running, yelling, aggressive movements, fights...). Anything related to
        people (personnel, patients or visitors).

        Use a formal and clear tone. Do not invent data.

        MINI-REPORTS:
        {global_context}
        
        GLOBAL SECURITY SUMMARY:
        """
        
        try:
            final_report = call_ollama_api(
                self.ollama_url, 
                {"model": "llama3", "prompt": final_prompt, "stream": False}
            )
            self.get_logger().info(f"\n\n\tINFORME FINAL VLM-HÍBRIDO\n{final_report}\n")
            
            response.success = True
            response.message = f"Informe VLM:\n{final_report}"
        except Exception as e:
            self.get_logger().error(f"Error Ollama en informe final: {e}")
            response.success = False
            response.message = str(e)

        return response

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    executor.add_node(VLMDirectReporterNode())

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()


