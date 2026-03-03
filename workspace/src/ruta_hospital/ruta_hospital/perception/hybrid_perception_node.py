#!/usr/bin/env python3
import rclpy
import os
from ruta_hospital.perception.base_perception import BasePerceptionNode
from .yolo_perception_node import YoloPerceptionNode
from .vlm_perception_node import VLMPerceptionNode

class HybridPerceptionNode(BasePerceptionNode):
    def __init__(self):
        super().__init__('hybrid_perception_node')
        
        # Apaga servicios fantasma al instanciarlos (deadlock)
        self.yolo_logic = YoloPerceptionNode(start_service=False)
        self.vlm_logic = VLMPerceptionNode(start_service=False)
        
        self.get_logger().info("Nodo percepcion con YOLO y VLM iniciado")

    def process_image(self, image_path: str) -> str:
        '''Combina los reportes de YOLO y VLM'''
        
        self.get_logger().info(f"Procesamiento híbrido iniciado para: {image_path}")

        # Posiciones y conteo exacto
        yolo_report = self.yolo_logic.process_image(image_path)
        
        # Contexto, peligros y descripción
        vlm_report = self.vlm_logic.process_image(image_path)

        combined_report = (
            " ANÁLISIS POSICIONAL (YOLO)\n"
            f"{yolo_report}\n\n"
            " ANÁLISIS SEMÁNTICO (VLM)\n"
            f"{vlm_report}\n"
        )

        self.get_logger().info(combined_report)
        return combined_report
    
    def check_path(self, path):
        '''Metodo para comprobar que el path es de una imagen que exista'''
        return os.path.isfile(path)

def main(args=None):
    rclpy.init(args=args)
    node = HybridPerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()