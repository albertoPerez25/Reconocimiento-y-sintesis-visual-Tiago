import json
import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness, answer_relevancy
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.run_config import RunConfig
from ruta_hospital.commons.api_utils import call_ollama_api 

class RagasEvaluator:
    def __init__(self, quest_path, metrics_dir, ollama_url="http://localhost:11434"):
        self.quest_path = quest_path
        self.metrics_dir = metrics_dir
        
        # LLM evaluador y embeddings requeridos por Ragas
        self.evaluator_llm = ChatOllama(model="llama3", base_url=ollama_url)
        self.evaluator_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

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
        
        df_results = result.to_pandas()
        output_path = os.path.join(self.metrics_dir, 'ragas_system_evaluation.csv')
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