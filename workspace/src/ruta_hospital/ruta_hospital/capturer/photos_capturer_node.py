#!/usr/bin/env python3
import os
import cv2
import rclpy
import numpy as np

from .base_capturer import BaseCaptureNode
from hospital_interfaces.msg import LiveCapture

DEFAULT_SIMILARITY_THRESHOLD = 5.0 # sobre 100 (5.0 = 5%)

class PhotosCapturerNode(BaseCaptureNode):
    '''Nodo encargado de guardar fotos en la ruta del robot'''
    
    def __init__(self):
        super().__init__('photos_node')
        
        self.declare_parameter("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD) # minimo de diferencia con la ultima imagen

        self.last_saved_cv_image = None
        self.sequence_buffer = []
        self.get_logger().info("Photos Node")

    def reset_state(self):
        '''Limpia la memoria de la última foto al empezar una vuelta nueva'''
        self.last_saved_cv_image = None
        self.sequence_buffer.clear()
    
    def is_image_different(self, current_cv_image):
        '''Calcula el Error Cuadratico Medio (MSE) para determinar si la imagen es distinta'''
        if self.last_saved_cv_image is None:
            return True

        gray_current = cv2.cvtColor(current_cv_image, cv2.COLOR_BGR2GRAY)
        gray_last = cv2.cvtColor(self.last_saved_cv_image, cv2.COLOR_BGR2GRAY)

        err = np.sum((gray_current.astype("float") - gray_last.astype("float")) ** 2)
        err /= float(gray_current.shape[0] * gray_current.shape[1])

        max_pixel_value = np.iinfo(gray_current.dtype).max
        max_mse = float(max_pixel_value) ** 2

        mse_percentage = (err / max_mse) * 100.0

        threshold = self.get_parameter("similarity_threshold").value
        return mse_percentage > threshold
    
    def process_and_save_capture(self, cv_image):
        '''Validación y guardado de una imagen'''
        if not self.is_image_different(cv_image):
            self.get_logger().debug("Foto omitida al no superar el límite de diferencia")
            return
        
        self.check_capture_count()
        
        image_name, filename = self.save_photo(cv_image)
        image_exists = os.path.isfile(filename) if filename else False

        if image_name is None or not image_exists:
            return
        
        self.save_metadata(image_name) 
        self.last_saved_cv_image = cv_image

        capture_mode = self.get_parameter('capture_mode').value
        
        if capture_mode == 'image':
            # Streaming instantáneo
            msg = LiveCapture()
            msg.file_path = filename
            msg.zone_name = self.current_zone_name 
            msg.timestamp = self.last_image.header.stamp.sec + (self.last_image.header.stamp.nanosec * 1e-9)
            msg.capture_mode = capture_mode
            self.capture_pub.publish(msg)
            
        elif capture_mode == 'sequence':
            # Guardar en memoria para cuando llegue el trigger
            self.sequence_buffer.append(filename)

    def execute_flush(self, zone_name):
        capture_mode = self.get_parameter('capture_mode').value
        
        if capture_mode == 'sequence' and len(self.sequence_buffer) > 0:
            msg = LiveCapture()
            msg.file_path = ",".join(self.sequence_buffer) # Empaquetar paths
            msg.zone_name = zone_name
            msg.timestamp = float(self.get_clock().now().nanoseconds * 1e-9)
            msg.capture_mode = capture_mode
            
            self.capture_pub.publish(msg)
            self.get_logger().info(f"Secuencia publicada para la zona {zone_name} con {len(self.sequence_buffer)} imágenes.")
            self.sequence_buffer.clear()
            
        return True

    def save_photo(self, cv_image):
        '''Traduce el mensaje de ROS2 a OpenCV y guarda el archivo'''
        try:
            image_name = f"{self.capture_count:06d}.jpg"
            filename = os.path.join(self.current_dir, image_name)
            
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f"Foto guardada en: {filename}")
            
            self.capture_count += 1
            
        except Exception as e:
            self.get_logger().error(f"Error al intentar guardar la foto: {e}")
            image_name,filename = None, None

        finally:    
            return image_name,filename

def main(args=None):
    rclpy.init(args=args)
    node = PhotosCapturerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Saliendo...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()