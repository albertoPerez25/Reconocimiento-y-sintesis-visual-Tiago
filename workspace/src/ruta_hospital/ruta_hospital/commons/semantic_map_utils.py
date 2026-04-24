import json
import math

def load_semantic_map(semantic_map_path, logger=None):
    '''Carga las zonas del hospital desde un archivo JSON externo'''
    try:
        with open(semantic_map_path, 'r') as f:
            data = json.load(f)
            hospital_zones = data.get("HOSPITAL_ZONES", {})
            reception_zone = data.get("RECEPTION_ZONE", {})
            if logger:
                logger.info("Mapa semántico cargado correctamente")
            return hospital_zones, reception_zone
    except Exception as e:
        if logger:
            logger.error(f"Error cargando mapa: {e}")
        return {}, {"esquina1": [0,0], "esquina2": [0,0]}

def get_nearest_room(position, semantic_map):
    '''Encuentra la habitación más cercana a unas coordenadas dadas'''
    min_dist = float('inf')
    nearest_room = None
    x, y = position[0], position[1]
    
    if not semantic_map:
        return nearest_room

    for room_name, coords in semantic_map.items():
        cx = (coords["esquina1"][0] + coords["esquina2"][0]) / 2.0
        cy = (coords["esquina1"][1] + coords["esquina2"][1]) / 2.0
        dist = math.hypot(x - cx, y - cy)
        if dist < min_dist:
            min_dist = dist
            nearest_room = room_name
            
    return nearest_room if nearest_room else "Desconocida"

def get_zone_name(position, hospital_zones, reception_zone=None):
    ''' Obtiene el nombre de la zona para unas coordenadas x,y.
        Agrupa los pasillos en las zonas adyacentes y unifica la recepción '''
    if not position or not hospital_zones:
        return "Desconocida"
        
    x, y = position[0], position[1]

    for nombre_zona, coords in hospital_zones.items():
        x1, y1 = coords["esquina1"]
        x2, y2 = coords["esquina2"]
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return nombre_zona
            
    # si está en la Recepción se unifica bajo el mismo nombre
    if reception_zone:
        rx1, ry1 = reception_zone["esquina1"]
        rx2, ry2 = reception_zone["esquina2"]
        if min(rx1, rx2) <= x <= max(rx1, rx2) and min(ry1, ry2) <= y <= max(ry1, ry2):
            return "Recepcion"
            
    nearest_room = get_nearest_room(position, hospital_zones)
    return nearest_room 

def get_precise_zone_name(position, hospital_zones, reception_zone=None):
    ''' Obtiene el nombre de las coordenadas x,y '''
    if not position or not hospital_zones:
        return "Desconocida"
        
    x, y = position[0], position[1]

    for nombre_zona, coords in hospital_zones.items():
        x1, y1 = coords["esquina1"]
        x2, y2 = coords["esquina2"]
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return nombre_zona
            
    nearest_room = get_nearest_room(position, hospital_zones)
    
    if reception_zone:
        rx1, ry1 = reception_zone["esquina1"]
        rx2, ry2 = reception_zone["esquina2"]
        if min(rx1, rx2) <= x <= max(rx1, rx2) and min(ry1, ry2) <= y <= max(ry1, ry2):
            return f"Recepción (cerca de {nearest_room})"
            
    return f"Pasillo (cerca de {nearest_room})"
    