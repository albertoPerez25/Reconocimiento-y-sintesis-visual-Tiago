#!/usr/bin/env python3
import cv2
import rclpy
import os
from ultralytics import YOLO

# Servicio personalizado para comunicación entre LLM y Yolo
from ruta_hospital.perception.base_perception import BasePerceptionNode 

#YOLO_MODEL = "yolov8n-pose.pt"
YOLO_MODEL = "yolo26n-pose.pt"
MIN_CONFIDENCE = 0.5

class YoloPerceptionNode(BasePerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('yolo_perception_node',start_service=start_service)
        self.model = YOLO(YOLO_MODEL)
        self.get_logger().info(f"Modelo {YOLO_MODEL} cargado")

    def process_image(self, image_path: str) -> str:
        '''Procesa la imagen y devuelve el reporte en forma de string '''
        image = cv2.imread(image_path)
        if image is None:
            return "Error: No se pudo leer la imagen"

        results = self.model(image, verbose=False)
        result = results[0]

        if len(result.boxes) == 0:
            return "Estado: No se han detectado personas"

        report = f"Estado: Se han detectado {len(result.boxes)} persona(s)\n"

        for i, (box, keypoints) in enumerate(zip(result.boxes, result.keypoints)):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1 
            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()
            posture = self.calculate_posture(width, height, pts, confs)
            report += f" - Persona {i+1}: {posture}\n"

        return report

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

        if hip_c > MIN_CONFIDENCE and knee_c > MIN_CONFIDENCE:
            if abs(hip_y - knee_y) < (height * 0.2) or (width > height * 0.6 and width < height * 1.2):
                return "(ignorar) Todo correcto. Persona sentada"
            
        if nose_c > MIN_CONFIDENCE and ankle_c > MIN_CONFIDENCE:
            if abs(ankle_y - nose_y) < (width * 0.6): 
                return "ATENCIÓN Caída detectada (cabeza y pies a altura similar), ENVIAR AYUDA URGENTEMENTE."
            
            elif height > (width * 1.5): 
                return "(ignorar) Todo correcto. Persona de pie o caminando"
        
        if height > (width * 1.3): 
            return "(ignorar) Todo correcto. Persona de pie (piernas parcialmente ocultas o predicción con poca confianza)"
        
        return "(ignorar) Todo correcto. Persona sentada o torso visible (piernas parcialmente ocultas o predicción con poca confianza)"
    
    def check_path(self, path):
        '''Metodo para comprobar que el path es de una imagen que exista'''
        return os.path.isfile(path)

def main(args=None):
    rclpy.init(args=args)
    try:
        rclpy.spin(YoloPerceptionNode())
    except KeyboardInterrupt: pass
    finally: rclpy.shutdown()

if __name__ == '__main__': main()