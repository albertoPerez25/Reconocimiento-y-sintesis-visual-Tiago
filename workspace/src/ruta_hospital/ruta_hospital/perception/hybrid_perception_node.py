#!/usr/bin/env python3
import rclpy
import os
import json
from ruta_hospital.perception.base_perception import BasePerceptionNode
from .yolo_perception_node import YoloPerceptionNode
from .vlm_perception_node import VLMPerceptionNode
from dataclasses import dataclass

@dataclass
class model_atr:
    desc: str
    alert: bool

class HybridPerceptionNode(BasePerceptionNode):
    def __init__(self):
        super().__init__('hybrid_perception_node')
        
        # Apaga servicios que podrian hacer una condicion de carrera con este
        self.yolo_logic = YoloPerceptionNode(start_service=False)
        self.vlm_logic = VLMPerceptionNode(start_service=False)
        
        self.get_logger().info("Nodo percepcion con YOLO y VLM iniciado")

    def process_image(self, image_path: str, zone_name="Desconocida", time_str="Desconocida", expected_objects="No especificados") -> str:
        '''Combina los reportes de YOLO y VLM'''
        self.get_logger().info(f"Procesamiento híbrido iniciado para: {image_path}")

        # Posiciones y conteo exacto
        yolo_json_str = self.yolo_logic.process_image(image_path, zone_name, time_str, expected_objects)
        # Contexto, peligros y descripción
        vlm_json_str = self.vlm_logic.process_image(image_path, zone_name, time_str, expected_objects)

        try:
            yolo_data = json.loads(yolo_json_str)
        except json.JSONDecodeError:
            yolo_data = {"descripcion_vlm": "Error de formato YOLO", "alerta": False}

        try:
            vlm_data = json.loads(vlm_json_str)
        except json.JSONDecodeError:
            vlm_data = {"descripcion_vlm": "Error de formato VLM", "alerta": False}

        yolo_desc = yolo_data.get("descripcion_vlm", "")
        yolo_alert = yolo_data.get("alerta", False)
        yolo = model_atr(yolo_desc,yolo_alert)

        vlm_desc = vlm_data.get("descripcion_vlm", "")
        vlm_alert = vlm_data.get("alerta", False)
        vlm = model_atr(vlm_desc,vlm_alert)

        final_desc,final_alert = self.get_combined_json(yolo,vlm)

        json_response = {
            "descripcion_vlm": final_desc,
            "alerta": final_alert
        }
        return json.dumps(json_response, ensure_ascii=False)
    
    def get_combined_json(self, yolo, vlm):
        final_alert = yolo.alert or vlm.alert

        if "despejado" in yolo.desc.lower() and "despejado" in vlm.desc.lower():
            combined_desc = "Despejado"
        else:
            combined_desc = f"[YOLO]: {yolo.desc} | [VLM]: {vlm.desc}"
            
            # confianza en base a lo que detecto cada modelo
            if yolo.alert and vlm.alert:
                combined_desc += " ALTA FIABILIDAD: Incidencia confirmada por ambos modelos."
            elif yolo.alert and not vlm.alert:
                combined_desc += " FIABLE: Peligro posicional detectado por YOLO (posible falso negativo del VLM)."
            elif vlm.alert and not yolo.alert:
                combined_desc += " PRECAUCIÓN: Alerta exclusiva del VLM (posible falso positivo)."

        return combined_desc,final_alert
    
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