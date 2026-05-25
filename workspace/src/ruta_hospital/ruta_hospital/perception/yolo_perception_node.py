#!/usr/bin/env python3
import cv2
import rclpy
import os
import json
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
    output_video_path: str = "/tmp/yolo_annotated_video.avi"
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

    def process_image(self, image_path, include_raw_detections=False):
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
            return {"descripcion_vlm": f"{len(result.boxes)} p. (Ocultos/Sin posturas)", "alerta": False}

        track_history = {}
        detections = []
        alert = False

        ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else [i+1 for i in range(len(result.boxes))]

        for box, keypoints, track_id in zip(result.boxes, result.keypoints, ids):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1 
            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()
            
            posture,is_alert = self.calculate_posture(width, height, pts, confs)

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

    def calculate_posture(self, width, height, pts, confs):
        '''Calcula las posturas en base a los puntos devueltos por YOLO'''
        if width > (height * 1.2): 
            return "Caída URGENTE",True
        
        nose_y, nose_c = pts[0][1], confs[0]
        hip_y = (pts[11][1] + pts[12][1]) / 2.0
        hip_c = (confs[11] + confs[12]) / 2.0

        knee_y = (pts[13][1] + pts[14][1]) / 2.0 
        knee_c = (confs[13] + confs[14]) / 2.0

        ankle_y = (pts[15][1] + pts[16][1]) / 2.0 
        ankle_c = (confs[15] + confs[16]) / 2.0

        if hip_c > self.min_confidence and knee_c > self.min_confidence:
            if abs(hip_y - knee_y) < (height * 0.2) or (width > height * 0.6 and width < height * 1.2):
                return "Sentada",False
            
        if nose_c > self.min_confidence and ankle_c > self.min_confidence:
            if abs(ankle_y - nose_y) < (width * 0.6): 
                return "Caída URGENTE",True # (cabeza y pies a altura similar)
            
            elif height > (width * 1.5): 
                return "De pie o caminando",False
        
        if height > (width * 1.3): 
            return "De pie (?)",False # piernas parcialmente ocultas 
        
        return "Sentada (?)",False # piernas parcialmente ocultas 
    
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
            frame_path = f"/tmp/yolo_seq_{index}.jpg"
            cv2.imwrite(frame_path, annotated_frame)
            state.sequence_paths.append(frame_path)

    def update_tracking_history(self, result, track_history):
        '''Actualiza el historial de posturas y devuelve True si hay alerta en este frame'''
        frame_alert = False
        
        if result.boxes is None or len(result.boxes) == 0 or result.keypoints is None:
            return frame_alert
            
        ids = result.boxes.id.int().cpu().tolist() if result.boxes.id is not None else [i+1 for i in range(len(result.boxes))]
        
        for box, keypoints, track_id in zip(result.boxes, result.keypoints, ids):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            width, height = x2 - x1, y2 - y1
            pts = keypoints.xy[0].tolist()
            confs = keypoints.conf[0].tolist()
            
            posture, is_alert = self.calculate_posture(width, height, pts, confs)
            if is_alert:
                frame_alert = True
            
            if track_id not in track_history:
                track_history[track_id] = set()
            track_history[track_id].add(posture)
            
        return frame_alert

    def build_response(self, track_history, global_alert, state=None, detections=None):
        '''Construye el JSON final con el resumen de la escena, integrando imagen estática y temporal'''
        if not track_history:
            return {"descripcion_vlm": "Despejado", "alerta": False}
            
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