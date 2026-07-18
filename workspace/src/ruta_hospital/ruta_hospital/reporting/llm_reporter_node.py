#!/usr/bin/env python3
import os
import time
import rclpy
import json
import threading
from hospital_interfaces.msg import LiveCapture, Alarm 
from rclpy.executors import MultiThreadedExecutor
from hospital_interfaces.srv import AnalyzeActivity
from hospital_interfaces.action import GenerateReport
from hospital_interfaces.srv import GetPatrolContext
from ruta_hospital.reporting.base_reporter import BaseReporterNode
from ruta_hospital.utils.shared.vector_manager import VectorManager

from ruta_hospital.reporting.utils.perception_strategies import (
    SequencePerceptionStrategy, 
    ImagePerceptionStrategy, 
    VideoPerceptionStrategy
)

DEFAULT_PERCEPTION_MODE = 'image' # 'sequence' para VLM temporal, 'image' para YOLO foto a foto, 'video' para clips de video

class LLMReporterNode(BaseReporterNode):
    def __init__(self):
        super().__init__('llm_reporter_node')
        self.declare_parameter('perception_mode', DEFAULT_PERCEPTION_MODE) 
        self.perception_mode = self.get_parameter('perception_mode').get_parameter_value().string_value     
        self.vision_cli = self.create_client(AnalyzeActivity, 'analyze_image', callback_group=self.cb_group)
        ollama_base_url = self.ollama_url.split('/api')[0] if '/api' in self.ollama_url else self.ollama_url
        
        # Gestor de FAISS y LangChain
        self.vector_manager = VectorManager(
            base_dir=self.rag_dir,
            ollama_url=ollama_base_url,
            llm_model=self.llm_model,
            max_stored_rounds=self.max_stored_rounds,
            use_reranker=self.use_reranker,
            enforce_zone_match=self.enforce_zone_match,
            max_words=self.max_words,
            logger=self.get_logger()
        )
        self.patrol_start_time = time.time()

        self.alarm_counters = {}
        self.alarm_counters_lock = threading.Lock()

        self.manage_init_data()

        self.live_patrol_data = {}
        self.data_lock = threading.Lock() # Protección para MultiThreadedExecutor
        self.active_zone = None # Tracker de estado para transiciones de zona

        self.capture_sub = self.create_subscription(
            LiveCapture,
            '/hospital/live_captures',
            self.live_capture_callback,
            10,
            callback_group=self.cb_group
        )
        self.get_logger().debug("Suscrito a stream en /hospital/live_captures")

        self.alarm_pub = self.create_publisher(Alarm, '/hospital/alarms', 10)
        self.get_logger().debug("Publicador de alarmas inicializado en /hospital/alarms")

        self.context_srv = self.create_service(
            GetPatrolContext, 
            'get_patrol_context', 
            self.get_context_callback
        )
        
        # Estrategia como composición
        if self.perception_mode == "sequence":
            self.get_logger().info("MODO SECUENCIA DE IMAGENES")
            self.perception_strategy = SequencePerceptionStrategy(self.vision_cli, self)
        elif self.perception_mode == "video":
            self.get_logger().info("MODO CLIPS DE VIDEO")
            self.perception_strategy = VideoPerceptionStrategy(self.vision_cli, self)
        else:
            self.get_logger().info("MODO IMAGENES INDIVIDUALES")
            self.perception_strategy = ImagePerceptionStrategy(self.vision_cli, self)

    def manage_init_data(self):
        if self.resume_session:
            self.vector_manager.clear_all_data(force_clear=False)
            self.current_round = self.vector_manager.get_highest_round_in_disk()
            if self.current_round > 0:
                self.get_logger().info(f"Sesión Reanudada. Retomando la memoria FAISS en la vuelta: {self.current_round}")
            
            # Cargar el último resumen si existe
            self.latest_final_summary = self.vector_manager.get_latest_summary()
            
            if "No hay un resumen" not in self.latest_final_summary and self.current_round > 0:
                recovered_data = self.vector_manager.load_round_data_from_disk(self.current_round)
                self.latest_global_context = json.dumps(recovered_data, ensure_ascii=False)
            else:
                self.latest_global_context = ""
        else:
            self.vector_manager.clear_all_data(force_clear=True)
            self.current_round = 0  # Contador interno de vueltas para el Temporal RAG 
            self.latest_global_context = ""
            self.latest_final_summary = ""

    def publish_alarm(self, zone_name, event_data):
        '''
        Construye y publica un JSON en la red ROS 2 
        cuando se detecta una situación de peligro vital o violación grave.
        '''
        alarm_msg = Alarm()
        alarm_msg.event_type = "ALERTA_CRITICA"
        alarm_msg.zone_name = zone_name
        alarm_msg.description = event_data.get("descripcion_vlm", "Peligro desconocido")
        
        # Limpiar la 's' del final y forzar el tipo float
        raw_time = str(event_data.get("tiempo", time.time()))
        alarm_msg.timestamp = float(raw_time.replace("s", "").strip())
        
        self.alarm_pub.publish(alarm_msg)
        self.get_logger().warn(f"ALERTA ACTIVADA [{zone_name}]: {alarm_msg.description}")


    def get_context_callback(self, request, response):
        response.global_context = self.latest_global_context
        response.final_summary = self.latest_final_summary
        response.success = (self.latest_global_context != "")
        return response


    async def execute_report_callback(self, goal_handle):
        '''Cierra la vuelta actual leyendo el estado vivo y generando el resumen final LLM'''
        self.get_logger().info("Vuelta terminada. Iniciando consolidación del informe...")
        result = GenerateReport.Result()
        
        with self.data_lock:
            # Forzar la salida de la última zona patrullada
            if getattr(self, 'active_zone', None) is not None:
                last_zone = self.active_zone
                if last_zone in self.live_patrol_data:
                    last_zone_data = self.live_patrol_data[last_zone]
                    if not last_zone_data["eventos_recientes"] and last_zone_data.get("cleared_vector_id") is None:
                        empty_event = {
                            "tiempo": f"{time.time()}s",
                            "descripcion_vlm": "Zona completamente vacía y despejada. No se ha detectado ninguna persona, ni pacientes, ni personal, ni ninguna otra actividad humana.",
                            "alerta": False,
                            "tipo_zona": last_zone_data.get("tipo_zona", "Desconocida")
                        }
                        last_zone_data["eventos_recientes"].append(empty_event)
                        self.vector_manager.add_single_event_to_index(last_zone, empty_event, self.current_round + 1)
            
            self.active_zone = None

            hospital_data_dict = json.loads(json.dumps(self.live_patrol_data))
            self.live_patrol_data.clear()
            self.current_round += 1

        if not hospital_data_dict:
            self.get_logger().info("La patrulla ha finalizado sin incidentes. Generando informe de seguridad limpio...")
        
        thread_output = {"summary_text": "", "llm_time": 0.0}
        t_init_llm = time.time() # TODO: 

        def worker():
            # Volcado a disco para Debug y la barra lateral de Streamlit
            self.vector_manager.dump_round_data_to_disk(self.current_round, hospital_data_dict)
            
            # Generación del resumen global in-memory con LangChain
            t_start_llm = time.time()
            summary_text = self.vector_manager.generate_global_summary(hospital_data_dict, self.current_round)

            thread_output["llm_time"] = time.time() - t_start_llm
            thread_output["summary_text"] = summary_text

        # Delegación multihilo nativa
        llm_thread = threading.Thread(target=worker)
        llm_thread.start()

        while llm_thread.is_alive():
            time.sleep(0.1)

        llm_thread.join()

        summary_text = thread_output["summary_text"]

        self.latest_global_context = json.dumps(hospital_data_dict)
        self.latest_final_summary = summary_text
        
        result.success = True if "Error" not in summary_text else False
        result.final_report = f"Informe generado:\n{summary_text}"
        
        self.current_metrics["tiempo_llm_segundos"] = round(thread_output["llm_time"], 2)
        self.current_metrics["tiempo_total_segundos"] = round(time.time() - self.patrol_start_time, 2)
        
        self.current_metrics["caracteres_contexto_visual"] = len(json.dumps(hospital_data_dict, ensure_ascii=False))
        self.current_metrics["caracteres_informe_final"] = len(summary_text)
        
        self.save_metrics()
        self.patrol_start_time = time.time()

        self.get_logger().info(f"\n\n\tINFORME FINAL LANGCHAIN\n{summary_text}\n")
        goal_handle.succeed()
        return result
    
    
    def live_capture_callback(self, msg):
        '''
        Callback síncrono que delega el trabajo asíncrono
        al MultiThreadedExecutor de ROS 2
        '''
        if self.executor:
            self.executor.create_task(self.async_live_capture_callback(msg))
        else:
            self.get_logger().error("No se encontró un executor para lanzar la tarea asíncrona.")
    
    async def async_live_capture_callback(self, msg):
        '''Procesa una imagen/evento en el instante en que el robot la publica'''
        try:
            image_path = msg.file_path
            zone_name = msg.zone_name
            timestamp = msg.timestamp

            zone_type, local_zone_data, captured_round = self._prepare_local_zone_data(zone_name)

            # Lógica de salida
            with self.data_lock:
                if getattr(self, 'active_zone', None) is not None and self.active_zone != zone_name:
                    old_zone = self.active_zone
                    if old_zone in self.live_patrol_data:
                        old_zone_data = self.live_patrol_data[old_zone]
                        # Si la zona anterior está vacía y no se ha inyectado aún el vector sintético
                        if not old_zone_data["eventos_recientes"] and old_zone_data.get("cleared_vector_id") is None:
                            empty_event = {
                                "tiempo": f"{timestamp}s",
                                "descripcion_vlm": "Zona completamente vacía y despejada. No se ha detectado ninguna persona, ni pacientes, ni personal, ni ninguna otra actividad humana.",
                                "alerta": False,
                                "tipo_zona": old_zone_data.get("tipo_zona", "Desconocida")
                            }

                            # Modificar la variable de memoria
                            old_zone_data["eventos_recientes"].append(empty_event)

                            # Inyectar y guardar el ID devuelto
                            inserted_ids = self.vector_manager.add_single_event_to_index(old_zone, empty_event, captured_round)
                            if inserted_ids and len(inserted_ids) > 0:
                                old_zone_data["cleared_vector_id"] = inserted_ids[0]
                
                # Actualizar la zona activa
                self.active_zone = zone_name

            # Empaquetar como mock para respetar la firma de las estrategias SOTA
            images_mock = [{'path': image_path, 'time': timestamp}]

            # inferencia asíncrona
            has_activity = await self.perception_strategy.process(
                images_mock, zone_name, local_zone_data, captured_round, goal_handle=None
            )

            # Si hay actividad válida, se guarda en FAISS y memoria
            if has_activity and local_zone_data["eventos_recientes"]:
                with self.data_lock:
                    self.current_metrics["zonas_con_output"] = self.current_metrics.get("zonas_con_output", 0) + 1
                self._register_and_evaluate_event(zone_name, zone_type, local_zone_data, captured_round)
            else:
                with self.data_lock:
                    self.current_metrics["zonas_despejadas"] = self.current_metrics.get("zonas_despejadas", 0) + 1

        except Exception as e:
            self.get_logger().error(f"Error procesando captura en tiempo real: {e}")


    def _prepare_local_zone_data(self, zone_name):
        '''Obtiene metadatos y prepara el contexto thread-safe para la zona'''
        # Obtención de metadatos fuera del lock (evita bloqueos si hace llamadas E/S de ROS 2)
        zone_info = self.get_zone_metadata(zone_name)
        zone_type = zone_info.get("tipo_zona", "Desconocida")

        # Asegurar la existencia de la zona en memoria viva de forma thread-safe
        with self.data_lock:
            if zone_name not in self.live_patrol_data:
                self.live_patrol_data[zone_name] = {
                    "nombre_zona": zone_name,
                    "tipo_zona": zone_type,
                    "eventos_recientes": [],
                    "cleared_vector_id": None
                }
            # Snapshot: El historial intacto al VLM para que mantenga el contexto RAG temporal,
            # pero se desvincula del diccionario original
            local_zone_data = json.loads(json.dumps(self.live_patrol_data[zone_name]))
            captured_round = self.current_round + 1

        return zone_type, local_zone_data, captured_round


    def _register_and_evaluate_event(self, zone_name, zone_type, local_zone_data, captured_round):
        '''Extrae el evento, lo guarda en memoria y FAISS, y dispara alarmas si es crítico'''
        # La estrategia siempre adjunta el nuevo evento al final de la lista proporcionada
        last_event = local_zone_data["eventos_recientes"][-1]

        with self.data_lock:
            # Si execute_report_callback vació la memoria general durante el await, 
            # se reinicializa limpiamente para la nueva vuelta
            if zone_name not in self.live_patrol_data:
                self.live_patrol_data[zone_name] = {
                    "nombre_zona": zone_name,
                    "tipo_zona": zone_type,
                    "eventos_recientes": []
                }
            
            # Borrar vector de zona despejada si existía
            if self.live_patrol_data[zone_name].get("cleared_vector_id") is not None:
                vector_id = self.live_patrol_data[zone_name]["cleared_vector_id"]
                self.vector_manager.remove_single_event_from_index(vector_id)
                self.live_patrol_data[zone_name]["cleared_vector_id"] = None

            # añadir solo el evento nuevo a la memoria global
            self.live_patrol_data[zone_name]["eventos_recientes"].append(last_event)
            
            # Ingesta en FAISS Sincronizada (previene corromper index.faiss)
            self.vector_manager.add_single_event_to_index(zone_name, last_event, captured_round)

        # PUBLICACIÓN DE ALARMAS fuera del lock para mantener baja la latencia de hilos
        if last_event.get("alerta"):
            self.publish_alarm(zone_name, last_event)

    def get_next_alarm_id(self, round_num):
        '''Genera un ID secuencial (1, 2, 3...) para las carpetas de alarma de cada vuelta'''
        with self.alarm_counters_lock:
            if round_num not in self.alarm_counters:
                self.alarm_counters[round_num] = 1
            else:
                self.alarm_counters[round_num] += 1
            return self.alarm_counters[round_num]
    

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor() 
    executor.add_node(LLMReporterNode())
    try: 
        executor.spin()
    except KeyboardInterrupt: 
        pass
    finally: 
        rclpy.shutdown()

if __name__ == '__main__': 
    main()