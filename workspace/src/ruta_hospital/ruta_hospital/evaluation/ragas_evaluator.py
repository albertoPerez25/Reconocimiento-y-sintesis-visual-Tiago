import json
import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness, answer_relevancy
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.run_config import RunConfig
from ruta_hospital.commons.api_utils import call_ollama_api 

class OllamaParams:
    def __init__(self, ollama_url = "http://localhost:11434", evaluator_llm_model = "llama3", evaluator_embed_model = "nomic-embed-text"):
        self.ollama_url=ollama_url
        self.evaluator_llm_model = evaluator_llm_model
        self.evaluator_embed_model = evaluator_embed_model

class RagasEvaluator:
    def __init__(self, quest_path, metrics_dir, ollama_params):
        self.quest_path = quest_path
        self.metrics_dir = metrics_dir
        
        # LLM evaluador y embeddings requeridos por Ragas
        self.evaluator_llm = ChatOllama(model=ollama_params.evaluator_llm_model, 
                                        base_url=ollama_params.ollama_url, 
                                        temperature=0.0)# Evita que Llama-3 añada texto extra al JSON
        self.evaluator_embeddings = OllamaEmbeddings(model=ollama_params.evaluator_embed_model, base_url=ollama_params.ollama_url)

    def evaluate_system(self, global_context_json):
        '''Genera respuestas y ejecuta Ragas'''
        eval_dict = self.generate_answers(global_context_json)
        
        dataset = Dataset.from_dict(eval_dict)
        
        result = evaluate(
            dataset=dataset,
            metrics=[answer_correctness, answer_relevancy],
            llm=self.evaluator_llm,
            embeddings=self.evaluator_embeddings,
            run_config=RunConfig(max_workers=1, timeout=120)
        )
        
        output_path = os.path.join(self.metrics_dir, 'ragas_system_evaluation.csv')
        df_results = result.to_pandas()
        df_results.to_csv(output_path, index=False)
        return df_results

    def generate_answers(self, global_context_json):
        '''Usa el LLM para responder a las preguntas basándose solo en la patrulla'''
        with open(self.quest_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        eval_data = {"question": [], "answer": [], "ground_truth": []}

        for item in questions_data:
            question = item["question"]
            ground_truth = item["ground_truth"]
            
            prompt = f"""
            Eres un sistema analizador de actividades humanas en un hospital. 
            Basándote ÚNICAMENTE en este registro visual de tu patrulla:
            {global_context_json}
            
            Responde de forma breve y concisa a la siguiente pregunta. 
            Si no tienes información para responder, di "No hay información".
            
            Pregunta: {question}
            """
            
            llm_answer = call_ollama_api(
                "http://localhost:11434/api/generate", 
                {"model": "llama3", "prompt": prompt, "stream": False}
            )

            eval_data["question"].append(question)
            eval_data["answer"].append(llm_answer.strip())
            eval_data["ground_truth"].append(ground_truth)

        return eval_data
    
    def evaluate_perception(self, perception_data, model_name="perception_model"):
        '''Genera respuestas imagen por imagen y ejecuta Ragas para el perceptor'''
        eval_dict = self.generate_perception_answers(perception_data)
        
        dataset = Dataset.from_dict(eval_dict)
        
        result = evaluate(
            dataset=dataset,
            metrics=[answer_correctness, answer_relevancy],
            llm=self.evaluator_llm,
            embeddings=self.evaluator_embeddings,
            run_config=RunConfig(max_workers=1, timeout=120)
        )
        
        # CSV con el nombre del modelo que evaluado
        output_path = os.path.join(self.metrics_dir, f'ragas_eval_{model_name}.csv')
        df_results = result.to_pandas()
        df_results.to_csv(output_path, index=False)
        return df_results

    def generate_perception_answers(self, perception_data):
        '''Usa el LLM para responder basándose en el output de una sola imagen'''
        eval_data = {"question": [], "answer": [], "ground_truth": []}

        for item in perception_data:
            context = item["context"]
            question = item["question"]
            ground_truth = item["ground_truth"]
            
            prompt = f"""
            Eres un sistema analizador de actividades humanas en un hospital. 
            Basándote ÚNICAMENTE en este JSON generado por un modelo de visión artificial para una imagen:
            {context}
            
            Responde de forma breve y concisa a la siguiente pregunta. 
            Si el JSON dice "Despejado" y se pregunta por actividades, responde que no hay actividades.
            Si no tienes información para responder en el JSON, di "No hay información".
            
            Pregunta: {question}
            """
            
            llm_answer = call_ollama_api(
                "http://localhost:11434/api/generate", 
                {"model": "llama3", "prompt": prompt, "stream": False}
            )

            eval_data["question"].append(question)
            eval_data["answer"].append(llm_answer.strip())
            eval_data["ground_truth"].append(ground_truth)

        return eval_data