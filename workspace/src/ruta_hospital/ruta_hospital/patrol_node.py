#!/usr/bin/env python3
import time
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
# Para leer input de la terminal:
import sys
import select
import tty
import termios

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
    [-3.2156, -25.070],
    [-8.3355, -16.266],
    [-2.0161, -19.663],
    [-2.7160, -9.7099],
    [-10.646, -2.9706], #
    [-4.8351, -4.0706], # evitar las sillas
    [-4.1000, 1.45583], # evitar las sillas
    [-10.021, 1.28012], 
    [-7.6369, 5.47739],
    [-4.3140, 7.82489]
]

""" 
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
    [-3.2156, -25.070],
    [-8.3355, -16.266],
    [-2.0161, -19.663],
    [-2.7160, -9.7099],
    [-10.646, -2.9706], #
    [-4.8351, -4.0706], # evitar las sillas
    [-4.1000, 1.45583], # evitar las sillas
    [-10.021, 1.28012], 
    [-7.6369, 5.47739],
    [-4.3140, 7.82489]
"""

def init():
    rclpy.init()
    navigator = BasicNavigator()
    navigator.waitUntilNav2Active()

    print("Patrol Node")
    return navigator

def create_pose(navigator, x, y):
    '''Crea poses neutras'''
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.w = 1.0 # Orientación neutra
    return pose

def state_check(result,index,iteration): 
    '''Devuelve el estado actual/final'''
    if result == TaskResult.SUCCEEDED:
        #time.sleep(2.0) # Pausa breve entre vueltas simulando dar un resumen
        ret = True
    else:
        ret = False
        print(f"\n {iteration+1} fallo(s) intentando llegar al punto {index}")
        if result == TaskResult.CANCELED:
            print(" Navegacion cancelada")
        elif result == TaskResult.FAILED:
            print(f" Intento {iteration+1} fallido")
        else:
            print(" Fallo desconocido:",result)
    return ret

def list_to_pose(navigator):
    '''Pasa la lista de waypoints a poses'''
    route_poses = []
    for point in PATH_POINTS:
        pose = create_pose(navigator, point[0], point[1])
        route_poses.append(pose)
    return route_poses

def execute_rescue(navigator, backup_dist=0.5, backup_speed=0.2):
    '''Saca al robot de un atasco dando marcha atrás y limpiando la memoria de obstáculos'''
    print("\n [Rescate] Intentando recuperar la navegación...")
    
    # Marcha atrás para separarse del obstáculo
    navigator.backup(backup_dist=backup_dist, backup_speed=backup_speed)
    while not navigator.isTaskComplete():
        time.sleep(1.0)
        
    navigator.clearAllCostmaps()   # Para eliminar obstáculos
    time.sleep(1.5)                # Para que el sensor láser se ajuste

def get_key_non_blocking():
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

def navigate_to_waypoint(navigator, pose, current_index, total_points, max_retries=2):
    '''Intenta llegar a un waypoint. Si falla, ejecuta el rescate y lo vuelve a intentar'''
    for it in range(max_retries):
        navigator.goToPose(pose)

        while not navigator.isTaskComplete():
            # El feedback de goToPose no tiene current_waypoint
            print(f"Punto actual: {current_index}/{total_points} | Intento: {it + 1}/{max_retries} | (s) Saltar", end='\r')
            
            key = get_key_non_blocking()
            if key and key.lower() == 's':
                print(f"\n [Salto] Punto {current_index} omitido por el usuario")
                navigator.cancelTask()
                time.sleep(0.2) # Que le de tiempo a procesarlo
                return True # para que no salte error

            #time.sleep(0.2)

        result = navigator.getResult()
        
        if state_check(result,current_index,it):
            return True
            
        if it < max_retries - 1:
            execute_rescue(navigator)

    print("Pasando al siguiente punto")
    return False

def do_patrol_iteration(route_poses, navigator):
    '''Reemplaza followWaypoints por un bucle iterativo para intercalar la marcha atrás y manejo de atascos'''
    total_points = len(route_poses)
    
    for i, pose in enumerate(route_poses):
        current_index = i + 1
        
        success = navigate_to_waypoint(navigator, pose, current_index, total_points, max_retries=2)

        """ if not success:
            continue # Pasa al siguiente punto

        # Da marcha atrás al salir del punto, ayuda con el lidar
        navigator.backup(backup_dist=0.0, backup_speed=0.2) # TODO: Comprobar si sigue siendo necesario
        while not navigator.isTaskComplete():
            time.sleep(1.0) """

def main():
    navigator = init()

    route_poses = list_to_pose(navigator)
    
    print(f"Ruta cargada con {len(route_poses)} puntos")

    try:
        iteration = 1
        while True:
            print(f"\nVUELTA Nº {iteration}")

            do_patrol_iteration(route_poses,navigator)
            iteration += 1

    except KeyboardInterrupt: # Para poder pararlo más fácil
        navigator.cancelTask()
    
    navigator.lifecycleShutdown()

if __name__ == '__main__':
    main()
