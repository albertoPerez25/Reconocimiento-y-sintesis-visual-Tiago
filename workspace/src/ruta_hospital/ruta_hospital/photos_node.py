#!/usr/bin/env python3
import os
import math
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge

# Variables de configuracion global
TARGET_DISTANCE_METERS = 1.0 # en metros
SAVE_DIR = "./hospital_photos/"
CAMERA_TOPIC = "/head_front_camera/rgb/image_raw"
ODOM_TOPIC = "/odom"

class PhotoCapturer(Node):
    '''Nodo encargado de guardar fotos en la ruta del robot'''
    
    def __init__(self):
        super().__init__('photo_capturer')
        
        self.bridge = CvBridge()
        self.last_image = None
        self.last_pose = None
        self.accumulated_distance = 0.0
        self.photo_count = 1

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
        '''Crea la carpeta de destino si no se encuentra'''
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    def camera_callback(self, msg):
        '''Asigna a last_image la imagen mas reciente del topic'''
        self.last_image = msg

    def calculate_distance(self, current_pose):
        '''Calcula la distancia euclidiana respecto a la anterior posicion'''
        dx = current_pose.x - self.last_pose.x
        dy = current_pose.y - self.last_pose.y
        return math.sqrt(dx**2 + dy**2)

    def odom_callback(self, msg):
        '''Suma la distancia recorrida y evalua si hay que procesar otra captura'''
        current_pose = msg.pose.pose.position

        if self.last_pose is None:
            self.last_pose = current_pose
            return

        step_distance = self.calculate_distance(current_pose)
        self.accumulated_distance += step_distance
        self.last_pose = current_pose

        if self.accumulated_distance >= TARGET_DISTANCE_METERS:
            if self.last_image is not None:
                self.save_photo()
            
            self.accumulated_distance = 0.0

    def save_photo(self):
        '''Traduce el mensaje de ROS2 a OpenCV y guarda el archivo'''
        try:
            cv_image = self.bridge.imgmsg_to_cv2(self.last_image, "bgr8")
            filename = f"{SAVE_DIR}{self.photo_count:06d}.jpg"
            
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f"Foto guardada en: {filename}")
            
            self.photo_count += 1
            
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