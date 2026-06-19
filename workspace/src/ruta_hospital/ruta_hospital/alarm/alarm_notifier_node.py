#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import subprocess
from hospital_interfaces.msg import Alarm

class AlarmNotifierNode(Node):
    def __init__(self):
        super().__init__('alarm_notifier_node')
        
        # Nos suscribimos al topic que dispara el reportero
        self.subscription = self.create_subscription(
            Alarm,
            '/hospital/alarms',
            self.alarm_callback,
            10
        )
        self.get_logger().info("Nodo Notificador de GNOME iniciado. Esperando alertas...")

    def alarm_callback(self, msg):
        '''
        Se ejecuta instantáneamente al recibir un mensaje en el topic de alarmas.
        Usa el comando nativo de Ubuntu para lanzar un pop-up crítico.
        '''
        self.get_logger().warn(f"Alarma recibida de {msg.zone_name}. Notificando al SO...")
        
        titulo = f"🚨 ALERTA CRÍTICA: {msg.zone_name}"
        cuerpo = f"{msg.description}\n\nPor favor, revise el área inmediatamente."
        
        try:
            # notify-send es el gestor de notificaciones de Ubuntu/GNOME
            # -u critical : Fuerza a que la notificación no desaparezca sola
            # -i dialog-warning : Usa el icono de peligro nativo del sistema
            subprocess.run([
                "notify-send", 
                "-u", "critical", 
                "-i", "dialog-warning", 
                titulo, 
                cuerpo
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Fallo al enviar la notificación de escritorio: {e}")
        except FileNotFoundError:
            self.get_logger().error("El comando 'notify-send' no está instalado en este sistema.")

def main(args=None):
    rclpy.init(args=args)
    node = AlarmNotifierNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()