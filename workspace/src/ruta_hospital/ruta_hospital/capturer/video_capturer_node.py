#!/usr/bin/env python3
import os
import cv2
import rclpy

from .base_capturer import BaseCaptureNode

DEFAULT_FPS = 10.0
MAX_FRAMES = 150 # Límite de seguridad de RAM por si el robot se queda parado

class VideoCapturerNode(BaseCaptureNode):
    '''Nodo encargado de capturar clips de vídeo fluidos entre los puntos de ruta'''
    
    def __init__(self):
        super().__init__('video_capturer_node')
        self.declare_parameter("fps", DEFAULT_FPS)
        
        self.frame_buffer = []
        self.get_logger().info("Video Capturer Node Listo")

    def reset_state(self):
        '''Limpia la memoria del buffer al empezar una vuelta nueva'''
        self.frame_buffer.clear()
        
    def camera_callback(self, msg):
        '''Sobrescribe el callback del padre para ir guardando frames fluidos'''
        super().camera_callback(msg) # Importante: mantiene actualizados los metadatos base
        
        # Solo acumulamos frames si estamos patrullando (hay directorio asignado)
        if self.current_dir:
            cv_image = self.cv_bridge_replacement()
            self.frame_buffer.append(cv_image)
            
            # Evitar desbordamiento de memoria si el robot se detiene mucho tiempo
            if len(self.frame_buffer) > MAX_FRAMES:
                self.frame_buffer.pop(0)

    def process_and_save_capture(self, cv_image):
        '''Se dispara por odometría. Compila el buffer en un clip y lo guarda'''
        if not self.frame_buffer:
            return
            
        self.check_capture_count()
        clip_name, filename = self.save_video()
        
        if clip_name and os.path.isfile(filename):
            self.save_metadata(clip_name) # Heredado: anota el timestamp y la pose
        
        # Vaciamos el buffer para empezar el siguiente clip de la ruta
        self.frame_buffer.clear()

    def save_video(self):
        '''Escribe los frames acumulados en un archivo .mp4'''
        try:
            clip_name = f"{self.capture_count:06d}.mp4"
            filename = os.path.join(self.current_dir, clip_name)
            
            fps = self.get_parameter("fps").value
            height, width, _ = self.frame_buffer[0].shape
            
            # Codec MP4 estándar compatible con OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(filename, fourcc, fps, (width, height))
            
            for frame in self.frame_buffer:
                video.write(frame)
                
            video.release()
            self.get_logger().info(f"Video guardado en: {filename} ({len(self.frame_buffer)} frames)")
            
            self.capture_count += 1
            return clip_name, filename
            
        except Exception as e:
            self.get_logger().error(f"Error al guardar el clip de video: {e}")
            return None, None
            
def main(args=None):
    rclpy.init(args=args)
    node = VideoCapturerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()