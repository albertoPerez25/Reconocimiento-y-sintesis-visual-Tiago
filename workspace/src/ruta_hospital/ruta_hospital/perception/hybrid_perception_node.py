#!/usr/bin/env python3
import rclpy
import os
import json
import cv2
import importlib
from dataclasses import dataclass
import time

from ruta_hospital.perception.base_perception import BasePerceptionNode, RagContext
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

        pose_names = [cls_path.rsplit('.', 1)[-1] for cls_path in pos_classes]
        vlm_names = [cls_path.rsplit('.', 1)[-1] for cls_path in vlm_classes]
        
        self.perception_metrics["modelo_usado"] = "hybrid_model"
        self.perception_metrics["modelos_acoplados"] = {
            "pose": pose_names,
            "vlm": vlm_names
        }

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


    def analyze_callback(self, request, response):
        '''Se ejecuta cada vez que recibe una petición del reportero por el servicio'''
        if not self.check_path(request.image_path):
            self.get_logger().error(f"Formato no soportado por los perceptores o ruta inválida: {request.image_path}")
            # Devolvemos un JSON de error válido para que el reportero no crashee al parsearlo
            response.report = json.dumps({"descripcion_vlm": "Error: Ruta o formato inválido.", "alerta": False}, ensure_ascii=False)
            return response 
                    
        self.get_logger().info(f"Analizando imagen: {os.path.basename(request.image_path)}...")
        self.tracking_memory.clear() # Limpiar memoria de tracking entre llamadas estáticas
        
        # Contexto de la zona (reglas RAG, historial) para dárselo a los VLMs
        context = RagContext(request)
        report_dict = self.process_image(request.image_path, context)
        self.save_perception_metrics()
        response.report = json.dumps(report_dict, ensure_ascii=False)
        return response


    def process_image(self, image_path, context):
        '''Combina los resultados de la inferencia delegando en los perceptores compatibles'''
        self.get_logger().debug(f"Procesamiento híbrido iniciado para: {image_path}")
        self.get_logger().debug(f"zone_name:{context.zone_name} | time_str:{context.time_str} | expected_activities:{context.expected_activities} | zone_type:{context.zone_type}")

        t_total_start = time.time()

        # 1. Ejecutar modelos de pose/posición
        pos_data_list, all_detections, image_to_vlm, requiere_vlm, yolo_duration = self._process_pose_models(image_path)

        # 2. Generar imagen anotada (si corresponde)
        image_to_vlm = self._prepare_vlm_image(all_detections, image_to_vlm, image_path, context)

        # 3. Ejecutar modelos VLM
        vlm_data_list, vlm_duration = self._process_vlm_models(requiere_vlm, image_to_vlm, context)

        # 4. Limpieza de temporales
        self._cleanup_temp_files(image_to_vlm, image_path)

        # Si el reportero envió un formato que no tiene modelos compatibles
        if not pos_data_list and not vlm_data_list:
            return {"descripcion_vlm": "Formato ignorado por los perceptores acoplados.", "alerta": False}
        
        self.get_logger().error(f"\n[DEBUG POS] Tipo: {type(pos_data_list)} | Contenido: {pos_data_list}")
        self.get_logger().error(f"[DEBUG VLM] Tipo: {type(vlm_data_list)} | Contenido: {vlm_data_list}")
        
        json_response = self.get_json_response(pos_data_list, vlm_data_list)
        self.get_logger().debug(f"{json_response}")

        total_duration = time.time() - t_total_start

        time_metrics = {
            "yolo_seconds": round(yolo_duration, 3),
            "vlm_seconds": round(vlm_duration, 3),
            "total_seconds": round(total_duration, 3)
        }
        self.perception_metrics["tiempos_procesado"].append(time_metrics)
        
        '''self.get_logger().info(
            f"\n{'='*45}\n"
            f"TIEMPOS DE PERCEPCIÓN ({os.path.basename(image_path)}):\n"
            f"   - YOLO (Espacial):  {yolo_duration:.2f} s\n"
            f"   - VLM (Semántico):  {vlm_duration:.2f} s\n"
            f"   - Total Pipeline:   {total_duration:.2f} s\n"
            f"{'='*45}"
        )'''
        return json_response
    
    def _process_pose_models(self, image_path):
        '''Ejecuta los modelos espaciales (YOLO) y recolecta las detecciones'''
        pos_data_list = []
        all_detections = []
        image_to_vlm = image_path
        requiere_vlm = len(self.pos_models) == 0 # si no hay modelo pose iniciado, se requiere vlm

        t_yolo_start = time.time()

        # Ejecutar modelos de posición (posiciones, conteo exacto y tracking)
        for model in self.pos_models:
            if model.check_path(image_path):
                # Retorno crudo (include_raw_detections=True)
                parsed_data = model.process_image(image_path, include_raw_detections=True)
                if isinstance(parsed_data, str):
                    try:
                        parsed_json = json.loads(parsed_data)
                        parsed_data = parsed_json if isinstance(parsed_json, dict) else {"descripcion_vlm": str(parsed_json), "alerta": False}
                    except Exception:
                        parsed_data = {"descripcion_vlm": parsed_data, "alerta": False}
                pos_data_list.append(parsed_data)

                # Detecciones para el renderizado visual
                if "detecciones" in parsed_data:
                    all_detections.extend(parsed_data["detecciones"])
                if "ruta_anotada" in parsed_data:
                    # El estimador ya provee el archivo con tracking
                    image_to_vlm = parsed_data["ruta_anotada"]

                desc_lower = str(parsed_data.get("descripcion_vlm", "")).lower()
                if "despejado" not in desc_lower and "0 personas" not in desc_lower:
                    # Con que al menos uno de los modelos de pose encuentre hay que pasarsela al VLM
                    requiere_vlm = True    

        yolo_duration = time.time() - t_yolo_start
        return pos_data_list, all_detections, image_to_vlm, requiere_vlm, yolo_duration
    
    def _prepare_vlm_image(self, all_detections, image_to_vlm, image_path, context):
        '''Dibuja las cajas delimitadoras de YOLO en la imagen si es necesario'''
        # comentar el bloque 'if annotated_img:' para que sea image_to_vlm = image_path (imagen limpia)
        if all_detections and image_to_vlm == image_path: 
            self.get_logger().debug("Generando imagen anotada con detecciones para el VLM...")
            annotated_img = self.get_image_with_tracking_data(all_detections, image_path, context)
            '''if annotated_img: # Seguridad por si cv2 falla al escribir
                image_to_vlm = annotated_img'''
        return image_to_vlm


    def _process_vlm_models(self, requiere_vlm, image_to_vlm, context):
        '''Ejecuta los Modelos de Lenguaje Visual solo si es necesario'''
        vlm_data_list = []
        vlm_duration = 0.0
        
        if requiere_vlm:
            t_vlm_start = time.time()
            for model in self.vlm_models:
                if model.check_path(image_to_vlm):
                    parsed_report = model.process_image(image_to_vlm, context)
                    if isinstance(parsed_report, str):
                        try:
                            parsed_json = json.loads(parsed_report)
                            parsed_report = parsed_json if isinstance(parsed_json, dict) else {"descripcion_vlm": str(parsed_json), "alerta": False}
                        except Exception:
                            parsed_report = {"descripcion_vlm": parsed_report, "alerta": False}
                    vlm_data_list.append(parsed_report)
            vlm_duration = time.time() - t_vlm_start
            
        return vlm_data_list, vlm_duration


    def _cleanup_temp_files(self, image_to_vlm, image_path):
        '''Libera espacio eliminando las imágenes anotadas temporales'''
        # Limpiaer frame temporal
        if self.delete_annotated_image and image_to_vlm != image_path:
            # Separar por comas por si es una secuencia, o iterar una sola ruta si es foto/vídeo
            for path_to_delete in image_to_vlm.split(','):
                clean_path = path_to_delete.strip()
                if os.path.exists(clean_path):
                    try:
                        os.remove(clean_path)
                    except OSError as e:
                        self.get_logger().error(f"Error borrando temporal {clean_path}: {e}")
    
        
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
            history_str = f"Número de personas detectadas: {len(detections)}\n"
            COLORS = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 0, 255)]
            COLOR_NAMES = ["ROJA", "AZUL", "VERDE", "AMARILLA", "MAGENTA"]
            
            for det in detections:
                trk_id = det["id"]
                bbox = det["bbox"]
                posture = det["posture"]
                
                # Sliding Window (Memoria FIFO de 3 frames)
                if trk_id not in self.tracking_memory:
                    self.tracking_memory[trk_id] = []
                self.tracking_memory[trk_id].append(posture)
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
        prefix = "ALERTA: " if final_alert else ""
        
        # Deduplicación y formateo limpio (Estilo Log)
        position_texts = [m.desc.strip() for m in pos_atr_list if m.desc.strip()]
        vlm_texts = [m.desc.strip() for m in vlm_atr_list if m.desc.strip()]
        
        # Filtrar los perceptores que no detectan nada
        empty_tokens = ["despejado", "despejada"]
        useful_vlms = [t for t in vlm_texts if not any(term in t.lower() for term in empty_tokens) and t != "."]
            
        # Caso base: Todos los modelos de posición ven 0 personas (o no hay) y no hay descripciones VLM útiles
        empty_position_models = all("0 personas" in t for t in position_texts) or not position_texts
        if empty_position_models and not useful_vlms:
            return f"{prefix}Despejado.", final_alert

        # Unir descripciones usando un punto como separador limpio
        parts = position_texts + useful_vlms
        combined_desc = f"{prefix}{'| '.join(parts)}"

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
        return json_response
    

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