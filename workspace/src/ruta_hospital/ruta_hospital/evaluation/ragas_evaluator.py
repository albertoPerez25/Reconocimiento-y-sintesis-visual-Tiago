import json
import os
import re
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness, answer_relevancy, faithfulness
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
            metrics=[answer_correctness, answer_relevancy, faithfulness],
            llm=self.evaluator_llm,
            embeddings=self.evaluator_embeddings,
            run_config=RunConfig(max_workers=4, timeout=420)
        )
        
        output_path = os.path.join(self.metrics_dir, 'ragas_system_evaluation.csv')
        df_results = result.to_pandas()
        df_results.to_csv(output_path, index=False)
        return df_results

    def generate_answers(self, global_context_json):
        '''Usa el LLM para responder a las preguntas basándose solo en la patrulla'''
        with open(self.quest_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        eval_data = {"question": [], "answer": [], "ground_truth": [], "contexts": []}

        for item in questions_data:
            question = item["question"]
            ground_truth = item["ground_truth"]
            
            prompt = f"""
            Eres un sistema analizador de actividades humanas en un hospital. 
            Basándote ÚNICAMENTE en este registro visual de tu patrulla:
            {global_context_json}
            
            Responde de forma breve y concisa a la siguiente pregunta.
            
            Pregunta: {question}
            """
            
            llm_answer = call_ollama_api(
                "http://localhost:11434/api/generate", 
                {"model": "llama3", "prompt": prompt, "stream": False}
            )

            eval_data["question"].append(question)
            eval_data["answer"].append(llm_answer.strip())
            eval_data["ground_truth"].append(ground_truth)

            natural_language_context = self.format_context_for_ragas(global_context_json)
            relevant_contexts = self.get_relevant_context(natural_language_context, question.lower())
                
            eval_data["contexts"].append(relevant_contexts)

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
            run_config=RunConfig(max_workers=4, timeout=120)
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

    def format_context_for_ragas(self, json_context):
        '''Convierte el JSON de los perceptores en lenguaje natural para que RAGAS lo entienda'''
        try:
            data = json.loads(json_context)
            formatted_contexts = []
            
            if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()): #el json esta dividido en zonas
                for zone, info in data.items():
                    eventos = info.get("eventos_recientes", [])
                    if not eventos:
                        formatted_contexts.append(f"La zona '{zone}' está despejada, sin eventos ni personas.")
                    else:
                        for ev in eventos:
                            desc = ev.get("descripcion_vlm", "sin descripción")
                            alerta = "HAY UNA ALERTA O PELIGRO" if ev.get("alerta") else "No hay alertas ni peligros"
                            formatted_contexts.append(f"En la zona '{zone}': {desc}. {alerta}.")
            

            if not formatted_contexts:
                return ["El entorno está completamente despejado y sin incidencias."]
                
            return formatted_contexts
        except Exception:
            # texto plano encapsulado en una lista (lo que espera RAGAS)
            return [str(json_context).strip()]
        
    def get_relevant_context(self, natural_language_context, question_lower):
        '''Filtra el contexto y devuelve solo la zona relevante para facilitar el trabajo a RAGAS'''
        relevant_contexts = []
        for chunk in natural_language_context:
            match = re.search(r"'(.*?)'", chunk)
            if match:
                complete_zone = match.group(1).lower()
                # Cosas como "Recepción (cerca de X)"
                base_zone = complete_zone.split(" (")[0] 
                
                if base_zone in question_lower or complete_zone in question_lower:
                    relevant_contexts.append(chunk)
        
        if not relevant_contexts:
            relevant_contexts = natural_language_context

        return relevant_contexts