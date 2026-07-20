import json
from geometry_msgs.msg import PoseStamped

def load_route(route_file_path, default_path_points, logger):
    '''Carga la lista de waypoints desde el archivo JSON'''
    try:
        with open(route_file_path, 'r') as f:
            data = json.load(f)
            route = data.get("PATH_POINTS", [])
            logger.info(f"Ruta cargada exitosamente desde {route_file_path}")
            return route
    except Exception as e:
        logger.error(f"Error cargando el archivo de ruta: {e}")
        return default_path_points

def list_to_pose(path_points, clock):
    '''Pasa la lista de waypoints a poses'''
    route_poses = []
    for point in path_points:
        pose = create_pose(clock, point[0], point[1])
        route_poses.append(pose)
    return route_poses

def create_pose(clock, x, y):
    '''Crea poses neutras'''
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = clock.now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.w = 1.0 # Orientación neutra
    return pose