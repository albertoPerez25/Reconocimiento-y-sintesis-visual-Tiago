#!/usr/bin/env python3
import os
import cv2
import rclpy
import numpy as np

from .base_capturer import BaseCaptureNode

DEFAULT_SIMILARITY_THRESHOLD = 25.0

class PhotosCapturerNode(BaseCaptureNode):
    '''Nodo encargado de guardar fotos en la ruta del robot'''
    
    def __init__(self):
        super().__init__('photos_node')
        
        self.declare_parameter("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD) # minimo de diferencia con la ultima imagen

        self.last_saved_cv_image = None
        self.get_logger().info("Photos Node")

    def reset_state(self):
        '''Limpia la memoria de la última foto al empezar una vuelta nueva'''
        self.last_saved_cv_image = None
    
    def is_image_different(self, current_cv_image):
        '''Calcula el Error Cuadratico Medio (MSE) para determinar si la imagen es distinta'''
        if self.last_saved_cv_image is None:
            return True

        gray_current = cv2.cvtColor(current_cv_image, cv2.COLOR_BGR2GRAY)
        gray_last = cv2.cvtColor(self.last_saved_cv_image, cv2.COLOR_BGR2GRAY)

        err = np.sum((gray_current.astype("float") - gray_last.astype("float")) ** 2)
        err /= float(gray_current.shape[0] * gray_current.shape[1])

        threshold = self.get_parameter(DEFAULT_SIMILARITY_THRESHOLD).value
        return err > threshold
    
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