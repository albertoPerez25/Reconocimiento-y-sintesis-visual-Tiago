#!/usr/bin/env python3
import rclpy
import os
import json
import cv2
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

        # Memoria a corto plazo
        self.tracking_memory = {}
        
        self.get_logger().info("Nodo percepcion con YOLO y VLM iniciado")

    def process_image(self, image_path, context):
        '''Combina los reportes de YOLO y VLM'''

        self.get_logger().info(f"Procesamiento híbrido iniciado para: {image_path}")
        self.get_logger().debug(f"zone_name:{context.zone_name} | time_str:{context.time_str} | expected_activities:{context.expected_activities} | zone_type:{context.zone_type}")

        # Posiciones, conteo exacto y tracking
        yolo_json_str = self.yolo_logic.process_image(image_path, None)
        
        try:
            yolo_data = json.loads(yolo_json_str)
        except json.JSONDecodeError:
            yolo_data = {"descripcion_vlm": "Error de formato YOLO", "alerta": False}

        detections = yolo_data.get("detections", [])
        if detections:
            image_to_vlm = self.get_image_with_tracking_data(detections, image_path, context)

        # Contexto, peligros y descripción
        vlm_json_str = self.vlm_logic.process_image(image_to_vlm, context)

        # Limpiaer frame temporal
        if image_to_vlm == "/tmp/annotated_vlm_frame.jpg" and os.path.exists(image_to_vlm):
            os.remove(image_to_vlm)

        try:
            vlm_data = json.loads(vlm_json_str)
        except json.JSONDecodeError:
            vlm_data = {"descripcion_vlm": "Error de formato VLM", "alerta": False}

        json_response = self.get_json_response(yolo_data, vlm_data)
        self.get_logger().debug(f"{json_response}")
        return json.dumps(json_response, ensure_ascii=False)
    
    def get_image_with_tracking_data(self, detections, image_path, context):
        '''Devuelve la imagen con un recuadrado señalando el trackeo hecho por YOLO'''
        final_image = image_path
        img_cv = cv2.imread(image_path)
        if img_cv is not None:
            history_str = ""
            COLORS = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 0, 255)]
            COLOR_NAMES = ["ROJA", "AZUL", "VERDE", "AMARILLA", "MAGENTA"]
            
            for det in detections:
                trk_id = det["id"]
                bbox = det["bbox"]
                
                # Limpiar la postura de YOLO para intentar no saturar al VLM
                clean_posture = det["posture"].replace("(ignorar) Todo correcto. ", "").replace("ATENCIÓN ", "")
                
                # Sliding Window (Memoria FIFO de 3 frames)
                if trk_id not in self.tracking_memory:
                    self.tracking_memory[trk_id] = []
                self.tracking_memory[trk_id].append(clean_posture)
                if len(self.tracking_memory[trk_id]) > 3:
                    self.tracking_memory[trk_id].pop(0)
                    
                # Colores y texto sobrepuestos a la imagen para pasársela al vlm
                color_idx = trk_id % len(COLORS)
                color_bgr = COLORS[color_idx]
                color_name = COLOR_NAMES[color_idx]
                
                history_str += f"- Sujeto ID_{trk_id} (Caja {color_name}): Historial -> {' | '.join(self.tracking_memory[trk_id])}\n"                
                cv2.rectangle(img_cv, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color_bgr, 3)
            
            context.tracking_history = history_str
            final_image = "/tmp/annotated_vlm_frame.jpg"
            cv2.imwrite(final_image, img_cv)

            return final_image
    
    def get_combined_json(self, yolo, vlm):
        '''Devuelve la descripcion y alertas finales teniendo en cuenta los json de yolo y del vlm'''
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
    
    def get_json_response(self, yolo_data, vlm_data):
        '''Devuelve la respuesta final a la petición en formato json'''
        yolo_desc = str(yolo_data.get("descripcion_vlm", "")) 
        yolo_alert = bool(yolo_data.get("alerta", False))
        yolo = model_atr(yolo_desc,yolo_alert)

        vlm_desc = str(vlm_data.get("descripcion_vlm", "")) # Convierto a str o bool para evitar que crashe si el vlm alucina pero devuelve un formato json "valido"
        vlm_alert = bool(vlm_data.get("alerta", False))
        vlm = model_atr(vlm_desc,vlm_alert)

        final_desc,final_alert = self.get_combined_json(yolo,vlm)

        json_response = {
            "descripcion_vlm": final_desc,
            "alerta": final_alert
        }
        return json_response
    
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