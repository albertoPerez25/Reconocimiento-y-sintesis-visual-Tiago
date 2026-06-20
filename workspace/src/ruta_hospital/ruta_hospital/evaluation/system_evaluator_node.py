#!/usr/bin/env python3
import os
import time
import rclpy
import json
import time
import csv
from dataclasses import dataclass
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from ament_index_python.packages import get_package_share_directory

from ruta_hospital.reporting.llm_reporter_node import LLMReporterNode
from ruta_hospital.evaluation.utils.ragas_evaluator import RagasEvaluator
from ruta_hospital.evaluation.base_evaluator import BaseEvaluatorNode
from ruta_hospital.evaluation.base_evaluator import InferencePipelineError
from ruta_hospital.utils.shared.semantic_map_utils import load_semantic_map, get_zone_name
from hospital_interfaces.action import GenerateReport

PKG_DIR = get_package_share_directory('ruta_hospital')

DEFAULT_QUESTIONS_PATH = os.path.join(PKG_DIR, 'config', 'quest.json')
DEFAULT_EVAL_FOLDER = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/datasets/hospital_photos/vuelta_A/"
DEFAULT_PERCEPTION_MODE = "image"  # 'sequence' para VLM temporal, 'image' para YOLO foto a foto, 'video' para clips de video
DEFAULT_USE_RERANKER = False
DEFAULT_RESUME_SESSION = True
DEFAULT_EVAL_TARGET = "both" # 'short_only', 'summary_only', 'both'

@dataclass
class MockLiveCapture:
    '''Mensaje simulado idéntico al hospital_interfaces.msg.LiveCapture'''
    file_path: str
    zone_name: str
    timestamp: float

class MockGoalHandle:
    ''' Falso Goal Handle para reutilizar el código de LLMReporterNode
        sin necesidad de levantar un Action Server real en la evaluación. '''
    def __init__(self):
        self.is_cancel_requested = False

    def publish_feedback(self, msg):
        '''Ignorar el feedback durante la evaluación en segundo plano'''
        pass

    def succeed(self):
        '''Simula el reporte exitoso de la acción al cliente'''
        pass

    def abort(self):
        '''Simula la cancelación de la acción'''
        pass

class SystemEvaluatorNode(BaseEvaluatorNode):
    def __init__(self):
        super().__init__('system_evaluator_node')
        # Reportero original para acceder a sus métodos
        self.reporter_logic = LLMReporterNode()
        self.reporter_logic.eval_name = self.evaluation_name
        #self.reporter_logic.current_metrics["modelo_reportero"] = self.evaluation_name
        self.reporter_logic.keep_photos = True

        # Parametros
        self.declare_parameter('questions_path', DEFAULT_QUESTIONS_PATH)
        self.declare_parameter('eval_folder_path', DEFAULT_EVAL_FOLDER)
        self.declare_parameter('perception_mode', DEFAULT_PERCEPTION_MODE)
        self.declare_parameter('use_reranker', DEFAULT_USE_RERANKER)
        self.declare_parameter('resume_session', DEFAULT_RESUME_SESSION)
        self.declare_parameter('evaluation_target', DEFAULT_EVAL_TARGET) 

        quest_path = self.get_parameter('questions_path').get_parameter_value().string_value
        self.eval_folder_path = self.get_parameter('eval_folder_path').get_parameter_value().string_value
        
        perception_mode = self.get_parameter('perception_mode').get_parameter_value().string_value
        self.reporter_logic.perception_mode = perception_mode

        resume_session = self.get_parameter('resume_session').get_parameter_value().bool_value
        self.reporter_logic.resume_session = resume_session

        use_reranker = self.get_parameter('use_reranker').get_parameter_value().bool_value
        if use_reranker:
            self.reporter_logic.vector_manager.use_reranker = True
            self.reporter_logic.vector_manager.load_reranker_model_if_needed()

        self.evaluation_target = self.get_parameter('evaluation_target').get_parameter_value().string_value

        default_map_path = os.path.join(PKG_DIR, 'config', 'semantic_map.json')
        self.declare_parameter('semantic_map_path', default_map_path)
        semantic_map_path = self.get_parameter('semantic_map_path').get_parameter_value().string_value
        
        self.hospital_zones, self.reception_zone = load_semantic_map(semantic_map_path, self.get_logger())

        self.metrics_dir = self.reporter_logic.metrics_dir # el mismo path de métricas
        self.ragas_evaluator = RagasEvaluator(
            quest_path, 
            self.metrics_dir, 
            self.ollama_params, 
            self.run_params, 
            self.get_logger()
        )

        self.action_cb_group = ReentrantCallbackGroup()
        
        self._action_server = ActionServer(
            self,
            GenerateReport,
            '/evaluate_patrol_system',
            execute_callback=self.evaluate_callback, 
            callback_group=self.action_cb_group
        )
        
        self.get_logger().info("Nodo Evaluador listo. Llama al servicio '/evaluate_patrol_system'")

    async def evaluate_callback(self, goal_handle):
        '''Orquesta el flujo de evaluación completo: obtención de datos (inferencia o lectura de disco), 
        ejecución de RAGAS y actualización de métricas'''
        
        self.get_logger().info("Iniciada Evaluación Ragas")
        total_init_time = time.time()
        inference_time = 0.0
        ragas_time = 0.0

        # Instanciar el objeto de retorno oficial que exige la Acción
        result = GenerateReport.Result()

        try:
            if self.evaluation_mode == "evaluate_only":
                short_dict, summary_dict = self.get_data_for_evaluate_only()
            else:
                t_start_inference = time.time()
                short_dict, summary_dict = await self.get_data_for_inference_and_evaluate()

                if self.evaluation_mode == "generate_only":
                    inference_time = time.time() - t_start_inference
                    self.sync_metrics_from_reporter(inference_time, 0.0, total_init_time)
                    self.save_metrics()

                    goal_handle.succeed()
                    result.final_report = f"Generación completada. Respuestas guardadas en {self.answers_file}"
                    return result

            t_start_ragas = time.time()
            self.ragas_evaluator.evaluate_system(
                short_dict=short_dict,
                summary_dict=summary_dict,
                config_name=self.evaluation_name,
                target=self.evaluation_target
            )       
            ragas_time = time.time() - t_start_ragas
        
            self.sync_metrics_from_reporter(inference_time, ragas_time, total_init_time)
            self.save_metrics()

            goal_handle.succeed()
            result.final_report = f"Evaluación Ragas completada con éxito. Guardado en: {self.metrics_dir}"
            return result
            
        except InferencePipelineError as e:
            self.get_logger().error(str(e))
            goal_handle.abort()
            result.final_report = str(e)
            return result
        
        except Exception as e:
            self.get_logger().error(f"Error inesperado durante la evaluación: {e}")
            goal_handle.abort()
            result.final_report = f"Fallo del sistema: {e}"
            return result
                
    def sync_metrics_from_reporter(self, inference_time, ragas_time, total_init_time):
        '''Sincroniza y consolida las métricas de rendimiento y ejecución obtenidas desde el nodo reportero 
        instanciado.'''

        rep_metrics = self.reporter_logic.current_metrics
        
        # tiempos y contadores
        self.current_metrics["total_imagenes_procesadas"] = rep_metrics.get("total_imagenes_procesadas", 0)
        self.current_metrics["tiempo_percepcion_segundos"] = rep_metrics.get("tiempo_percepcion_segundos", 0.0)
        self.current_metrics["tiempo_llm_segundos"] = rep_metrics.get("tiempo_llm_segundos", 0.0)
        
        # verbosidad
        self.current_metrics["caracteres_contexto_visual"] = rep_metrics.get("caracteres_contexto_visual", 0)
        self.current_metrics["caracteres_informe_final"] = rep_metrics.get("caracteres_informe_final", 0)
        
        self.current_metrics["tiempo_inferencia_total_segundos"] = inference_time
        self.current_metrics["tiempo_ragas_evaluacion_segundos"] = ragas_time
        self.current_metrics["tiempo_total_ejecucion_segundos"] = round(time.time() - total_init_time, 2)
    
    def get_data_for_evaluate_only(self):
        '''Carga y devuelve los diccionarios de evaluación intermedios desde el disco para una ejecución rápida 
        de métricas RAGAS sin inferencia'''

        saved_data = self.load_intermediate_answers()
        if not saved_data or "short_dict" not in saved_data or "summary_dict" not in saved_data:
            raise InferencePipelineError("Fallo cargando las respuestas del LLM a evaluar")
        
        short_dict = saved_data["short_dict"]
        summary_dict = saved_data["summary_dict"]

        return short_dict,summary_dict
    
    async def get_data_for_inference_and_evaluate(self): 
        '''Simula el ciclo completo inyectando eventos en tiempo real al reportero de producción'''
        
        faiss_index_file = os.path.join(self.reporter_logic.vector_manager.faiss_path, "index.faiss")
        existe_faiss = os.path.exists(faiss_index_file)
        skip_inference = self.reporter_logic.resume_session and existe_faiss

        if not skip_inference:
            summary_text = await self._run_patrol_simulation()
        else:
            self.get_logger().info("Resume Session activo y FAISS detectado. Saltando simulación de perceptores...")
            # Forzar carga de FAISS a la RAM
            self.reporter_logic.vector_manager.get_highest_round_in_disk()
            summary_text = self.reporter_logic.latest_final_summary

        return self._generate_ragas_answers(summary_text)
    

    async def _run_patrol_simulation(self):
        '''Sub-orquestador: Prepara el entorno, inyecta los eventos y consolida el informe.'''
        valid_rows = self._prepare_and_read_dataset()
        await self._inject_dataset_events(valid_rows)
        return await self._consolidate_patrol_report()
    

    def _prepare_and_read_dataset(self):
        '''Prepara el entorno limpiando la caché y lee las filas válidas del CSV.'''
        self.reporter_logic.vector_manager.clear_all_data()
        self.get_logger().info("Limpieza de base vectorial ejecutada")
        
        # El reportero en producción empieza en 0 y suma 1 al consolidar. Lo alineamos.
        self.reporter_logic.current_round = 0 
            
        self.get_logger().info(f"Simulando patrulla leyendo dataset: {self.eval_folder_path}")
        if not os.path.exists(self.eval_folder_path):
            raise InferencePipelineError(f"Directorio de evaluación no encontrado: {self.eval_folder_path}")
            
        csv_path = os.path.join(self.eval_folder_path, "metadata.csv")
        if not os.path.exists(csv_path):
            raise InferencePipelineError(f"Falta el archivo metadata.csv en {self.eval_folder_path}. Es necesario para ubicar las fotos en el mapa.")

        with open(csv_path, mode='r') as file:
            reader = csv.reader(file)
            valid_rows = [row for row in reader if row and len(row) >= 5]
            
        if not valid_rows:
            raise InferencePipelineError(f"El archivo {csv_path} no contiene datos válidos.")
            
        return valid_rows
    

    async def _inject_dataset_events(self, valid_rows):
        '''Itera sobre las filas del CSV, simula las capturas y las inyecta en el reportero.'''
        timestamp_counter = 0.0
        processed_files = 0
        n_files = len(valid_rows)
        
        for row in valid_rows:
            # BARRA DE PROGRESO
            percent = processed_files / n_files
            chunks = int(percent * 30) # Tamaño de la barra (30 caracteres)
            bar = '█' * chunks + '-' * (30 - chunks)
            
            # print con \r para sobrescribir la misma línea en la terminal
            print(f'\r\033[94mImágenes Procesadas\033[0m |{bar}| {processed_files}/{n_files} ({(percent*100):.1f}%)', end='', flush=True)

            file_name = row[0]
            try:
                # Extraer coordenadas de la fila (Formato: nombre, t_sec, t_nano, pos_x, pos_y...)
                x = float(row[3])
                y = float(row[4])
            except ValueError:
                continue # Saltar la cabecera si la hubiera

            img_path = os.path.join(self.eval_folder_path, file_name)
            if not os.path.isfile(img_path):
                self.get_logger().warn(f"Imagen listada en CSV pero no encontrada en disco: {file_name}")
                continue
            
            zone_name = get_zone_name([x, y], self.hospital_zones, self.reception_zone)
            mock_msg = MockLiveCapture(file_path=img_path, zone_name=zone_name, timestamp=timestamp_counter)
            
            await self.reporter_logic.async_live_capture_callback(mock_msg)
            timestamp_counter += 1.0
            processed_files += 1

        if processed_files == 0:
            raise InferencePipelineError(f"No se procesó ninguna imagen/vídeo del CSV en: {self.eval_folder_path}.")
        
        print() # Salto de línea para no pisar la barra de progreso
        self.get_logger().debug(f"Se han inyectado {processed_files} eventos en FAISS exitosamente.")


    async def _consolidate_patrol_report(self):
        '''Simula el fin de la vuelta llamando al callback del reportero y mide tiempos.'''
        mock_goal_handle = MockGoalHandle()
        
        self.get_logger().debug("Fin de patrulla simulado. Consolidando informe y volcando a disco...")
        t_init_llm = time.time()
        
        # Volcará los .txt a disco y usará LangChain para el resumen.
        result = await self.reporter_logic.execute_report_callback(mock_goal_handle)
        
        self.reporter_logic.current_metrics["tiempo_llm_segundos"] = round(time.time() - t_init_llm, 2)

        if not result.success:
            raise InferencePipelineError("Fallo al generar el resumen global por lotes")
            
        return result.final_report


    def _generate_ragas_answers(self, summary_text):
        '''Prepara el contexto limpio y ejecuta la generación de respuestas de RAGAS.'''
        pregenerated_summary = summary_text.replace("Informe generado:\n", "").strip()

        self.get_logger().info("Generando respuestas LLM para evaluación RAGAS...")
        
        # Recupera la "foto en RAM" exacta que usó el LLM
        hospital_data_dict = json.loads(self.reporter_logic.latest_global_context)
        
        # Parseo limpio para no penalizar 'context_precision' con ruido JSON
        context_texts = []
        for zone, info in hospital_data_dict.items():
            if info.get("eventos_recientes"):
                context_texts.append(f"ZONA: {zone}\n{json.dumps(info, ensure_ascii=False)}")
            else:
                context_texts.append(f"ZONA: {zone}\nSin eventos detectados, despejada.")
        global_context_clean_text = "\n\n".join(context_texts)

        self.current_metrics["caracteres_contexto_visual"] = len(global_context_clean_text)
        t_init_llm = time.time()

        short_dict, summary_dict = self.ragas_evaluator.generate_answers(
            vector_manager=self.reporter_logic.vector_manager,
            global_context_json=global_context_clean_text, 
            pregenerated_summary=pregenerated_summary,
            target=self.evaluation_target
        )

        t_end_llm = time.time()
        self.current_metrics["tiempo_llm_segundos"] = round(t_end_llm - t_init_llm, 2)
        self.current_metrics["tiempo_inferencia_total_segundos"] = self.current_metrics["tiempo_llm_segundos"]

        # Métricas de la patrulla del reportero
        self.current_metrics["tiempo_percepcion_segundos"] = self.reporter_logic.current_metrics.get("tiempo_percepcion_segundos", 0.0)
        self.current_metrics["total_imagenes_procesadas"] = self.reporter_logic.current_metrics.get("total_imagenes_procesadas", 0)
        
        total_chars = 0
        if short_dict:
            total_chars += sum(len(str(ans)) for ans in short_dict.values())
        if summary_dict:
            total_chars += sum(len(str(ans)) for ans in summary_dict.values())
        self.current_metrics["caracteres_informe_final"] = total_chars
        
        if self.evaluation_mode in ["generate_only", "full"]:
            self.save_intermediate_answers({"short_dict": short_dict, "summary_dict": summary_dict})
        
        return short_dict, summary_dict
    
def main(args=None):
    rclpy.init(args=args)
    
    executor = MultiThreadedExecutor()
    eval_node = SystemEvaluatorNode()
    
    # Como tienen llamadas asíncronas, es necesario añadir tanto el nodo contenedor (eval_node) 
    # como el nodo reportero instanciado (reporter_logic) al executor, para evitar que 
    # sus clientes asíncronos se queden bloqueados.
    executor.add_node(eval_node)
    executor.add_node(eval_node.reporter_logic)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()