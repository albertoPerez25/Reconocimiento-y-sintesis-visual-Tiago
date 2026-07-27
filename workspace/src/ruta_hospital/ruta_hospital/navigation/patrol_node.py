#!/usr/bin/env python3
import time
import rclpy
import os
import subprocess 
import math

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.action import ActionClient
from hospital_interfaces.action import GenerateReport
from ruta_hospital.chatbot import chatbot_web

from rcl_interfaces.srv import SetParameters 
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType

from ruta_hospital.navigation.utils.route_parser_utils import load_route,list_to_pose
from ruta_hospital.navigation.utils.file_utils import clean_all_orphan_folders, get_next_available_folder
from ruta_hospital.utils.commons.file_utils import delete_folder
from ruta_hospital.utils.commons.terminal_utils import get_key_non_blocking
from ament_index_python.packages import get_package_share_directory

from hospital_interfaces.srv import FlushZoneData
from ruta_hospital.utils.shared.semantic_map_utils import get_zone_name, load_semantic_map

# Waypoints por defecto
DEFAULT_PATH_POINTS = [
    [4.83898, 8.27372], [8.21112, 6.68955], [11.4583, 1.65471], [4.47097, 0.75583], 
    [4.83519, -4.0706], [11.0001, -3.4900], [2.34139, -9.9597], [7.14909, -18.077],
    [2.01610, -19.663], [1.35232, -27.070], [7.02417, -31.315], [4.21443, -36.248], 
    [-4.1522, -41.493], [-8.8351, -36.498], [-8.8975, -29.067], [-3.2156, -25.610], 
    [-8.6355, -16.666], [-2.0161, -20.663], [-3.5160, -7.2099], [-2.7160, -9.7099],
    [-10.646, -2.9706], [-4.8351, -4.0706], [-4.1000, 1.45583], [-10.321, 1.68012], 
    [-7.6369, 5.47739], [-4.3140, 7.82489],
]

PKG_DIR = get_package_share_directory('ruta_hospital')
DEFAULT_WAYPOINTS_PATH = os.path.join(PKG_DIR, "config", "route_waypoints.json")
REPO_ROOT_DIR = os.path.abspath(os.path.join(PKG_DIR, "..", "..", "..", "..", ".."))
DEFAULT_PHOTOS_DIR = os.path.join(REPO_ROOT_DIR, "datasets", "hospital_photos", "")

if not os.path.exists(os.path.join(REPO_ROOT_DIR, "datasets")):
    DEFAULT_PHOTOS_DIR = os.path.join(os.path.expanduser("~"), "ruta_hospital_datasets", "hospital_photos", "")

DEFAULT_KEEP_TEMP_FOLDERS = False
DEFAULT_CAPTURER_NAME = "photos_node"
DEFAULT_USE_RERANKER = False 

class PatrolNode(rclpy.node.Node):
    def __init__(self):
        super().__init__('patrol_node')

        self.declare_parameter('route_file_path', DEFAULT_WAYPOINTS_PATH)
        self.route_file_path = self.get_parameter('route_file_path').get_parameter_value().string_value

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
        
        # Variables de estado y métricas
        self.total_distance = 0.0
        self.last_nav_pose = None  # Almacenará tuplas (x, y) para evitar fallos de referencia
        self.patrol_start_time = 0.0

        self.current_folder_path = ""
        self.current_zone = "Desconocida"
        self.last_zone_change_time = 0.0
        self.debounce_duration = 2.0 
        self.chatbot_process = None

        default_map_path = os.path.join(PKG_DIR, 'config', 'semantic_map.json')
        self.hospital_zones, self.reception_zone = load_semantic_map(default_map_path, self.get_logger())

    def set_capturer_zone(self, zone_name):
        if not self.param_client.wait_for_service(timeout_sec=1.0):
            return
        req = SetParameters.Request()
        param = Parameter()
        param.name = "current_zone"
        param.value = ParameterValue(type=ParameterType.PARAMETER_STRING, string_value=zone_name)
        req.parameters.append(param)
        self.param_client.call_async(req)

    def trigger_zone_flush(self, zone_name):
        if not self.flush_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Servicio de flush no disponible. Ignorando...")
            return
        req = FlushZoneData.Request()
        req.zone_name = zone_name
        self.flush_cli.call_async(req)
        self.get_logger().debug(f"Trigger de fin de zona enviado para: {zone_name}")

    def set_capturer_folder(self, folder_path):
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
        self.get_logger().info("Iniciado el informe")
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
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('La meta fue rechazada por el reportero, no se generará informe')
            if not self.keep_temp_folders:
                delete_folder(folder_to_clean, self.get_logger())
            return
        self.get_logger().info('Generando informe...')
        self.active_goal_handle = goal_handle 
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(lambda fut: self.get_result_callback(fut, folder_to_clean))

    def report_feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"[Reportero]: Zona: {feedback.current_zone} ({feedback.percentage_complete:.1f}%)")

    def get_result_callback(self, future, folder_to_clean):
        result = future.result().result
        status = future.result().status
        if status == 4 and result.success:
            self.get_logger().info(f"\nINFORME COMPLETADO \n{result.final_report}\n")
        else:
            self.get_logger().error(f"ERROR generando el informe en el reportero: {result.final_report}")
            
        if not self.keep_temp_folders:
            self.get_logger().debug(f"Limpiando datos de sesión: {folder_to_clean}")
            delete_folder(folder_to_clean, self.get_logger())
        else:
            self.get_logger().debug(f"Modo keep_temp_folders ON. Se conserva: {folder_to_clean}")
        self.active_goal_handle = None 

    def state_check(self, result, index, iteration): 
        if result == TaskResult.SUCCEEDED:
            ret = True
        else:
            ret = False
            self.get_logger().warn(f"{iteration+1} fallo(s) intentando llegar al punto {index}")
            if result == TaskResult.CANCELED:
                self.get_logger().warn(" Navegacion cancelada")
            elif result == TaskResult.FAILED:
                self.get_logger().error(f" Intento {iteration+1} fallido")
            else:
                self.get_logger().error(f" Fallo desconocido: {result}") 
        return ret

    def execute_rescue(self, backup_dist=0.5, backup_speed=0.2):
        self.get_logger().info("\n [Rescate] Intentando recuperar la navegación...")
        self.navigator.backup(backup_dist=backup_dist, backup_speed=backup_speed)
        while not self.navigator.isTaskComplete():
            time.sleep(1.0)
        self.navigator.clearAllCostmaps()   
        time.sleep(1.5)                

    def navigate_to_waypoint(self, pose, current_index, total_points, max_retries=2):
        for it in range(max_retries):
            self.navigator.goToPose(pose)

            while not self.navigator.isTaskComplete():
                feedback = self.navigator.getFeedback()
                if feedback:
                    x = feedback.current_pose.pose.position.x
                    y = feedback.current_pose.pose.position.y
                    
                    # CÁLCULO DE DISTANCIA ROBUSTO
                    if self.last_nav_pose is not None:
                        dx = x - self.last_nav_pose[0]
                        dy = y - self.last_nav_pose[1]
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        # Fallback: Filtro de ruido. Solo acumular si el movimiento es lógico (< 1m por iteración)
                        if 0.001 < dist < 1.0:
                            self.total_distance += dist
                    
                    # Guardamos la posición como tupla pura para aislar referencias de memoria
                    self.last_nav_pose = (x, y)

                    # LOGICA DE ZONAS
                    new_zone = get_zone_name([x, y], self.hospital_zones, self.reception_zone)
                    if new_zone != self.current_zone and new_zone != "Desconocida":
                        if time.time() - self.last_zone_change_time > self.debounce_duration:
                            if self.current_zone != "Desconocida":
                                self.get_logger().info(f"\nTransición detectada: Abandonando {self.current_zone} -> Entrando a {new_zone}")
                                self.trigger_zone_flush(self.current_zone)
                            
                            self.current_zone = new_zone
                            self.last_zone_change_time = time.time()
                            self.set_capturer_zone(new_zone)

                nav_msg = f"Ruta: {current_index}/{total_points} | Intento: {it + 1}/{max_retries} | [s] Saltar [d] Cancelar inf. [c] Chat"
                print(f"\r\033[K{nav_msg}", end='', flush=True)

                key = get_key_non_blocking()
                time.sleep(0.01)
                if key and key.lower() == 's':
                    self.get_logger().warn(f"\n [Salto] Punto {current_index} omitido por el usuario")
                    self.navigator.cancelTask()
                    time.sleep(0.2) 
                    return True 
                elif key and key.lower() == 'd' and hasattr(self, 'active_goal_handle') and self.active_goal_handle:
                    self.get_logger().warn("[Informe] Cancelado el informe en curso")
                    self.active_goal_handle.cancel_goal_async()
                elif key and key.lower() == 'c':
                    print("\n") 
                    self.get_logger().info("Abriendo interfaz web del Chatbot (Streamlit)...")
                    if not hasattr(self, 'chatbot_process') or self.chatbot_process is None or self.chatbot_process.poll() is not None:
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
                return True
                
            if it < max_retries - 1:
                self.execute_rescue() 

        self.get_logger().info("Pasando al siguiente punto")
        return False

    def do_patrol_iteration(self):
        total_points = len(self.route_poses)
        
        # Reset de estadísticas
        self.total_distance = 0.0
        self.last_nav_pose = None
        self.patrol_start_time = time.time()
        self.current_zone = "Desconocida"
        self.last_zone_change_time = 0.0 
        
        for i, pose in enumerate(self.route_poses):
            current_index = i + 1
            success = self.navigate_to_waypoint(pose, current_index, total_points, max_retries=2) 
        
        # Parar temporizador
        patrol_end_time = time.time()
        elapsed_minutes = (patrol_end_time - self.patrol_start_time) / 60.0
        
        # Imprimir estadísticas finales SIN DECIMALES en la distancia
        self.get_logger().info(f"\n" + "="*50)
        self.get_logger().info(f"ESTADÍSTICAS DE LA PATRULLA:")
        self.get_logger().info(f"Distancia total recorrida: {int(self.total_distance)} metros")
        self.get_logger().info(f"Tiempo de ejecución: {int(elapsed_minutes)} minutos")
        self.get_logger().info("="*50 + "\n")
        
        self.patrol_start_time = 0.0 
        
        if self.current_zone != "Desconocida":
            self.get_logger().info(f"\nRuta terminada. Vaciando buffers de la última zona ({self.current_zone}).")
            self.trigger_zone_flush(self.current_zone)

    def run_patrol(self):
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
            break # solo quiero medir una vuelta

def main(args=None):
    rclpy.init(args=args)
    patrol_node = PatrolNode()
    
    try:
        patrol_node.run_patrol()
    except KeyboardInterrupt: 
        patrol_node.navigator.cancelTask()
        patrol_node.get_logger().info('Ruta cancelada')
    finally:
        patrol_node.navigator.lifecycleShutdown()
        patrol_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()