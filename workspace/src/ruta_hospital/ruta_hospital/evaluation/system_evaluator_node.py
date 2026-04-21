#!/usr/bin/env python3
import os
import rclpy
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
from ament_index_python.packages import get_package_share_directory

from ruta_hospital.reporting.llm_reporter_node import LLMReporterNode
from ruta_hospital.evaluation.utils.ragas_evaluator import RagasEvaluator
from ruta_hospital.evaluation.base_evaluator import BaseEvaluatorNode

from hospital_interfaces.action import GenerateReport

PKG_DIR = get_package_share_directory('ruta_hospital')
DEFAULT_QUESTIONS_PATH = os.path.join(PKG_DIR, 'config', 'quest.json')
DEFAULT_EVAL_FOLDER = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/hospital_photos/vuelta_A/"

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

        quest_path = self.get_parameter('questions_path').get_parameter_value().string_value
        self.eval_folder_path = self.get_parameter('eval_folder_path').get_parameter_value().string_value
        
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

        mock_result = GenerateReport.Result()
        mock_goal_handle = MockGoalHandle()
        
        zone_groups = self.reporter_logic.validate_data(self.eval_folder_path, mock_result)
        if not zone_groups:
            response.success = False
            response.message = "Fallo validando los datos del directorio" # Captura el error
            return response
            
        self.get_logger().info("Extrayendo contexto de perceptores")
        global_context_json = await self.reporter_logic.process_each_image(zone_groups, mock_goal_handle, mock_result)
        
        if not global_context_json:
            response.success = False
            response.message = "Fallo en el procesamiento de imágenes en el perceptor"
            return response
        
        self.get_logger().info("Generando resumen global...")
        mock_result = self.reporter_logic.generate_global_summary(global_context_json, mock_result)
        
        if not mock_result.success:
            response.success = False
            response.message = "Fallo al generar el resumen global por lotes"
            return response
            
        pregenerated_summary = mock_result.final_report.replace("Informe generado:\n", "").strip() # quitarlo para evitar errores de ragas
        reduced_context = getattr(self.reporter_logic, 'last_reduced_context', None)
        self.get_logger().info("Generando respuestas...")

        try:
            self.ragas_evaluator.evaluate_system(
                global_context_json,
                pregenerated_summary=pregenerated_summary, # para poder reconstruir exactamente el mismo prompt
                reduced_context=reduced_context,
                config_name=self.evaluation_name
            )            
            response.success = True
            response.message = f"Evaluación Ragas completada con éxito. Guardado en: {self.metrics_dir}"
        except Exception as e:
            self.get_logger().error(f"Error durante Ragas: {e}")
            response.success = False
            response.message = f"Fallo en evaluación: {e}"
            
        return response

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