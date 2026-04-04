import os
from abc import ABC, abstractmethod
from rclpy.node import Node
from hospital_interfaces.srv import AnalyzeActivity

class RagContext:
    def __init__(self,request):
        self.zone_name = getattr(request, 'zone_name', 'Desconocida') # por si en alguna llamada faltan datos
        self.time_str = getattr(request, 'time', 'Desconocida')
        self.expected_activities = getattr(request, 'expected_activities', 'No especificadas')
        self.zone_type = getattr(request, 'zone_type', 'Desconocida')

class BasePerceptionNode(Node, ABC):
    '''Clase abstracta para los nodos de percepción visual'''
    def __init__(self, node_name, start_service=True):
        super().__init__(node_name)
        
        # Servidor del servicio que recibe imágenes y devuelve un reporte
        # de posiciones
        if start_service:
            self.srv = self.create_service(
                AnalyzeActivity, 
                'analyze_image', 
                self.analyze_callback
            )
            self.get_logger().info(f"Servidor de percepción [{node_name}] listo y esperando imágenes.")
        else:
            self.get_logger().info(f"Lógica de [{node_name}] cargada internamente como módulo.")

    def analyze_callback(self, request, response):
        '''Se ejecuta cada vez que recibe una imagen por el servicio'''
        if not self.check_path(request.image_path):
            self.get_logger().error("No se encontró la imagen en la ruta especificada")
            response.report = "Error: No se encontró la imagen en la ruta especificada."
            return response 
                    
        self.get_logger().info(f"Analizando imagen: {os.path.basename(request.image_path)}...")
        
        context = RagContext(request)

        response.report = self.process_image(request.image_path, context)
        return response

    @abstractmethod
    def process_image(self, image_path, context):
        '''Método que implementa cada nodo hijo. Devuelve el reporte en forma de string '''
        pass

    @abstractmethod
    def check_path(self, path):
        '''Metodo para comprobar que el tipo de path es el adecuado para el tipo de perceptor'''
        pass