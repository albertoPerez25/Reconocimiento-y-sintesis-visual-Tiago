#!/usr/bin/env python3
import time
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import sys
import select
import tty
import termios
import json
from std_srvs.srv import Trigger

PATH_POINTS = [
    [4.83898, 8.27372],
    [8.21112, 6.68955],
    [11.4583, 1.65471],
    [4.47097, 0.75583], # evitar las sillas
    [4.83519, -4.0706], # evitar las sillas
    [11.0001, -3.4900],
    [2.34139, -9.9597],
    [7.14909, -18.077],
    [2.01610, -19.663],
    [1.35232, -27.070], # 10
    [7.02417, -31.315],    
    [4.21443, -36.248], 
    [-4.1522, -41.493],
    [-8.8351, -36.498],
    [-8.8975, -29.067],
    [-3.2156, -25.610], # bug issue #24
    [-8.6355, -16.666],
    [-2.0161, -20.663],
    [-3.5160, -7.2099], # evitar colision esquina
    [-2.7160, -9.7099],
    [-10.646, -2.9706], 
    [-4.8351, -4.0706], # evitar las sillas
    [-4.1000, 1.45583], # evitar las sillas
    [-10.321, 1.68012], 
    [-7.6369, 5.47739],
    [-4.3140, 7.82489],
]

class PatrolNode(rclpy.node.Node):
    def __init__(self):
        super().__init__('patrol_node')

        # Cargar JSON con los puntos de ruta
        self.declare_parameter('route_file_path', 'default_route.json')
        self.route_file_path = self.get_parameter('route_file_path').get_parameter_value().string_value
        self.path_points = self.load_route()

        self.navigator = BasicNavigator()
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Patrol Node Initialized")
        self.route_poses = self.list_to_pose()
        self.report_client = self.create_client(Trigger, '/generate_patrol_report') # Para iniciar el reporte
        self.clean_client = self.create_client(Trigger, '/clean_patrol_data')

    def trigger_report(self):
        '''Llama al servicio de generación de informes al final de una vuelta'''
        self.get_logger().info("Iniciado el informe")
        
        # 3 segundos de espera para ver si el nodo reportero está encendido
        if not self.report_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().warn("El servicio '/generate_patrol_report' no está activo, no se hará el informe")
            self.request_data_cleanup()
            return

        req = Trigger.Request()
        future_response = self.report_client.call_async(req)
                
        #rclpy.spin_until_future_complete(self, future_response) # espera hasta que recibe la respuesta
        completed = self.wait_response(future_response)

        if completed:
            try:
                response = future_response.result()
                if response.success:
                    self.get_logger().info(response.message)
                else:
                    self.get_logger().warn(f"El nodo LLM reportó un problema: {response.message}")
            except Exception as e:
                self.get_logger().error(f"Fallo al invocar el servicio: {e}")
        else:
            self.get_logger().warn("El informe no pudo generarse y/o fué interrumpido")
        
        self.request_data_cleanup()

    def wait_response(self, future_response, timeout_max=5000.0, spin_timeout_sec=0.2):
        '''
        Espera a recibir el informe, permitiendo saltar con ENTER o timeout
        Devuelve True si eterminó, o False si se interrumpió la espera.
        '''
        self.get_logger().info("(s para saltar)")
        waiting_time = 0.0

        while rclpy.ok() and not future_response.done():
            # Spin de medio segundo para no congelar el robot
            rclpy.spin_until_future_complete(self, future_response, timeout_sec=spin_timeout_sec)
            waiting_time += spin_timeout_sec

            # lectura no bloqueante
            key = self.get_key_non_blocking()
            if key and key.lower() == 's':
                sys.stdin.readline() # Limpiar buffer
                return False

            if waiting_time >= timeout_max:
                self.get_logger().error("Timeout superado. Se omitirá el informe")
                return False
        return future_response.done()

    def request_data_cleanup(self):
        '''Pide que detenga el informe y borre las fotos'''
        #self.get_logger().info("Solicitando limpieza de datos")
        if self.clean_client.wait_for_service(timeout_sec=2.0):
            req = Trigger.Request()
            self.clean_client.call_async(req) # Llamada asíncrona para no bloquear a la patrulla
        else:
            self.get_logger().warn("No se pudo alcanzar al servicio de limpieza")

    def load_route(self):
        '''Carga la lista de waypoints desde el archivo JSON'''
        try:
            with open(self.route_file_path, 'r') as f:
                data = json.load(f)
                route = data.get("PATH_POINTS", [])
                self.get_logger().info(f"Ruta cargada exitosamente desde {self.route_file_path}")
                return route
        except Exception as e:
            self.get_logger().error(f"Error cargando el archivo de ruta: {e}")
            return PATH_POINTS

    def list_to_pose(self):
        '''Pasa la lista de waypoints a poses'''
        route_poses = []
        for point in self.path_points:
            pose = self.create_pose(point[0], point[1])
            route_poses.append(pose)
        return route_poses

    def create_pose(self, x, y):
        '''Crea poses neutras'''
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.w = 1.0 # Orientación neutra
        return pose

    def state_check(self, result, index, iteration): 
        '''Devuelve el estado actual/final'''
        if result == TaskResult.SUCCEEDED:
            #time.sleep(2.0) # Pausa breve entre vueltas simulando dar un resumen
            ret = True
        else:
            ret = False
            self.get_logger().warn(f"{iteration+1} fallo(s) intentando llegar al punto {index}")
            if result == TaskResult.CANCELED:
                self.get_logger().warn(" Navegacion cancelada")
            elif result == TaskResult.FAILED:
                self.get_logger().error(f" Intento {iteration+1} fallido")
            else:
                self.get_logger().error(f" Fallo desconocido: {result}") # Usar f-string
        return ret

    def execute_rescue(self, backup_dist=0.5, backup_speed=0.2):
        '''Saca al robot de un atasco dando marcha atrás y limpiando la memoria de obstáculos'''
        self.get_logger().info("\n [Rescate] Intentando recuperar la navegación...")
        
        # Marcha atrás para separarse del obstáculo
        self.navigator.backup(backup_dist=backup_dist, backup_speed=backup_speed)
        while not self.navigator.isTaskComplete():
            time.sleep(1.0)
            
        self.navigator.clearAllCostmaps()   # Para eliminar obstáculos
        time.sleep(1.5)                # Para que el sensor láser se ajuste

    def get_key_non_blocking(self):
        '''Lee una tecla sin pulsar Enter asíncronamente'''
        try:
            file_descriptor_stdin = sys.stdin.fileno()
            old_settings = termios.tcgetattr(file_descriptor_stdin) # en caso de un crasheo, restaurar
            try:
                tty.setcbreak(file_descriptor_stdin) # modo cbreak no necesita pulsar enter
                if select.select([sys.stdin], [], [], 0.2)[0]: # input en cada instante, asíncrono
                    return sys.stdin.read(1)
            finally:
                termios.tcsetattr(file_descriptor_stdin, termios.TCSADRAIN, old_settings) # restaura terminal
        except Exception:
            pass # Falla silenciosamente si la terminal no soporta lectura cruda
        return None

    def navigate_to_waypoint(self, pose, current_index, total_points, max_retries=2):
        '''Intenta llegar a un waypoint. Si falla, ejecuta el rescate y lo vuelve a intentar'''
        for it in range(max_retries):
            self.navigator.goToPose(pose)

            while not self.navigator.isTaskComplete():
                # El feedback de goToPose no tiene current_waypoint
                print(f"Punto actual: {current_index}/{total_points} | Intento: {it + 1}/{max_retries} | (s) Saltar", end='\r')
                
                key = self.get_key_non_blocking()
                if key and key.lower() == 's':
                    self.get_logger().warn(f"\n [Salto] Punto {current_index} omitido por el usuario")
                    self.navigator.cancelTask()
                    time.sleep(0.2) # Que le de tiempo a procesarlo
                    return True # para que no salte error

            result = self.navigator.getResult()
            
            if self.state_check(result,current_index,it):
                """self.navigator.backup(backup_dist=0.1, backup_speed=0.2)
                while not self.navigator.isTaskComplete():
                    time.sleep(1.0) """
                return True
                
            if it < max_retries - 1:
                self.execute_rescue() 

        self.get_logger().info("Pasando al siguiente punto")
        return False

    def do_patrol_iteration(self):
        '''Reemplaza followWaypoints por un bucle iterativo para intercalar la marcha atrás y manejo de atascos'''
        total_points = len(self.route_poses)
        
        for i, pose in enumerate(self.route_poses):
            current_index = i + 1
            
            self.navigate_to_waypoint(pose, current_index, total_points, max_retries=2) 
            #self.trigger_report()

    def run_patrol(self):
        '''Bucle infinito de iteraciones de patrullas al hospital'''
        self.get_logger().info(f"Ruta cargada con {len(self.route_poses)} puntos")
        iteration = 1
        while rclpy.ok():
            self.get_logger().info(f"\nVUELTA Nº {iteration}")
            self.do_patrol_iteration()
            self.trigger_report()
            iteration += 1
            break

def main(args=None):
    rclpy.init(args=args)
    patrol_node = PatrolNode()
    
    try:
        patrol_node.run_patrol()
    except KeyboardInterrupt: # Para poder pararlo más fácil
        patrol_node.navigator.cancelTask()
        patrol_node.get_logger().info('Ruta cancelada')
    finally:
        patrol_node.navigator.lifecycleShutdown()
        patrol_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
