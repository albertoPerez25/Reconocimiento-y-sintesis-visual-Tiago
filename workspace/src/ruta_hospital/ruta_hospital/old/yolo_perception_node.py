#!/usr/bin/env python3
import cv2
import rclpy
from rclpy.node import Node
from ultralytics import YOLO

# Servicio personalizado para comunicación entre LLM y Yolo
from hospital_interfaces.srv import AnalyzeActivity

#YOLO_MODEL = "yolov8n-pose.pt"
YOLO_MODEL = "yolo26n-pose.pt"
MIN_CONFIDENCE = 0.5

class YoloPerceptionNode(Node):
    def __init__(self):
        super().__init__('yolo_perception_node')
        
        self.model = YOLO(YOLO_MODEL)
        self.get_logger().info(f"Modelo {YOLO_MODEL} cargado")
        
        # Servidor del servicio que recibe imágenes y devuelve un reporte
        # de posiciones
        self.srv = self.create_service(
            AnalyzeActivity, 
            'analyze_image', 
            self.analyze_callback
        )
        self.get_logger().info("Servidor de percepción YOLO listo y esperando imágenes")

    def analyze_callback(self, request, response):
        '''Se ejecuta cada vez que recibe una imagen por el servicio'''

        image = cv2.imread(request.image_path)
        if image is None:
            response.report = "Error: No se pudo leer la imagen"
            return response

        results = self.model(image, verbose=False)
        result = results[0]

        if len(result.boxes) == 0:
            response.report = "Estado: No se han detectado personas"
            return response

        report = f"Estado: Se han detectado {len(result.boxes)} persona(s)\n"

        for i, (box, keypoints) in enumerate(zip(result.boxes, result.keypoints)):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1 
            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()

            posture = self.calculate_posture(width, height, pts, confs)
            report += f" - Persona {i+1}: {posture}\n"

        response.report = report
        return response

    def calculate_posture(self, width, height, pts, confs):
        '''Calcula las posturas en base a los puntos devueltos por YOLO'''

        if width > (height * 1.2):
            return "Posible caída detectada (cuerpo en horizontal en el suelo)"

        nose_y = pts[0][1]
        nose_c = confs[0]

        hip_y = (pts[11][1] + pts[12][1]) / 2.0
        hip_c = (confs[11] + confs[12]) / 2.0

        knee_y = (pts[13][1] + pts[14][1]) / 2.0
        knee_c = (confs[13] + confs[14]) / 2.0

        ankle_y = (pts[15][1] + pts[16][1]) / 2.0 
        ankle_c = (confs[15] + confs[16]) / 2.0

        if hip_c > MIN_CONFIDENCE and knee_c > MIN_CONFIDENCE:
            thigh_vertical_dist = abs(hip_y - knee_y)
            if thigh_vertical_dist < (height * 0.2) or (width > height * 0.6 and width < height * 1.2):
                return "Persona sentada"

        if nose_c > MIN_CONFIDENCE and ankle_c > MIN_CONFIDENCE:
            vertical_diff = abs(ankle_y - nose_y)
            if vertical_diff < (width * 0.6):
                return "Posible caída detectada (cabeza y pies a altura similar)"
            elif height > (width * 1.5):
                return "Persona de pie o caminando"

        if height > (width * 1.3):
            return "Persona de pie (piernas parcialmente ocultas o predicción con poca confianza)"
        return "Persona sentada o torso visible (piernas parcialmente ocultas o predicción con poca confianza)"

def main(args=None):
    rclpy.init(args=args)
    node = YoloPerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()