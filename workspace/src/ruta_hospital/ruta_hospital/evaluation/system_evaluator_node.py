#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger

from ruta_hospital.reporting.llm_reporter_node import LLMReporterNode
from ruta_hospital.evaluation.ragas_evaluator import RagasEvaluator

class SystemEvaluatorNode(Node):
    def __init__(self):
        super().__init__('system_evaluator_node')
        # Reportero original para acceder a sus métodos
        self.reporter_logic = LLMReporterNode()

        # Evaluador de Ragas
        ruta_quest = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/config/quest.json"
        self.metrics_dir = self.reporter_logic.metrics_dir # el mismo path de métricas
        self.ragas_evaluator = RagasEvaluator(ruta_quest, self.metrics_dir)
        
        # Servicio distinto para la evaluación
        self.eval_srv = self.create_service(
            Trigger, 
            'evaluate_patrol_system', 
            self.evaluate_callback,
            callback_group=self.reporter_logic.cb_group
        )
        self.get_logger().info("Nodo Evaluador listo. Llama al servicio '/evaluate_patrol_system'")

    async def evaluate_callback(self, request, response):
        self.get_logger().info("Iniciada Evaluación Ragas")
        
        zone_groups = self.reporter_logic.validate_data(response)
        if not zone_groups:
            return response
            
        self.get_logger().info("Extrayendo contexto de perceptores (YOLO/VLM)...")
        global_context_json = await self.reporter_logic.process_each_image(zone_groups, response)
        
        if not global_context_json or self.reporter_logic.abort_processing:
            return response
            
        self.get_logger().info("Generando respuestas...")
        try:
            self.ragas_evaluator.evaluate_system(global_context_json)
            
            response.success = True
            response.message = f"Evaluación Ragas completada con éxito. Revisa la carpeta de métricas: {self.metrics_dir}"
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