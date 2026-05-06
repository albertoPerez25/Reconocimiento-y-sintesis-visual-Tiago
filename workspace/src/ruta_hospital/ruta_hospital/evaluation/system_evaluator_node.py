#!/usr/bin/env python3
import os
import time
import rclpy
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
from ament_index_python.packages import get_package_share_directory

from ruta_hospital.reporting.llm_reporter_node import LLMReporterNode
from ruta_hospital.evaluation.utils.ragas_evaluator import RagasEvaluator
from ruta_hospital.evaluation.base_evaluator import BaseEvaluatorNode
from ruta_hospital.evaluation.base_evaluator import InferencePipelineError

from hospital_interfaces.action import GenerateReport

PKG_DIR = get_package_share_directory('ruta_hospital')
DEFAULT_QUESTIONS_PATH = os.path.join(PKG_DIR, 'config', 'quest.json')
DEFAULT_EVAL_FOLDER = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/hospital_photos/vuelta_A/"
DEFAULT_PERCEPTION_MODE = "image"

class MockGoalHandle:
    ''' Falso Goal Handle para reutilizar el código de LLMReporterNode
        sin necesidad de levantar un Action Server real en la evaluación. '''
    def __init__(self):
        self.is_cancel_requested = False

    def publish_feedback(self, msg):
        # Ignorar el feedback durante la evaluación en segundo plano
        pass

class SystemEvaluatorNode(BaseEvaluatorNode):
    def __init__(self):
        super().__init__('system_evaluator_node')
        # Reportero original para acceder a sus métodos
        self.reporter_logic = LLMReporterNode()

        # Parametros
        self.declare_parameter('questions_path', DEFAULT_QUESTIONS_PATH)
        self.declare_parameter('eval_folder_path', DEFAULT_EVAL_FOLDER)
        self.declare_parameter('perception_mode', DEFAULT_PERCEPTION_MODE)

        quest_path = self.get_parameter('questions_path').get_parameter_value().string_value
        self.eval_folder_path = self.get_parameter('eval_folder_path').get_parameter_value().string_value
        
        perception_mode = self.get_parameter('perception_mode').get_parameter_value().string_value
        self.reporter_logic.perception_mode = perception_mode

        self.metrics_dir = self.reporter_logic.metrics_dir # el mismo path de métricas
        self.ragas_evaluator = RagasEvaluator(
            quest_path, 
            self.metrics_dir, 
            self.ollama_params, 
            self.run_params, 
            self.get_logger()
        )
        
        # Servicio distinto para la evaluación
        self.eval_srv = self.create_service(
            Trigger, 
            'evaluate_patrol_system', 
            self.evaluate_callback,
            callback_group=self.reporter_logic.cb_group # Evita Deadlocks rehusando el grupo del reportero
        )
        self.get_logger().info("Nodo Evaluador listo. Llama al servicio '/evaluate_patrol_system'")

    async def evaluate_callback(self, request, response):
        self.get_logger().info("Iniciada Evaluación Ragas")
        total_init_time = time.time()
        inference_time = 0.0
        ragas_time = 0.0

        if self.evaluation_mode == "evaluate_only":
            short_dict, summary_dict = self.evaluate_only(request, response)
        else:
            short_dict, summary_dict = await self.inference_and_evaluate(request, response)

            if self.evaluation_mode == "generate_only":
                response.success = True
                response.message = f"Generación completada. Respuestas guardadas en {self.answers_file}"
                
                self.sync_metrics_from_reporter(inference_time, 0.0, total_init_time)
                self.save_metrics()
                return response

        try:
            self.ragas_evaluator.evaluate_system(
                short_dict=short_dict,
                summary_dict=summary_dict,
                config_name=self.evaluation_name
            )           
            response.success = True
            response.message = f"Evaluación Ragas completada con éxito. Guardado en: {self.metrics_dir}"
        
            self.sync_metrics_from_reporter(inference_time, ragas_time, total_init_time)
            self.save_metrics()
            
        except InferencePipelineError as e:
            self.get_logger().error(str(e))
            response.success = False
            response.message = str(e)
        
        except Exception as e:
            self.get_logger().error(f"Error inesperado durante la evaluación: {e}")
            response.success = False
            response.message = f"Fallo del sistema: {e}"
            
        return response
    
    def sync_metrics_from_reporter(self, inference_time, ragas_time, total_init_time):
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
    
    def evaluate_only(self, request, response):
        saved_data = self.load_intermediate_answers()
        if not saved_data or "short_dict" not in saved_data or "summary_dict" not in saved_data:
            response.success = False
            response.message = "Fallo cargando datos persistentes para evaluar."
            return response
        
        short_dict = saved_data["short_dict"]
        summary_dict = saved_data["summary_dict"]

        return short_dict,summary_dict
    
    async def inference_and_evaluate(self, request, response):
        mock_result = GenerateReport.Result()
        mock_goal_handle = MockGoalHandle()
        
        zone_groups = self.reporter_logic.validate_data(self.eval_folder_path, mock_result)
        if not zone_groups:
            raise InferencePipelineError("Fallo validando los datos del directorio")
            
        self.get_logger().info("Extrayendo contexto de perceptores")
        global_context_json = await self.reporter_logic.process_each_image(zone_groups, mock_goal_handle, mock_result)
        
        if not global_context_json:
            raise InferencePipelineError("Fallo en el procesamiento de imágenes en el perceptor")
        
        self.get_logger().info("Generando resumen global...")
        t_init_llm = time.time()
        mock_result = self.reporter_logic.generate_global_summary(global_context_json, mock_result)
        self.reporter_logic.current_metrics["tiempo_llm_segundos"] = round(time.time() - t_init_llm, 2)

        if not mock_result.success:
            raise InferencePipelineError("Fallo al generar el resumen global por lotes")
            
        pregenerated_summary = mock_result.final_report.replace("Informe generado:\n", "").strip() # quitarlo para evitar errores de ragas
        reduced_context = getattr(self.reporter_logic, 'last_reduced_context', None)
        
        self.get_logger().info("Generando respuestas LLM...")
        short_dict, summary_dict = self.ragas_evaluator.generate_answers(
            global_context_json,
            pregenerated_summary=pregenerated_summary,
            reduced_context=reduced_context
        )
        
        # Guardado intermedio si no es "evaluate_only"
        if self.evaluation_mode in ["generate_only", "full"]:
            self.save_intermediate_answers({"short_dict": short_dict, "summary_dict": summary_dict})
        
        return short_dict,summary_dict

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