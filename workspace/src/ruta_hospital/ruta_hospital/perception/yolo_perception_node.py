#!/usr/bin/env python3
import cv2
import rclpy
import os
import json
from ultralytics import YOLO

# Servicio personalizado para comunicación entre LLM y Yolo
from ruta_hospital.perception.base_perception import BasePerceptionNode 

#yolov8n-pose.pt
DEFAULT_YOLO_MODEL = "yolo26n-pose.pt"
DEFAULT_MIN_CONFIDENCE = 0.5

class YoloPerceptionNode(BasePerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('yolo_perception_node',start_service=start_service)
        self.declare_parameter('yolo_model', DEFAULT_YOLO_MODEL)
        self.declare_parameter('min_confidence', DEFAULT_MIN_CONFIDENCE)

        selected_yolo_model = self.get_parameter('yolo_model').get_parameter_value().string_value
        self.min_confidence = self.get_parameter('min_confidence').get_parameter_value().double_value

        self.model = YOLO(selected_yolo_model)
        self.get_logger().info(f"Modelo {selected_yolo_model} cargado")

    def process_image(self, image_path, context):
        '''Procesa la imagen y devuelve el reporte en forma de string '''
        image = cv2.imread(image_path)
        if image is None:
            return json.dumps({"descripcion_vlm": "Error: No se pudo leer la imagen con OpenCV", "alerta": False}, ensure_ascii=False)

        results = self.model.track(image, persist=True, verbose=False)
        result = results[0]

        if len(result.boxes) == 0:
            return json.dumps({"descripcion_vlm": "Despejado", "alerta": False}, ensure_ascii=False)

        descriptions = []
        detections = []
        global_humans_detected = False

        ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else [i+1 for i in range(len(result.boxes))]

        for box, keypoints, track_id in zip(result.boxes, result.keypoints, ids):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1 
            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()
            
            posture = self.calculate_posture(width, height, pts, confs)
            descriptions.append(f"Persona {track_id}: {posture}")

            detections.append({
                "id": track_id,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "posture": posture
            })

            #if "ATENCIÓN" in posture:
            global_humans_detected = True

        # Conteo de personas con la lista de posturas
        final_description = f"Estado: Se han detectado {len(result.boxes)} persona(s). " + " ".join(descriptions)

        json_response = {
            "descripcion_vlm": final_description,
            "alerta": global_humans_detected,
            "detecciones": detections
        }

        return json.dumps(json_response, ensure_ascii=False) # evita que se rompan los acentos

    def calculate_posture(self, width, height, pts, confs):
        '''Calcula las posturas en base a los puntos devueltos por YOLO'''
        if width > (height * 1.2): 
            return "ATENCIÓN Caída detectada (cuerpo en el suelo), ENVIAR AYUDA URGENTEMENTE."
        
        nose_y, nose_c = pts[0][1], confs[0]
        hip_y = (pts[11][1] + pts[12][1]) / 2.0
        hip_c = (confs[11] + confs[12]) / 2.0

        knee_y = (pts[13][1] + pts[14][1]) / 2.0 
        knee_c = (confs[13] + confs[14]) / 2.0

        ankle_y = (pts[15][1] + pts[16][1]) / 2.0 
        ankle_c = (confs[15] + confs[16]) / 2.0

        if hip_c > self.min_confidence and knee_c > self.min_confidence:
            if abs(hip_y - knee_y) < (height * 0.2) or (width > height * 0.6 and width < height * 1.2):
                return "Persona sentada"
            
        if nose_c > self.min_confidence and ankle_c > self.min_confidence:
            if abs(ankle_y - nose_y) < (width * 0.6): 
                return "ATENCIÓN Caída detectada, ENVIAR AYUDA URGENTEMENTE." # (cabeza y pies a altura similar)
            
            elif height > (width * 1.5): 
                return "(ignorar) Todo correcto. Persona de pie o caminando"
        
        if height > (width * 1.3): 
            return "Persona de pie (predicción con poca confianza)" # piernas parcialmente ocultas 
        
        return "Persona sentada o torso visible (predicción con poca confianza)" # piernas parcialmente ocultas 
    
    def check_path(self, path):
        '''Metodo para comprobar que el path es de una imagen que exista'''
        return os.path.isfile(path)

def main(args=None):
    rclpy.init(args=args)
    try:
        rclpy.spin(YoloPerceptionNode())
    except KeyboardInterrupt: pass
    finally: rclpy.shutdown()

if __name__ == '__main__': 
    main()