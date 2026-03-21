#!/usr/bin/env python3
import os
import math
import cv2
import csv
import rclpy
import numpy as np
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
#from cv_bridge import CvBridge

from tf2_ros import Buffer, TransformListener
from rcl_interfaces.msg import ParameterDescriptor
from hospital_interfaces.srv import AnalyzeActivity
from rcl_interfaces.msg import SetParametersResult


# Variables de configuracion global
TARGET_DISTANCE_METERS = "target_distance_meters" # en metros
SIMILARITY_THRESHOLD = "similarity_threshold"
CURRENT_SAVE_DIR_PARAM = "current_save_dir"

CAMERA_TOPIC = "/head_front_camera/rgb/image_raw"
ODOM_TOPIC = "/odom"
CSV_FILENAME = "metadata.csv"

class PhotoCapturer(rclpy.node.Node):
    '''Nodo encargado de guardar fotos en la ruta del robot'''
    
    def __init__(self):
        super().__init__('photo_capturer')
        
        # la distancia como parametro para poder cambiarlo en ejecucion
        self.declare_parameter(TARGET_DISTANCE_METERS, 1.0) # (nombre, valor por defecto)
        self.declare_parameter(SIMILARITY_THRESHOLD, 25.0) # minimo de diferencia con la ultima imagen

        # Parámetro dinámico para la carpeta actual
        self.declare_parameter(CURRENT_SAVE_DIR_PARAM, "")

        #self.bridge = CvBridge()
        self.last_image = None
        self.last_pose = None
        self.last_saved_cv_image = None
        self.accumulated_distance = 0.0

        self.current_dir = ""
        self.photo_count = 1

        # para la posición más precisa
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        """ self.setup_directory()
        self.photo_count = self.get_starting_photo_count() """

        self.image_sub = self.create_subscription(
            Image, 
            CAMERA_TOPIC, 
            self.camera_callback, 
            10
        )
        
        self.odom_sub = self.create_subscription(
            Odometry, 
            ODOM_TOPIC, 
            self.odom_callback, 
            10
        )

        self.add_on_set_parameters_callback(self.parameters_callback) # para cambiar el directorio dinámicamente
        self.get_logger().info("Photos Node")

    def parameters_callback(self, params):
        '''Callback que se ejecuta cuando cambian los parámetros del nodo'''        
        for param in params:
            if param.name == CURRENT_SAVE_DIR_PARAM:
                new_dir = param.value
                if new_dir and new_dir != self.current_dir:
                    self.current_dir = new_dir
                    self.setup_directory()
                    self.photo_count = self.get_starting_photo_count()
                    self.last_saved_cv_image = None
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

    def get_starting_photo_count(self):
        '''Busca la ultima foto registrada en el CSV para continuar la numeracion'''
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
    
    def is_image_different(self, current_cv_image):
        '''Calcula el Error Cuadratico Medio (MSE) para determinar si la imagen es distinta'''
        if self.last_saved_cv_image is None:
            return True

        gray_current = cv2.cvtColor(current_cv_image, cv2.COLOR_BGR2GRAY)
        gray_last = cv2.cvtColor(self.last_saved_cv_image, cv2.COLOR_BGR2GRAY)

        err = np.sum((gray_current.astype("float") - gray_last.astype("float")) ** 2)
        err /= float(gray_current.shape[0] * gray_current.shape[1])

        threshold = self.get_parameter(SIMILARITY_THRESHOLD).value
        return err > threshold

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
        
        """if self.accumulated_distance >= target_distance:

            if self.last_image is not None:
                self.accumulated_distance = 0.0
                cv_image = self.bridge.imgmsg_to_cv2(self.last_image, "bgr8")
                
                if self.is_image_different(cv_image):
                    image_name, filename = self.save_photo(cv_image)

                    if image_name is not None and os.path.isfile(filename):
                        self.save_metadata(image_name)
                        self.last_saved_cv_image = cv_image 
                else:
                    self.get_logger().info("Foto omitida al no superar el límite de diferencia")
             """
        
    def try_save_data(self):
        '''Evalua si se cumplen los requisitos para guardar foto y metadatos.'''
        target_distance = self.get_parameter(TARGET_DISTANCE_METERS).value

        if self.accumulated_distance < target_distance:
            return
        
        self.accumulated_distance = 0.0
        
        if self.last_image is None:
            return

        #cv_image = self.bridge.imgmsg_to_cv2(self.last_image, "bgr8") Incompatible con Numpy 2, que es necesario para los modelos
        cv_image = self.cv_bridge_replacement()

        if not self.is_image_different(cv_image):
            self.get_logger().info("Foto omitida al no superar el límite de diferencia")
            return
        
        self.check_photo_count()
        
        image_name, filename = self.save_photo(cv_image)
        image_exists = os.path.isfile(filename)

        if image_name is None or not image_exists:
            return
        
        self.save_metadata(image_name)
        self.last_saved_cv_image = cv_image

    def check_photo_count(self):
        '''Resetea el CSV y el contador si se ha resetado la carpeta de fotos'''
        csv_path = os.path.join(self.current_dir, CSV_FILENAME)
        csv_exists = os.path.isfile(csv_path)
        if not csv_exists:
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['filename', 'timestamp_sec', 'timestamp_nanosec',\
                                    'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])
            self.photo_count = 1

    def save_photo(self, cv_image):
        '''Traduce el mensaje de ROS2 a OpenCV y guarda el archivo'''
        try:
            image_name = f"{self.photo_count:06d}.jpg"
            filename = os.path.join(self.current_dir, image_name)
            
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f"Foto guardada en: {filename}")
            
            self.photo_count += 1
            
        except Exception as e:
            self.get_logger().error(f"Error al intentar guardar la foto: {e}")
            image_name,filename = None, None

        finally:    
            return image_name,filename
    
    def save_metadata(self, image_name):
        '''Obtiene los metadatos (tiempo y posicion) y los guarda en el CSV'''
        try:
            t_sec = self.last_image.header.stamp.sec
            t_nanosec = self.last_image.header.stamp.nanosec

            trans = self.tf_buffer.lookup_transform(
                'map', 
                'base_footprint', 
                rclpy.time.Time() # ultima transformacion disponible
            )
            
            pos = trans.transform.translation
            ori = trans.transform.rotation

            csv_path = os.path.join(self.current_dir, CSV_FILENAME)
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([image_name, t_sec, t_nanosec, pos.x, pos.y, pos.z,\
                                  ori.x, ori.y, ori.z, ori.w])

            self.get_logger().info(f"Guardados metadatos de: {image_name}")

        except Exception as e:
            self.get_logger().error(f"Error al intentar guardar metadatos: {e}")

    def cv_bridge_replacement(self,):
        img_array = np.frombuffer(self.last_image.data, dtype=np.uint8)
        cv_image = img_array.reshape((self.last_image.height, self.last_image.width, 3))
        #cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        return cv_image

def main(args=None):
    rclpy.init(args=args)
    node = PhotoCapturer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Saliendo...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()