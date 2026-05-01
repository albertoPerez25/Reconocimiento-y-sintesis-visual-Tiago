import os
import math
import csv
import rclpy
import numpy as np
from abc import ABC, abstractmethod
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener
from rcl_interfaces.msg import SetParametersResult

#from cv_bridge import CvBridge

# Variables de configuracion global compartidas
TARGET_DISTANCE_METERS =  0.2# en metros
CURRENT_SAVE_DIR_PARAM = ""
CAMERA_TOPIC = "/head_front_camera/rgb/image_raw"
ODOM_TOPIC = "/odom"
CSV_FILENAME = "metadata.csv"

class BaseCaptureNode(rclpy.node.Node, ABC):
    '''Clase abstracta encargada de la lógica común para capturar datos visuales (fotos/vídeo) en la ruta'''
    
    def __init__(self, node_name):
        super().__init__(node_name)
        
        # la distancia como parametro para poder cambiarlo en ejecucion
        self.declare_parameter("target_distance_meters", TARGET_DISTANCE_METERS) # (nombre, valor por defecto)
        self.declare_parameter("current_save_dir", CURRENT_SAVE_DIR_PARAM) # Parámetro dinámico para la carpeta actual

        self.last_image = None
        self.last_pose = None
        self.accumulated_distance = 0.0

        self.current_dir = ""
        self.capture_count = 1

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.image_sub = self.create_subscription(Image, CAMERA_TOPIC, self.camera_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, ODOM_TOPIC, self.odom_callback, 10)

        self.add_on_set_parameters_callback(self.parameters_callback)
        self.get_logger().info(f"Base Capture Node [{node_name}] iniciado")

    def parameters_callback(self, params):
        '''Callback que se ejecuta cuando cambian los parámetros del nodo'''        
        for param in params:
            if param.name == CURRENT_SAVE_DIR_PARAM:
                new_dir = param.value
                if new_dir and new_dir != self.current_dir:
                    self.current_dir = new_dir
                    self.setup_directory()
                    self.capture_count = self.get_starting_capture_count()
                    self.reset_state() # Hook para resetear variables del hijo (como la última foto tomada)
                    self.accumulated_distance = 0.0
        
        return SetParametersResult(successful=True)

    def setup_directory(self):
        '''Crea la carpeta de destino y el archivo CSV si no se encuentran'''
        if not self.current_dir:
            return 1
        
        if not os.path.exists(self.current_dir):
            os.makedirs(self.current_dir)

        csv_path = os.path.join(self.current_dir, CSV_FILENAME)
        file_exists = os.path.isfile(csv_path)

        # Crear el CSV con cabeceras si es la primera vez
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['filename', 'timestamp_sec', 'timestamp_nanosec',\
                                  'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])

    def get_starting_capture_count(self):
        '''Busca la ultima captura registrada en el CSV para continuar la numeracion'''
        if not self.current_dir: 
            return 1

        csv_path = os.path.join(self.current_dir, CSV_FILENAME)
        
        if not os.path.isfile(csv_path):
            return 1
            
        try:
            with open(csv_path, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                csv_rows = list(csv_reader)
                
                if len(csv_rows) <= 1:
                    return 1
                    
                last_filename = csv_rows[-1][0] 
                num = int(last_filename.split('.')[0])
                return num + 1
                
        except Exception as e:
            self.get_logger().warn(f"No se pudo leer el CSV, iniciando en 1: {e}")
            return 1

    def camera_callback(self, msg):
        '''Asigna a last_image la imagen mas reciente del topic'''
        self.last_image = msg

    def calculate_distance(self, current_pose):
        '''Calcula la distancia euclidiana respecto a la anterior posicion'''
        dx = current_pose.position.x - self.last_pose.position.x
        dy = current_pose.position.y - self.last_pose.position.y
        return math.sqrt(dx**2 + dy**2)

    def odom_callback(self, msg):
        '''Suma la distancia recorrida y evalua si hay que procesar otra captura'''
        # Si no hay directorio asignado no procesa la odometría
        if not self.current_dir:
            return

        current_pose = msg.pose.pose

        if self.last_pose is None:
            self.last_pose = current_pose
            return

        step_distance = self.calculate_distance(current_pose)
        self.accumulated_distance += step_distance
        self.last_pose = current_pose

        self.try_save_data()
        
    def try_save_data(self):
        '''Evalua si se cumplen los requisitos para guardar foto y metadatos.'''
        target_distance = self.get_parameter(TARGET_DISTANCE_METERS).value

        if self.accumulated_distance < target_distance:
            return
        
        self.accumulated_distance = 0.0
        
        if self.last_image is None:
            return

        cv_image = self.cv_bridge_replacement()
        
        # Delegamos la responsabilidad de guardar la foto/vídeo al nodo hijo
        self.process_and_save_capture(cv_image)

    def check_capture_count(self):
        '''Resetea el CSV y el contador si se ha reseteado la carpeta de capturas'''
        csv_path = os.path.join(self.current_dir, CSV_FILENAME)
        csv_exists = os.path.isfile(csv_path)
        if not csv_exists:
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['filename', 'timestamp_sec', 'timestamp_nanosec',\
                                    'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])
            self.capture_count = 1

    def save_metadata(self, file_name):
        '''Obtiene los metadatos (tiempo y posicion) y los guarda en el CSV'''
        try:
            t_sec = self.last_image.header.stamp.sec
            t_nanosec = self.last_image.header.stamp.nanosec

            trans = self.tf_buffer.lookup_transform(
                'map', 
                'base_footprint', 
                rclpy.time.Time() 
            )
            
            pos = trans.transform.translation
            ori = trans.transform.rotation

            csv_path = os.path.join(self.current_dir, CSV_FILENAME)
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([file_name, t_sec, t_nanosec, pos.x, pos.y, pos.z,\
                                  ori.x, ori.y, ori.z, ori.w])

            self.get_logger().info(f"Guardados metadatos de: {file_name}")

        except Exception as e:
            self.get_logger().error(f"Error al intentar guardar metadatos: {e}")

    def cv_bridge_replacement(self):
        '''reemplazo a cv_bridge '''
        img_array = np.frombuffer(self.last_image.data, dtype=np.uint8)
        cv_image = img_array.reshape((self.last_image.height, self.last_image.width, 3))
        #cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        return cv_image

    @abstractmethod
    def process_and_save_capture(self, cv_image):
        '''Lógica de guardado específica a implementar por fotos o clips de vídeo'''
        pass

    def reset_state(self):
        '''Permite al hijo resetear sus variables de memoria cuando cambia el directorio'''
        pass