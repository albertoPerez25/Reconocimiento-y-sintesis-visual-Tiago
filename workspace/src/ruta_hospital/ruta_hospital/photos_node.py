#!/usr/bin/env python3
import os
import math
import cv2
import csv
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge

from tf2_ros import Buffer, TransformListener
#from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

# Variables de configuracion global
TARGET_DISTANCE_METERS = "target_distance_meters" # en metros
SAVE_DIR = "./hospital_photos/"
CAMERA_TOPIC = "/head_front_camera/rgb/image_raw"
ODOM_TOPIC = "/odom"
CSV_FILENAME = "metadata.csv"

class PhotoCapturer(Node):
    '''Nodo encargado de guardar fotos en la ruta del robot'''
    
    def __init__(self):
        super().__init__('photo_capturer')
        
        # la distancia como parametro para poder cambiarlo en ejecucion
        self.declare_parameter(TARGET_DISTANCE_METERS, 1.0) # (nombre, valor por defecto)

        self.bridge = CvBridge()
        self.last_image = None
        self.last_pose = None
        self.accumulated_distance = 0.0
        self.photo_count = 1

        # para la posición más precisa
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.setup_directory()

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

        self.get_logger().info("Photos Node")

    def setup_directory(self):
        '''Crea la carpeta de destino y el archivo CSV si no se encuentran'''
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        csv_path = os.path.join(SAVE_DIR, CSV_FILENAME)
        file_exists = os.path.isfile(csv_path)

        # Crear el CSV con cabeceras si es la primera vez
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['filename', 'timestamp_sec', 'timestamp_nanosec',\
                                  'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])

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
        current_pose = msg.pose.pose

        if self.last_pose is None:
            self.last_pose = current_pose
            return

        step_distance = self.calculate_distance(current_pose)
        self.accumulated_distance += step_distance
        self.last_pose = current_pose

        target_distance = self.get_parameter(TARGET_DISTANCE_METERS).value

        if self.accumulated_distance >= target_distance:
            if self.last_image is not None:
                image_name,filename = self.save_photo()

                if image_name is not None and os.path.isfile(filename):
                    self.save_metadata(image_name)
            
            self.accumulated_distance = 0.0

    def save_photo(self):
        '''Traduce el mensaje de ROS2 a OpenCV y guarda el archivo'''
        try:
            cv_image = self.bridge.imgmsg_to_cv2(self.last_image, "bgr8")
            image_name = f"{self.photo_count:06d}.jpg"
            filename = f"{SAVE_DIR}{image_name}.jpg"
            
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f"Foto guardada en: {filename}")
            
            self.photo_count += 1
            
        except Exception as e:
            self.get_logger().error(f"Error al intentar guardar la foto: {e}")
            image_name,filename = None

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

            csv_path = os.path.join(SAVE_DIR, CSV_FILENAME)
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([image_name, t_sec, t_nanosec, pos.x, pos.y, pos.z,\
                                  ori.x, ori.y, ori.z, ori.w])

            self.get_logger().info(f"Guardados metadatos de: {image_name}")

        except Exception as e:
            self.get_logger().error(f"Error al intentar guardar la foto: {e}")

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