#!/usr/bin/env python3
import cv2
import rclpy
import os
import uuid
from ultralytics import YOLO
from dataclasses import dataclass, field

# Servicio personalizado para comunicación entre LLM y Yolo
from ruta_hospital.perception.base_position_perception import BasePositionPerceptionNode

#yolov8n-pose.pt
DEFAULT_YOLO_MODEL = "yolo26n-pose.pt"
DEFAULT_MIN_CONFIDENCE = 0.5

@dataclass
class TemporalRenderState:
    is_hybrid: bool
    is_video: bool
    output_video_path: str = field(default_factory=lambda: f"/tmp/yolo_video_{uuid.uuid4().hex[:8]}.avi")
    video_writer: object = None
    sequence_paths: list = field(default_factory=list)

class YoloPerceptionNode(BasePositionPerceptionNode):
    def __init__(self,start_service=True):
        super().__init__('yolo_perception_node',start_service=start_service)
        self.declare_parameter('yolo_model', DEFAULT_YOLO_MODEL)
        self.declare_parameter('min_confidence', DEFAULT_MIN_CONFIDENCE)

        selected_yolo_model = self.get_parameter('yolo_model').get_parameter_value().string_value
        self.min_confidence = self.get_parameter('min_confidence').get_parameter_value().double_value

        self.model = YOLO(selected_yolo_model)
        self.get_logger().info(f"Modelo {selected_yolo_model} cargado")

    def process_image(self, image_path, include_raw_detections=False): # TODO: Dividir
        '''Procesa la imagen y devuelve el reporte en forma de string '''
        is_video = image_path.lower().endswith('.avi')
        is_sequence = ',' in image_path
        
        if is_video or is_sequence:
            return self.process_temporal_data(image_path, is_video, include_raw_detections)

        image = cv2.imread(image_path)
        if image is None:
            return {"descripcion_vlm": "Error: No se pudo leer la imagen con OpenCV", "alerta": False}

        results = self.model.track(image, persist=True, verbose=False)
        result = results[0]

        if len(result.boxes) == 0:
            return {"descripcion_vlm": "Despejado", "alerta": False}
        
        if result.keypoints is None:
            return {"descripcion_vlm": f"{len(result.boxes)} personas. (Ocultos/Sin posturas)", "alerta": False}

        track_history = {}
        detections = []
        alert = False

        img_height, img_width = image.shape[:2]
        total_area = img_width * img_height

        ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else [i+1 for i in range(len(result.boxes))]

        for box, keypoints, track_id in zip(result.boxes, result.keypoints, ids):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1 

            if (width * height) < (total_area * self.min_area_ratio):
                continue

            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()
            
            posture,is_alert = self.calculate_posture(width, 
                                                      height, 
                                                      pts, 
                                                      confs, 
                                                      y2, 
                                                      img_height
                                                    )

            if is_alert:
                alert = True

            track_history[track_id] = {posture}

            detections.append({
                "id": track_id,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "posture": posture
            })

        # Conteo de personas con la lista de posturas
        json_response = self.build_response(
            track_history=track_history, 
            global_alert=alert, 
            detections=detections if include_raw_detections else None
        )

        return json_response

    def calculate_posture(self, width, height, pts, confs, y2, img_height): # TODO: Dividir
        '''Calcula posturas usando relaciones biomecánicas y conciencia espacial'''
        
        nose_y, nose_c = pts[0][1], confs[0]
        
        # Eje Y en imágenes crece hacia abajo. (Valores mayores = más cerca del suelo)
        hip_y = (pts[11][1] + pts[12][1]) / 2.0
        hip_c = (confs[11] + confs[12]) / 2.0

        knee_y = (pts[13][1] + pts[14][1]) / 2.0 
        knee_c = (confs[13] + confs[14]) / 2.0

        ankle_y = (pts[15][1] + pts[16][1]) / 2.0 
        ankle_c = (confs[15] + confs[16]) / 2.0

        # DETECCIÓN DE ESTADO HORIZONTAL
        is_horizontal = False
        
        # Biomecánica: cabeza a la altura de la cadera o más baja
        if nose_c > self.min_confidence and hip_c > self.min_confidence:
            if nose_y > (hip_y - height * 0.15): 
                is_horizontal = True
                
        # Aspect Ratio: Caja muy ancha (con confirmación de puntos si los hay)
        elif width > (height * 1.3):
            if nose_c > self.min_confidence and hip_c > self.min_confidence:
                if abs(nose_y - hip_y) < (height * 0.3):
                    is_horizontal = True
            elif width > (height * 1.8): # Oclusión severa pero extremadamente horizontal
                is_horizontal = True

        # DIFERENCIADOR CAMILLA VS SUELO
        if is_horizontal:
            # Ratio vertical: 0.0 es el techo, 1.0 es el suelo de la imagen
            vertical_ratio = y2 / img_height
            
            # Si YOLO no ve las piernas, asumimos que están bajo sábanas
            legs_occluded = (knee_c < self.min_confidence and ankle_c < self.min_confidence)
            
            # REGLA DE SEGURIDAD (Priorizar falsos positivos de caídas a falsos negativos):
            # - Si y2 < 0.5: Es imposible que sea el suelo salvo que esté a 30m (Es camilla)
            # - Si y2 < 0.7 y las piernas están ocultas (Seguro es camilla)
            if (vertical_ratio < 0.5) or (vertical_ratio < 0.7 and legs_occluded):
                return "Tumbada en camilla", False
            else:
                return "Caída URGENTE", True

        # POSTURAS VERTICALES
        # Heurística: Sentada (Rodillas a la altura de la cadera)
        if hip_c > self.min_confidence and knee_c > self.min_confidence:
            if abs(hip_y - knee_y) < (height * 0.25):
                return "Sentada", False

        # Heurística: De pie (Cabeza alta y caja vertical)
        if nose_c > self.min_confidence and hip_c > self.min_confidence:
            if height > (width * 1.1) and nose_y < (hip_y - height * 0.2):
                return "De pie o caminando", False

        # FALLBACKS (Si fallan los puntos por recortes de la cámara)
        if height > (width * 1.2): 
            return "Postura indeterminada", False # "De pie (?)"
        elif width > height:
            return "Postura indeterminada", False # "Sentada (?)"
            
        return "Postura indeterminada", False
    
    def process_temporal_data(self, image_path, is_video, include_raw_detections):
        '''Procesa vídeo o secuencias orquestando el renderizado y el análisis'''
        source = image_path if is_video else [r.strip() for r in image_path.split(',') if os.path.isfile(r.strip())]
        
        if not source:
            return {"descripcion_vlm": "Error: Fuente temporal vacía", "alerta": False}
            
        results = self.model.track(source, persist=True, verbose=False, stream=True)
        
        global_alert = False
        track_history = {} 
        state = TemporalRenderState(is_hybrid=include_raw_detections, is_video=is_video)
        
        for i, result in enumerate(results):
            # Renderizado visual
            if state.is_hybrid:
                self.handle_temporal_rendering(result, i, state)
                
            # Análisis de posturas y alertas 
            frame_alert = self.update_tracking_history(result, track_history)
            if frame_alert:
                global_alert = True

        if state.video_writer is not None:
            state.video_writer.release()
            
        # Formateo y retorno de la respuesta
        return self.build_response(track_history, global_alert, state=state)

    def handle_temporal_rendering(self, result, index, state):
        '''Gestiona el renderizado SOTA y guardado de frames para vídeo o secuencias'''
        annotated_frame = result.plot() 
        
        if state.is_video:
            if state.video_writer is None:
                height, width, _ = annotated_frame.shape
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                state.video_writer = cv2.VideoWriter(state.output_video_path, fourcc, 30, (width, height))
            state.video_writer.write(annotated_frame)
        else:
            unique_id = uuid.uuid4().hex[:8]
            frame_path = f"/tmp/yolo_seq_{unique_id}_{index}.jpg"
            cv2.imwrite(frame_path, annotated_frame)
            state.sequence_paths.append(frame_path)

    def update_tracking_history(self, result, track_history):
        '''Actualiza el historial de posturas y devuelve True si hay alerta en este frame'''
        frame_alert = False
        
        if result.boxes is None or len(result.boxes) == 0 or result.keypoints is None:
            return frame_alert
        
        # Obtener dimensiones originales (height, width) del objeto Ultralytics
        img_height, img_width = result.orig_shape
        total_area = img_width * img_height
            
        ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else [i+1 for i in range(len(result.boxes))]
        
        for box, keypoints, track_id in zip(result.boxes, result.keypoints, ids):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1

            # Filtro de profundidad por área (Ignorar personas en otras salas)
            if (width * height) < (total_area * self.min_area_ratio):
                continue

            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()
            
            posture, is_alert = self.calculate_posture(width, 
                                                       height, 
                                                       pts, 
                                                       confs, 
                                                       y2, 
                                                       img_height
                                                    )
            if len(pts) < 17:
                return "Postura desconocida", False
            if is_alert:
                frame_alert = True
            if track_id not in track_history:
                track_history[track_id] = set()
            track_history[track_id].add(posture)
            
        return frame_alert

    def build_response(self, track_history, global_alert, state=None, detections=None):
        '''Construye el JSON final con el resumen de la escena, integrando imagen estática y temporal'''
        if not track_history:
            json_response = {"descripcion_vlm": "Despejado", "alerta": False}
        else:
            descriptions = []
            for tid, postures in track_history.items():
                descriptions.append(f"Persona Nº {tid}: {' -> '.join(list(postures))}")
                
            final_description = f"{len(track_history)} personas. ({', '.join(descriptions)})"
            
            json_response = {
                "descripcion_vlm": final_description,
                "alerta": global_alert
            }
        
        # Inyección para flujos temporales (vídeo/secuencia)
        if state and state.is_hybrid:
            json_response["ruta_anotada"] = state.output_video_path if state.is_video else ",".join(state.sequence_paths)
            
        # Inyección para flujos estáticos (imagen)
        if detections is not None:
            json_response["detecciones"] = detections
            
        return json_response
    
    def check_path(self, path):
        '''Verifica que el input sea una imagen, vídeo o secuencia válida'''
        if not path:
            return False
            
        if path.lower().endswith('.avi') and os.path.isfile(path):
            return True
            
        rutas = path.split(',')
        return any(os.path.isfile(r.strip()) for r in rutas)

def main(args=None):
    rclpy.init(args=args)
    try:
        rclpy.spin(YoloPerceptionNode())
    except KeyboardInterrupt: pass
    finally: rclpy.shutdown()

if __name__ == '__main__': 
    main()