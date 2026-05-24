#!/usr/bin/env python3
import rclpy
import os
import json
import cv2
import importlib
from dataclasses import dataclass

from ruta_hospital.perception.base_perception import BasePerceptionNode
#from .yolo_perception_node import YoloPerceptionNode
#from .vlm_perception_node import VLMPerceptionNode

DEFAULT_ANNOTATED_IMG_PATH = "/tmp/annotated_vlm_frame.jpg"
DEFAULT_DELETE_ANNOTATED_IMG = True

DEFAULT_POSITION_ESTIMATORS = ['ruta_hospital.perception.yolo_perception_node.YoloPerceptionNode']
DEFAULT_VLM_ESTIMATORS = ['ruta_hospital.perception.vlm_perception_node.VLMPerceptionNode']

@dataclass
class model_atr:
    desc: str
    alert: bool

def load_node_class(class_path):
    '''Importa y devuelve una clase dinámicamente desde un string de ruta (Patrón SOTA)'''
    module_path, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

class HybridPerceptionNode(BasePerceptionNode):
    def __init__(self):
        super().__init__('hybrid_perception_node')
        
        # Memoria a corto plazo
        self.tracking_memory = {}

        # parametros
        self.declare_parameter('annotated_image_path', DEFAULT_ANNOTATED_IMG_PATH)
        self.declare_parameter('delete_annotated_image', DEFAULT_DELETE_ANNOTATED_IMG)

        self.declare_parameter('position_estimators', DEFAULT_POSITION_ESTIMATORS)
        self.declare_parameter('vlm_estimators', DEFAULT_VLM_ESTIMATORS)

        self.annotated_image_path = self.get_parameter('annotated_image_path').get_parameter_value().string_value
        self.delete_annotated_image = self.get_parameter('delete_annotated_image').get_parameter_value().bool_value
        
        pos_classes = self.get_parameter('position_estimators').get_parameter_value().string_array_value
        vlm_classes = self.get_parameter('vlm_estimators').get_parameter_value().string_array_value

        self.pos_models = []
        self.vlm_models = []

        # Instanciación en tiempo de ejecución
        for cls_path in pos_classes:
            try:
                cls = load_node_class(cls_path)
                self.pos_models.append(cls(start_service=False))
                self.get_logger().debug(f"Estimador de posición acoplado: {cls_path}")
            except Exception as e:
                self.get_logger().error(f"Error acoplando {cls_path}: {e}")

        for cls_path in vlm_classes:
            try:
                cls = load_node_class(cls_path)
                self.vlm_models.append(cls(start_service=False))
                self.get_logger().debug(f"Modelo VLM acoplado: {cls_path}")
            except Exception as e:
                self.get_logger().error(f"Error acoplando {cls_path}: {e}")
        
        self.saved_image_counter = 0
        
        self.get_logger().info("Nodo percepcion con YOLO y VLM iniciado")


    def process_image(self, image_path, context):
        '''Combina los resultados de la inferencia delegando en los perceptores compatibles'''

        self.get_logger().debug(f"Procesamiento híbrido iniciado para: {image_path}")
        self.get_logger().debug(f"zone_name:{context.zone_name} | time_str:{context.time_str} | expected_activities:{context.expected_activities} | zone_type:{context.zone_type}")

        pos_data_list = []
        all_detections = []

        # Ejecutar modelos de posición (posiciones, conteo exacto y tracking)
        for model in self.pos_models:
            if model.check_path(image_path):
                # Retorno crudo (is_hybrid=True)
                report = model.process_image(image_path, is_hybrid=True)
                try:
                    data = json.loads(report)
                except json.JSONDecodeError:
                    data = {"descripcion_vlm": "Error de formato POSE", "alerta": False}

                pos_data_list.append(data)
                # Detecciones para el renderizado visual
                if "detecciones" in data:
                    all_detections.extend(data["detecciones"])
        
        # Generar imagen anotada
        image_to_vlm = image_path
        # comentar el bloque 'if all_detections:' para que sea image_to_vlm = image_path (imagen limpia)
        if all_detections: 
            self.get_logger().debug("Generando imagen anotada con detecciones para el VLM...")
            annotated_img = self.get_image_with_tracking_data(all_detections, image_path, context)
            if annotated_img: # Seguridad por si cv2 falla al escribir
                image_to_vlm = annotated_img

        # Ejecutar modelos VLM (contexto, peligros y descripción)
        vlm_data_list = []
        for model in self.vlm_models:
            if model.check_path(image_to_vlm):
                report = model.process_image(image_to_vlm, context)
                try:
                    report = json.loads(report)
                except json.JSONDecodeError:
                    report = {"descripcion_vlm": "Error de formato VLM", "alerta": False}
                
                vlm_data_list.append(json.loads(report))

        # Limpiaer frame temporal
        if self.delete_annotated_image and image_to_vlm == self.annotated_image_path and os.path.exists(image_to_vlm):
            os.remove(image_to_vlm)

        # Si el reportero envió un formato que no tiene modelos compatibles
        if not pos_data_list and not vlm_data_list:
            return json.dumps({"descripcion_vlm": "Formato ignorado por los perceptores acoplados.", "alerta": False}, ensure_ascii=False)
        
        json_response = self.get_json_response(pos_data_list, vlm_data_list)
        self.get_logger().debug(f"{json_response}")
        return json.dumps(json_response, ensure_ascii=False)
    
        
    def check_path(self, path):
        '''Metodo para comprobar que el input sea compatible con alguno de los modelos'''
        for model in self.pos_models + self.vlm_models:
            if model.check_path(path):
                return True
        return False
    

    def get_image_with_tracking_data(self, detections, image_path, context):
        '''Devuelve la imagen con un recuadrado señalando el trackeo hecho por YOLO'''
        final_image_path = image_path
        img_cv = cv2.imread(image_path)
        if img_cv is not None:
            history_str = ""
            COLORS = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 0, 255)]
            COLOR_NAMES = ["ROJA", "AZUL", "VERDE", "AMARILLA", "MAGENTA"]
            
            for det in detections:
                trk_id = det["id"]
                bbox = det["bbox"]
                
                # Limpiar la postura de YOLO para intentar no saturar al VLM
                clean_posture = det["posture"].replace("(ignorar) Todo correcto. ", "").replace("ATENCIÓN ", "")
                
                # Sliding Window (Memoria FIFO de 3 frames)
                if trk_id not in self.tracking_memory:
                    self.tracking_memory[trk_id] = []
                self.tracking_memory[trk_id].append(clean_posture)
                if len(self.tracking_memory[trk_id]) > 3:
                    self.tracking_memory[trk_id].pop(0)
                    
                # Colores y texto sobrepuestos a la imagen para pasársela al vlm
                color_idx = trk_id % len(COLORS)
                color_bgr = COLORS[color_idx]
                color_name = COLOR_NAMES[color_idx]
                
                history_str += f"- Sujeto ID_{trk_id} (Caja {color_name}): Historial -> {' | '.join(self.tracking_memory[trk_id])}\n"                
                cv2.rectangle(img_cv, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color_bgr, 3)
            
            context.tracking_history = history_str

            if not self.delete_annotated_image:
                base, ext = os.path.splitext(self.annotated_image_path) # Separar ruta y extensión (/tmp/foto , .jpg)
                final_image_path = f"{base}_{self.saved_image_counter}{ext}"
                self.saved_image_counter += 1
                self.get_logger().debug(f"Imagen con tracking: {final_image_path}")
            else:
                final_image_path = self.annotated_image_path

            cv2.imwrite(final_image_path, img_cv)

            return final_image_path
        else:
            self.get_logger().error(f"img_cv es None. Path: {image_path}")
            return None
    

    def get_combined_json(self, pos_atr_list, vlm_atr_list):
        '''Devuelve la descripcion y alertas finales teniendo en cuenta los json de yolo y del vlm'''
        final_alert = any(m.alert for m in pos_atr_list + vlm_atr_list)
        prefix = "[ALERTA] " if final_alert else ""
        
        # Deduplicación y formateo limpio (Estilo Log)
        position_texts = [m.desc.strip() for m in pos_atr_list if m.desc.strip()]
        vlm_texts = [m.desc.strip() for m in vlm_atr_list if m.desc.strip()]
        
        # Filtrar los perceptores que no detectan nada
        empty_tokens = ["despejado", "despejada"]
        useful_vlms = [t for t in vlm_texts if not any(term in t.lower() for term in empty_tokens) and t != "."]
            
        # Caso base: Todos los modelos de posición ven 0 personas (o no hay) y no hay descripciones VLM útiles
        empty_position_models = all("0 p." in t for t in position_texts) or not position_texts
        if empty_position_models and not useful_vlms:
            return f"{prefix}Despejado.", final_alert

        # Unir descripciones usando un punto como separador limpio
        parts = position_texts + useful_vlms
        combined_desc = f"{prefix}{'. '.join(parts)}"

        return combined_desc, final_alert
    

    def get_json_response(self, pos_data_list, vlm_data_list):
        '''Devuelve la respuesta final a la petición en formato json'''
        pos_atr_list = []
        for data in pos_data_list:
            desc = str(data.get("descripcion_vlm", "")).strip()
            alert = bool(data.get("alerta", False))
            pos_atr_list.append(model_atr(desc, alert)) 
            # TODO: La falta de una persona puede ser información relevante

        vlm_atr_list = []
        for data in vlm_data_list:
            desc = str(data.get("descripcion_vlm", "")).strip()
            alert = bool(data.get("alerta", False))
            # Convierto a str o bool para evitar que crashe si el vlm alucina 
            # pero devuelve un formato json "valido"
            vlm_atr_list.append(model_atr(desc, alert))

        final_desc, final_alert = self.get_combined_json(pos_atr_list, vlm_atr_list)

        json_response = {
            "descripcion_vlm": final_desc,
            "alerta": final_alert
        }
        return json.dumps(json_response, ensure_ascii=False)
    

def main(args=None):
    rclpy.init(args=args)
    node = HybridPerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()