#!/usr/bin/env python3
import os
import cv2
import rclpy

from .base_capturer import BaseCaptureNode
from hospital_interfaces.msg import LiveCapture

DEFAULT_FPS = 10.0
MAX_FRAMES = 150 # Límite de seguridad de RAM por si el robot se queda parado

VIDEO_TARGET_DISTANCE_METERS =  2.0 # en metros
VIDEO_TARGET_ANGLE = 3.14  # 360 grados en radianes

class VideoCapturerNode(BaseCaptureNode):
    '''Nodo encargado de capturar clips de vídeo fluidos entre los puntos de ruta'''
    
    def __init__(self):
        super().__init__(
            'video_capturer_node', 
            default_distance=VIDEO_TARGET_DISTANCE_METERS,  
            default_angle=VIDEO_TARGET_ANGLE    
        )
        self.declare_parameter("fps", DEFAULT_FPS)
        
        self.frame_buffer = []

        # Timer para muestrear frames sin bloquear el callback de la cámara
        #fps = self.get_parameter("fps").value
        #timer_period = 1.0 / fps
        #self.record_timer = self.create_timer(timer_period, self.record_frame)

        self.get_logger().info("Video Capturer Node Listo")

    def reset_state(self):
        '''Limpia la memoria del buffer al empezar una vuelta nueva'''
        self.frame_buffer.clear()
        
    """def record_frame(self):
        '''Añade frames al buffer a la velocidad exacta de los FPS deseados'''
        if self.current_dir and self.last_image is not None:
            cv_image = self.cv_bridge_replacement()
            cv_image_resized = cv2.resize(cv_image, (640, 480)) # el modelo la reducirá igualmente, así se ahorra espacio y memoria
            self.frame_buffer.append(cv_image_resized)
            
            # Evitar desbordamiento de memoria si el robot se detiene mucho tiempo
            if len(self.frame_buffer) > MAX_FRAMES:
                self.frame_buffer.pop(0) """
    
    def execute_flush(self, zone_name):
        '''Cierra el clip de vídeo actual y lo publica al reportero'''
        capture_mode = 'video'
        
        if len(self.frame_buffer) > 0:
            clip_name, filename = self.save_video()
            
            if filename:
                self.save_metadata(clip_name)
                # Publicar el evento usando el contrato tipado SOTA
                msg = LiveCapture()
                msg.file_path = filename
                msg.zone_name = zone_name if zone_name else self.current_zone_name
                msg.timestamp = float(self.get_clock().now().nanoseconds * 1e-9)
                msg.capture_mode = capture_mode
                
                self.capture_pub.publish(msg)
                self.get_logger().info(f"Clip de vídeo publicado para la zona {zone_name}.")
            
            # Vaciar el buffer en RAM para empezar limpios la siguiente zona
            self.frame_buffer.clear()
            
        return True

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
            self.save_metadata(clip_name) 

            capture_mode = 'video'
            
            msg = LiveCapture()
            msg.file_path = filename
            msg.zone_name = self.current_zone_name
            # Usar el tiempo actual del sistema para el timestamp del mensaje
            msg.timestamp = float(self.get_clock().now().nanoseconds * 1e-9)
            msg.capture_mode = capture_mode
            
            self.capture_pub.publish(msg)
        
        #Vaciada del buffer para empezar el siguiente clip de la ruta
        self.frame_buffer.clear()

    def save_video(self):
        '''Escribe los frames acumulados en un archivo .avi'''
        try:
            clip_name = f"{self.capture_count:06d}.avi"
            filename = os.path.join(self.current_dir, clip_name)
            
            fps = self.get_parameter("fps").value
            height, width, _ = self.frame_buffer[0].shape
            
            # Codec XVID estándar compatible con OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
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
    except Exception as e:
        print(f"\n\n{'='*50}")
        print("[ERROR FATAL DETECTADO EN NODO DE VÍDEO]")
        print(f"{'='*50}\n")
        import traceback
        traceback.print_exc()
        input("\n[El nodo ha crasheado]. Presiona ENTER para cerrar la terminal de gnome...")
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()