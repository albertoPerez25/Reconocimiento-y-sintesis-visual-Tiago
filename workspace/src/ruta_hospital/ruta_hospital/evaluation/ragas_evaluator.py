import json
import os
import re
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness, answer_relevancy, faithfulness, summarization_score
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.run_config import RunConfig
from ruta_hospital.commons.api_utils import call_ollama_api 

class OllamaParams:
    def __init__(self, ollama_url = "http://localhost:11434", evaluator_llm_model = "llama3", evaluator_embed_model = "nomic-embed-text"):
        self.ollama_url=ollama_url
        self.evaluator_llm_model = evaluator_llm_model
        self.evaluator_embed_model = evaluator_embed_model

class EvaluatorRunParams:
    def __init__(self, system_workers = 4, system_timeout = 420, perceptor_workers = 4, perceptors_timeout = 420):
        self.system_workers = system_workers
        self.system_timeout = system_timeout
        self.perceptors_workers = perceptor_workers
        self.perceptors_timeout = perceptors_timeout

class RagasEvaluator:
    def __init__(self, quest_path, metrics_dir, ollama_params, run_params, logger = None):
        self.quest_path = quest_path
        self.metrics_dir = metrics_dir
        self.run_params = run_params
        self.logger = logger
        
        # LLM evaluador y embeddings requeridos por Ragas
        self.evaluator_llm = ChatOllama(model=ollama_params.evaluator_llm_model, 
                                        base_url=ollama_params.ollama_url, 
                                        temperature=0.0, # Evita que Llama-3 añada texto extra al JSON
                                        format="json")
        self.evaluator_embeddings = OllamaEmbeddings(model=ollama_params.evaluator_embed_model, base_url=ollama_params.ollama_url)

    def evaluate_system(self, global_context_json, reporter_prompt_func=None):
        '''Genera respuestas y ejecuta Ragas'''
        short_dict, summary_dict = self.generate_answers(global_context_json, reporter_prompt_func)
        
        results_dfs = []
        
        # preguntas cortas 
        if short_dict["question"]:
            dataset_short = Dataset.from_dict(short_dict)
            result_short = evaluate(
                dataset=dataset_short,
                metrics=[answer_correctness, answer_relevancy, faithfulness],
                llm=self.evaluator_llm,
                embeddings=self.evaluator_embeddings,
                run_config=RunConfig(max_workers=self.run_params.perceptors_workers, 
                                     timeout=self.run_params.perceptors_timeout)
            )
            df_short = result_short.to_pandas()
            df_short['eval_type'] = 'short'
            results_dfs.append(df_short)

        # resumen 
        if summary_dict["question"]:
            dataset_summary = Dataset.from_dict(summary_dict)
            result_summary = evaluate(
                dataset=dataset_summary,
                metrics=[answer_correctness, faithfulness, summarization_score],
                llm=self.evaluator_llm,
                embeddings=self.evaluator_embeddings,
                run_config=RunConfig(max_workers=self.run_params.perceptors_workers, 
                                     timeout=self.run_params.perceptors_timeout),
                column_map={
                    "question": "question",
                    "answer": "answer",
                    "contexts": "contexts",
                    "ground_truth": "ground_truth",
                    "reference_contexts": "reference_contexts" # Necesario para esta columna, si no se pasa column_map no la encuentra (por algún motivo)
                }
            )
            df_summary = result_summary.to_pandas()
            df_summary['eval_type'] = 'summary'
            results_dfs.append(df_summary)

        if results_dfs:
            df_final = pd.concat(results_dfs, ignore_index=True)
            output_path = os.path.join(self.metrics_dir, 'ragas_system_evaluation.csv')
            df_final.to_csv(output_path, index=False)
            return df_final
        else:
            return pd.DataFrame()

    def generate_answers(self, global_context_json, reporter_prompt_func=None):
        '''Usa el LLM para responder a las preguntas basándose solo en la patrulla'''
        with open(self.quest_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        short_eval_data = {"question": [], "answer": [], "ground_truth": [], "contexts": []}
        summary_eval_data = {"question": [], "answer": [], "ground_truth": [], "contexts": [], "reference_contexts": []}

        for item in questions_data:
            question = item["question"]
            ground_truth = item["ground_truth"]
            question_type = item.get("type", "short") # asume short para retrocompatibilidad con archivos legacy
            
            if question_type == "summary" and (not question or str(question).strip() == ""):
                # Si la pregunta está vacía misma logica que el reportero
                if reporter_prompt_func:
                    prompt = reporter_prompt_func(global_context_json)
                else:
                    # Fallback
                    prompt = f"Genera un reporte de actividades humanas detectadas con estos datos: {global_context_json}"
                
                # Para RAGAS, es necesario que la columna "question" sea algo
                question_for_ragas = "Redacta el informe de seguridad global de la patrulla del hospital."
            
            else:
                prompt = f"""
                Eres un sistema analizador de actividades humanas en un hospital. 
                Basándote ÚNICAMENTE en este registro visual de tu patrulla:
                {global_context_json}
                
                Responde de forma breve y concisa a la siguiente pregunta.
                
                Pregunta: {question}
                """
                question_for_ragas = str(question)

            llm_answer = call_ollama_api(
                "http://localhost:11434/api/generate",
                {"model": "llama3", "prompt": prompt, "stream": False}
            )

            natural_context_full = self.format_context_for_ragas(global_context_json, filter_empty=False) # para poder evaluar correctamente el Faithfulness
            natural_context_filtered = self.format_context_for_ragas(global_context_json, filter_empty=True) # Para que Ragas o el LLM en resumen no se pierda 

            if question_type == "summary":
                summary_eval_data["question"].append(question_for_ragas)
                summary_eval_data["answer"].append(llm_answer.strip())
                summary_eval_data["ground_truth"].append(ground_truth)
                summary_eval_data["contexts"].append(natural_context_filtered) # para faithfulness
                summary_eval_data["reference_contexts"].append(natural_context_filtered) # para summarization_score. Texto original contra el que juzgar el resumen generado
                
                self.logger.debug(f"Resumen generado: {llm_answer.strip()}")
                self.logger.debug(f"Contexto original: {global_context_json}")

            else:
                relevant_contexts = self.get_relevant_context(natural_context_full, question.lower())

                short_eval_data["question"].append(question_for_ragas)
                short_eval_data["answer"].append(llm_answer.strip())
                short_eval_data["ground_truth"].append(ground_truth)
                short_eval_data["contexts"].append(relevant_contexts)
                
        return short_eval_data, summary_eval_data
    
    def evaluate_perception(self, perception_data, model_name="perception_model"):
        '''Genera respuestas imagen por imagen y ejecuta Ragas para el perceptor'''
        eval_dict = self.generate_perception_answers(perception_data)
        
        dataset = Dataset.from_dict(eval_dict)
        
        result = evaluate(
            dataset=dataset,
            metrics=[answer_correctness, faithfulness, answer_relevancy],
            llm=self.evaluator_llm,
            embeddings=self.evaluator_embeddings,
            run_config=RunConfig(max_workers=self.run_params.perceptors_workers, 
                                 timeout=self.run_params.perceptors_timeout)
        )
        
        # CSV con el nombre del modelo que evaluado
        output_path = os.path.join(self.metrics_dir, f'ragas_eval_{model_name}.csv')
        df_results = result.to_pandas()
        df_results.to_csv(output_path, index=False)
        return df_results

    def generate_perception_answers(self, perception_data):
        '''Usa el LLM para responder basándose en el output de una sola imagen'''
        eval_data = {"question": [], "answer": [], "ground_truth": [], "contexts": []}

        for item in perception_data:
            rag_context = item["rag_context"]
            perceptor_output = item["perceptor_output"]
            question = item["question"]
            ground_truth = item["ground_truth"]
            
            prompt = f"""
            Eres un sistema analizador de actividades humanas en un hospital. 
            Basándote ÚNICAMENTE en este JSON generado por un modelo de visión artificial para una imagen:
            {perceptor_output}
            
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
            eval_data["contexts"].append([rag_context]) # debe evaluar la fidelidad solo contra los datos inyectados del RAG

        return eval_data

    def format_context_for_ragas(self, json_context, filter_empty=False):
        '''Convierte el JSON de los perceptores en lenguaje natural para que RAGAS lo entienda'''
        try:
            data = json.loads(json_context)
            formatted_contexts = []
            
            if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()): #el json esta dividido en zonas
                for zone, info in data.items():
                    events = info.get("eventos_recientes", [])
                    if not events:
                        if not filter_empty:
                            formatted_contexts.append(f"La zona '{zone}' está despejada, sin eventos ni personas.")
                    else:
                        for ev in events:
                            desc = ev.get("descripcion_vlm", "sin descripción")
                            detection = "Se ha detectado actividad humana" if ev.get("alerta") else "No hay alertas ni peligros" # TODO
                            formatted_contexts.append(f"En la zona '{zone}': {desc}. {detection}.")
            

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