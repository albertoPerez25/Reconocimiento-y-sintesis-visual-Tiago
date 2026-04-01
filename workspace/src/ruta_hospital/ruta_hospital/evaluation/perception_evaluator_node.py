#!/usr/bin/env python3
import os
import json
import rclpy
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
from rclpy.callback_groups import ReentrantCallbackGroup
from ament_index_python.packages import get_package_share_directory

from hospital_interfaces.srv import AnalyzeActivity
from ruta_hospital.evaluation.ragas_evaluator import RagasEvaluator
from ruta_hospital.evaluation.base_evaluator import BaseEvaluatorNode

PKG_DIR = get_package_share_directory('ruta_hospital')
DEFAULT_DATASET_PATH = os.path.join(PKG_DIR, 'config', 'perception_dataset.json')
DEFAULT_IMAGES_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/test_dataset/"
DEFAULT_METRICS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"

class PerceptionEvaluatorNode(BaseEvaluatorNode):
    '''Nodo encargado de evaluar la agudeza visual de los modelos de percepción (YOLO/VLM) de forma aislada'''
    def __init__(self):
        super().__init__('perception_evaluator_node')

        self.declare_parameter('dataset_path', DEFAULT_DATASET_PATH)
        self.declare_parameter('images_dir', DEFAULT_IMAGES_DIR)
        self.declare_parameter('metrics_dir', DEFAULT_METRICS_DIR)
        self.declare_parameter('tested_model_name', 'unknown_model') # Para nombrar el CSV resultante

        # Extracción de parámetros

        self.dataset_path = self.get_parameter('dataset_path').get_parameter_value().string_value
        self.images_dir = self.get_parameter('images_dir').get_parameter_value().string_value
        self.metrics_dir = self.get_parameter('metrics_dir').get_parameter_value().string_value
        self.tested_model_name = self.get_parameter('tested_model_name').get_parameter_value().string_value

        # Evaluador RAGAS
        self.ragas_evaluator = RagasEvaluator(quest_path="", metrics_dir=self.metrics_dir, ollama_params=self.ollama_params, run_params=self.run_params)
        
        self.cb_group = ReentrantCallbackGroup() # Evitar Deadlocks. El de sistema usa el grupo del reportero, pero este no así que hay que crear otro grupo

        self.vision_cli = self.create_client(
            AnalyzeActivity, 
            'analyze_image',
            callback_group=self.cb_group
        )
        
        self.eval_srv = self.create_service( # servidor para iniciar la evaluacion
            Trigger, 
            'evaluate_perception_model', 
            self.evaluate_callback,
            callback_group=self.cb_group
        )
        
        self.get_logger().info(f"Evaluador de Percepción listo. Llama a '/evaluate_perception_model' para testear el modelo activo.")

    async def evaluate_callback(self, request, response):        
        '''Orquestador principal para la evaluación de percepción aislada'''
        
        if not self.vision_cli.wait_for_service(timeout_sec=5.0):
            response.success = False
            response.message = "Error: No hay ningún nodo de percepción activo en /analyze_image."
            return response

        dataset = self.load_dataset()
        if not dataset:
            response.success = False
            response.message = f"Error leyendo el dataset {self.dataset_path}"
            return response

        perception_data_for_ragas = await self.process_images(dataset)

        if not perception_data_for_ragas:
            response.success = False
            response.message = "No se pudo extraer ningún dato válido para evaluar."
            return response

        return self.run_ragas_evaluation(perception_data_for_ragas, response)

    def load_dataset(self):
        '''Carga el dataset de evaluación desde el archivo JSON'''
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.get_logger().error(f"Error leyendo el dataset {self.dataset_path}: {e}")
            return None

    async def process_images(self, dataset):
        '''Itera sobre las imágenes, llama al perceptor y formatea los datos para RAGAS'''    
        perception_data_for_ragas = []

        for image in dataset:
            img_name = image.get("image_name")
            questions = image.get("questions", [])
            img_path = os.path.join(self.images_dir, img_name)
            
            if not os.path.isfile(img_path):
                self.get_logger().warn(f"{img_path}: Imagen no encontrada")
                continue
                
            self.get_logger().info(f"Preguntando al perceptor sobre: {img_name}")
            
            # Llamada al servicio del perceptor
            req = AnalyzeActivity.Request()
            req.image_path = img_path
            
            try:
                result = await self.vision_cli.call_async(req)
                perceptor_output = result.report
            except Exception as e:
                self.get_logger().error(f"Fallo al analizar {img_name}: {e}")
                continue

            # Empaquetar las preguntas de la imagen y el output del modelo
            for q in questions:
                perception_data_for_ragas.append({
                    "context": perceptor_output,
                    "question": q["question"],
                    "ground_truth": q["ground_truth"]
                })

        return perception_data_for_ragas

    def run_ragas_evaluation(self, perception_data_for_ragas, response):
        '''Ejecuta la evaluación RAGAS y actualiza la respuesta del servicio ROS'''
        self.get_logger().info("Inferencia completada. Pasando resultados a RAGAS para su puntuación...")
        
        try:
            self.ragas_evaluator.evaluate_perception(perception_data_for_ragas, model_name=self.tested_model_name)
            response.success = True
            response.message = f"Evaluación VQA completada. CSV guardado como 'ragas_eval_{self.tested_model_name}.csv' en {self.metrics_dir}"
        except Exception as e:
            self.get_logger().error(f"Error durante Ragas: {e}")
            response.success = False
            response.message = f"Fallo en evaluación RAGAS: {e}"
            
        return response

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    eval_node = PerceptionEvaluatorNode()
    executor.add_node(eval_node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()