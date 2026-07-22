#!/usr/bin/env python3
import time
import rclpy
import os
import subprocess # para lanzar el proceso del chatbot

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.action import ActionClient
from hospital_interfaces.action import GenerateReport
from ruta_hospital.chatbot import chatbot_web

from rcl_interfaces.srv import SetParameters # Para cambiar el dir del photos_node
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType

from ruta_hospital.navigation.utils.route_parser_utils import load_route,list_to_pose
from ruta_hospital.navigation.utils.file_utils import clean_all_orphan_folders, get_next_available_folder
from ruta_hospital.utils.commons.file_utils import delete_folder
from ruta_hospital.utils.commons.terminal_utils import get_key_non_blocking
from ament_index_python.packages import get_package_share_directory

from hospital_interfaces.srv import FlushZoneData
from ruta_hospital.utils.shared.semantic_map_utils import get_zone_name, load_semantic_map

DEFAULT_PATH_POINTS = [
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

PKG_DIR = get_package_share_directory('ruta_hospital')

DEFAULT_WAYPOINTS_PATH = os.path.join(PKG_DIR, "config", "route_waypoints.json")
REPO_ROOT_DIR = os.path.abspath(os.path.join(PKG_DIR, "..", "..", "..", "..", ".."))
DEFAULT_PHOTOS_DIR = os.path.join(REPO_ROOT_DIR, "datasets", "hospital_photos", "")

if not os.path.exists(os.path.join(REPO_ROOT_DIR, "datasets")):
    DEFAULT_PHOTOS_DIR = os.path.join(os.path.expanduser("~"), "ruta_hospital_datasets", "hospital_photos", "")

DEFAULT_KEEP_TEMP_FOLDERS = False
DEFAULT_CAPTURER_NAME = "photos_node"
DEFAULT_USE_RERANKER = False # también se puede configurar con una variable de entorno

class PatrolNode(rclpy.node.Node):
    def __init__(self):
        super().__init__('patrol_node')

        # Cargar JSON con los puntos de ruta
        self.declare_parameter('route_file_path', DEFAULT_WAYPOINTS_PATH)
        self.route_file_path = self.get_parameter('route_file_path').get_parameter_value().string_value

        # Directorio raíz para las subcarpetas
        self.declare_parameter('base_photos_dir', DEFAULT_PHOTOS_DIR)
        self.base_photos_dir = self.get_parameter('base_photos_dir').get_parameter_value().string_value

        self.declare_parameter('keep_temp_folders', DEFAULT_KEEP_TEMP_FOLDERS)
        self.keep_temp_folders = self.get_parameter('keep_temp_folders').get_parameter_value().bool_value

        self.declare_parameter('capturer_node_name', DEFAULT_CAPTURER_NAME)
        self.capturer_node_name = self.get_parameter('capturer_node_name').get_parameter_value().string_value

        self.declare_parameter('use_reranker', DEFAULT_USE_RERANKER)
        self.use_reranker = self.get_parameter('use_reranker').get_parameter_value().bool_value

        self.path_points = load_route(self.route_file_path, DEFAULT_PATH_POINTS, self.get_logger())

        self.navigator = BasicNavigator()
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Nodo patrulla iniciado")
        self.route_poses = list_to_pose(self.path_points, self.navigator.get_clock())

        self.report_action_client = ActionClient(self, GenerateReport, 'generate_patrol_report')     
        self.param_client = self.create_client(SetParameters, f'/{self.capturer_node_name}/set_parameters')
        self.flush_cli = self.create_client(FlushZoneData, '/capturer/flush_zone')
        self.current_folder_path = ""
        self.current_zone = "Desconocida"
        self.last_zone_change_time = 0.0
        self.debounce_duration = 2.0 # Segundos de "ceguera" temporal tras un cambio de zona para evitar ping-pong
        self.chatbot_process = None

        default_map_path = os.path.join(PKG_DIR, 'config', 'semantic_map.json')
        self.hospital_zones, self.reception_zone = load_semantic_map(default_map_path, self.get_logger())

    def set_capturer_zone(self, zone_name):
        '''Avisa al nodo capturador de la zona actual en tiempo real para el modo imagen'''
        if not self.param_client.wait_for_service(timeout_sec=1.0):
            return
            
        req = SetParameters.Request()
        param = Parameter()
        param.name = "current_zone"
        param.value = ParameterValue(type=ParameterType.PARAMETER_STRING, string_value=zone_name)
        req.parameters.append(param)
        self.param_client.call_async(req)

    def trigger_zone_flush(self, zone_name):
        '''Llama al capturador asíncronamente para que envíe sus buffers de la zona indicada'''
        if not self.flush_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Servicio de flush no disponible. Ignorando...")
            return

        req = FlushZoneData.Request()
        req.zone_name = zone_name
        
        # Llamada asíncrona (Fire-and-Forget) controlada semánticamente
        self.flush_cli.call_async(req)
        self.get_logger().debug(f"Trigger de fin de zona enviado para: {zone_name}")

    def set_capturer_folder(self, folder_path):
        '''Avisa al photos_node de la nueva carpeta usando SetParameters'''
        if not self.param_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn("No se pudo conectar con el nodo foto")
            return
            
        req = SetParameters.Request()
        param = Parameter()
        param.name = "current_save_dir"
        param.value = ParameterValue(type=ParameterType.PARAMETER_STRING, string_value=folder_path)
        req.parameters.append(param)
        self.param_client.call_async(req)
        self.current_folder_path = folder_path

    def trigger_report(self):
        '''Llama al servicio de generación de informes al final de una vuelta'''
        self.get_logger().info("Iniciado el informe")
        
        # 3 segundos de espera para ver si el nodo reportero está encendido
        if not self.report_action_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().warn("El servidor de acción '/generate_patrol_report' no está activo.")
            if not self.keep_temp_folders:
                delete_folder(self.current_folder_path, self.get_logger())
            return

        goal_msg = GenerateReport.Goal()
        goal_msg.folder_path = self.current_folder_path

        send_goal_future = self.report_action_client.send_goal_async(goal_msg, feedback_callback=self.report_feedback_callback)
        send_goal_future.add_done_callback(lambda future: self.goal_response_callback(future, self.current_folder_path))

    def goal_response_callback(self, future, folder_to_clean):
        '''Se ejecuta cuando el servidor de acción responde si acepta o rechaza la meta'''
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('La meta fue rechazada por el reportero, no se generará informe')
            if not self.keep_temp_folders:
                delete_folder(folder_to_clean, self.get_logger())
            return

        self.get_logger().info('Generando informe...')
        self.active_goal_handle = goal_handle # En caso de ser necesario cancelarlo luego

        # Callback para cuando la meta termine definitivamente
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(lambda fut: self.get_result_callback(fut, folder_to_clean))

    def report_feedback_callback(self, feedback_msg):
        '''Recibe y muestra el progreso temporal del reportero'''
        feedback = feedback_msg.feedback
        self.get_logger().info(f"[Reportero]: Zona: {feedback.current_zone} ({feedback.percentage_complete:.1f}%)")

    def get_result_callback(self, future, folder_to_clean):
        '''Se ejecuta cuando el reportero ha terminado y respondido con el informe'''
        result = future.result().result
        status = future.result().status

        # Estado 4 (SUCCEEDED) en rclpy.action significa éxito
        if status == 4 and result.success:
            self.get_logger().info(f"\nINFORME COMPLETADO \n{result.final_report}\n")
        else:
            self.get_logger().error("ERROR generando el informe en el reportero: {result.final_report}")
            
        if not self.keep_temp_folders:
            self.get_logger().debug(f"Limpiando datos de sesión: {folder_to_clean}")
            delete_folder(folder_to_clean, self.get_logger())
        else:
            self.get_logger().debug(f"Modo keep_temp_folders ON. Se conserva: {folder_to_clean}")
        self.active_goal_handle = None # Limpiar referencia

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

    def navigate_to_waypoint(self, pose, current_index, total_points, max_retries=2):
        '''Intenta llegar a un waypoint. Si falla, ejecuta el rescate y lo vuelve a intentar'''
        for it in range(max_retries):
            self.navigator.goToPose(pose)

            while not self.navigator.isTaskComplete():

                feedback = self.navigator.getFeedback()
                if feedback:
                    x = feedback.current_pose.pose.position.x
                    y = feedback.current_pose.pose.position.y
                    new_zone = get_zone_name([x, y], self.hospital_zones, self.reception_zone)
                    
                    if new_zone != self.current_zone and new_zone != "Desconocida":
                        if time.time() - self.last_zone_change_time > self.debounce_duration:
                            if self.current_zone != "Desconocida":
                                # Añadido \n para que no pise la barra de tu interfaz de terminal
                                self.get_logger().info(f"\nTransición detectada: Abandonando {self.current_zone} -> Entrando a {new_zone}")
                                self.trigger_zone_flush(self.current_zone)
                            
                            self.current_zone = new_zone
                            self.last_zone_change_time = time.time()
                            self.set_capturer_zone(new_zone)

                # El feedback de goToPose no tiene current_waypoint
                nav_msg = f"Ruta: {current_index}/{total_points} | Intento: {it + 1}/{max_retries} | [s] Saltar [d] Cancelar inf. [c] Chat"
                
                print(f"\r\033[K{nav_msg}", end='', flush=True)

                key = get_key_non_blocking()
                time.sleep(0.01)
                if key and key.lower() == 's':
                    self.get_logger().warn(f"\n [Salto] Punto {current_index} omitido por el usuario")
                    self.navigator.cancelTask()

                    time.sleep(0.2) # Que le de tiempo a procesarlo
                    return True # para que no salte error

                elif key and key.lower( ) == 'd' and hasattr(self, 'active_goal_handle') and self.active_goal_handle:
                    self.get_logger().warn("[Informe] Cancelado el informe en curso")
                    self.active_goal_handle.cancel_goal_async()

                elif key and key.lower() == 'c':
                    print("\n") # Salto de línea para no pisar el log
                    self.get_logger().info("Abriendo interfaz web del Chatbot (Streamlit)...")
                    
                    if not hasattr(self, 'chatbot_process') \
                        or self.chatbot_process is None \
                        or self.chatbot_process.poll() is not None:
                        try:
                            chatbot_script = chatbot_web.__file__
                            env_config = os.environ.copy()
                            env_config["USE_RERANKER"] = str(self.use_reranker)
                            self.chatbot_process = subprocess.Popen(['streamlit', 'run', chatbot_script], env=env_config)
                        except ImportError:
                            self.get_logger().warn(f"Error al lanzar el proceso del chatbot: No se pudo importar el proceso")
                    else:
                        self.get_logger().warn("El chatbot ya se está ejecutando")
                        
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

        # Reiniciar el estado para evitar arrastrar la última zona de la vuelta anterior
        self.current_zone = "Desconocida"
        self.last_zone_change_time = 0.0 #time.time()
        
        for i, pose in enumerate(self.route_poses):
            current_index = i + 1
            
            success = self.navigate_to_waypoint(pose, current_index, total_points, max_retries=2) 

            #self.trigger_report()
        
        # Un último flush explícito de la zona 
        # en la que el robot se haya detenido para que no se pierdan esos datos.
        if self.current_zone != "Desconocida":
            self.get_logger().info(f"\nRuta terminada. Vaciando buffers de la última zona ({self.current_zone}).")
            self.trigger_zone_flush(self.current_zone)

    def run_patrol(self):
        '''Bucle infinito de iteraciones de patrullas al hospital'''
        self.get_logger().info(f"Ruta cargada con {len(self.route_poses)} puntos")
        iteration = 1
        
        if not self.keep_temp_folders:
            clean_all_orphan_folders(self.base_photos_dir, self.get_logger())
        else:
            self.get_logger().warn(f"Modo keep_temp_folders ON. Las carpetas de capturas NO se borrarán")
            
        while rclpy.ok():
            self.get_logger().info(f"\nVUELTA Nº {iteration}")

            new_folder = get_next_available_folder(self.base_photos_dir, self.get_logger())
            if not new_folder:
                time.sleep(5)
                continue
            
            self.set_capturer_folder(new_folder)
            self.do_patrol_iteration()
            self.trigger_report()
            iteration += 1

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

# TODO LIST
# Testear hacer varias vueltas -> hecho
# Rehacer datasets (grande imagen y video) -> hecho
# Testear imagen, secuencia y video -> falta imagen y secuencia ig, testar con evaluador, más rapido
# memoria