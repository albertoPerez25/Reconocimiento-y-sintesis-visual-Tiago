import os
import json
from abc import abstractmethod
from ruta_hospital.perception.base_perception import BasePerceptionNode

class BasePositionPerceptionNode(BasePerceptionNode):
    '''Clase abstracta para los estimadores de posición (YOLO, PoseNet, etc.)'''
    def __init__(self, node_name, start_service=True):
        super().__init__(node_name, start_service=start_service)

    def analyze_callback(self, request, response):
        '''Sobreescribe el callback porque los estimadores de posición no usan RagContext'''
        if not self.check_path(request.image_path):
            self.get_logger().error("No se encontró la imagen en la ruta especificada")
            response.report = "Error: No se encontró la imagen en la ruta especificada."
            return response 
                    
        self.get_logger().info(f"Analizando posición en: {os.path.basename(request.image_path)}...")
        
        # Funciona en modo independiente (no híbrido), no debe incluir las detecciones
        report_dict = self.process_image(request.image_path, include_raw_detections=False)
        response.report = json.dumps(report_dict, ensure_ascii=False)
        return response

    @abstractmethod
    def process_image(self, image_path, include_raw_detections=False):
        '''
        Método que implementa cada nodo hijo. Devuelve el reporte en forma de string 
        '''
        pass