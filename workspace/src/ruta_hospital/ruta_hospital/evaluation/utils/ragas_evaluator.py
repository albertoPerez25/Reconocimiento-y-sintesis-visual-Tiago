import json
import os
import re
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_correctness, 
    answer_relevancy, 
    faithfulness, 
    summarization_score,
    context_precision,
    context_recall,
    context_entity_recall,
    answer_similarity,
    _noise_sensitivity,
    AspectCritic
)
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.run_config import RunConfig
from ruta_hospital.utils.commons.api_utils import call_ollama_api 
from ruta_hospital.utils.shared import vector_manager

# Metricas custom que no usan LLMs
from ruta_hospital.evaluation.utils.custom_metrics import RougeScoreMetric, HHEMFidelity, BERTScoreMetric
rouge_metric = RougeScoreMetric()
hhem_metric = HHEMFidelity()
bert_metric = BERTScoreMetric()

class OllamaParams:
    def __init__(self, ollama_url = "http://localhost:11434", 
                 evaluator_llm_model = "llama3", 
                 evaluator_embed_model = "nomic-embed-text", 
                 api_key=None,
                 provider="local"):
        
        self.ollama_url=ollama_url
        self.evaluator_llm_model = evaluator_llm_model
        self.evaluator_embed_model = evaluator_embed_model
        #self.reporter_llm_model = None 

        # Preparado para APIs cloud # TODO
        self.api_key = api_key
        self.provider = provider

class EvaluatorRunParams:
    def __init__(self, system_workers = 4, system_timeout = 420, perceptor_workers = 4, perceptors_timeout = 420, max_words = 300, max_stored_rounds = 5):
        self.system_workers = system_workers
        self.system_timeout = system_timeout
        self.perceptors_workers = perceptor_workers
        self.perceptors_timeout = perceptors_timeout
        self.max_words = max_words
        self.max_stored_rounds = max_stored_rounds

class EvalContext:
    def __init__(self, global_json, pregenerated_summary=None, reduced_context=None):
        self.global_json = global_json
        self.pregenerated_summary = pregenerated_summary
        self.reduced_context = reduced_context

class RagasEvaluator:
    def __init__(self, quest_path, metrics_dir, ollama_params, run_params, logger = None):
        self.quest_path = quest_path
        self.metrics_dir = metrics_dir
        self.ollama_params = ollama_params
        self.run_params = run_params
        self.logger = logger
        
        # LLM evaluador y embeddings requeridos por Ragas
        self.evaluator_llm = ChatOllama(model=ollama_params.evaluator_llm_model, 
                                        base_url=ollama_params.ollama_url, 
                                        temperature=0.0, # Evita que Llama-3 añada texto extra al JSON
                                        num_ctx=4096, #8192 # aumentado del default (2048) para intentar evitar errores summary (contexto grande)
                                        seed=42 
                                        )#format="json" quitado para intentar evitar errores en el summary
        self.evaluator_embeddings = OllamaEmbeddings(model=ollama_params.evaluator_embed_model, base_url=ollama_params.ollama_url)

    def evaluate_system(self, short_dict, summary_dict, config_name="", target='both'):
        '''Genera respuestas y ejecuta Ragas'''
        # El nombre se inyecta justo antes de evaluar garantizando que esté actualizado
        for d in [short_dict, summary_dict]: 
            if d.get("question"):
                d["evaluation_name"] = [config_name] * len(d["question"])
        results_dfs = []
        
        # Evaluar preguntas cortas
        short_metrics = [
            answer_correctness, 
            answer_relevancy, 
            faithfulness,
            context_precision,
            context_recall,
            context_entity_recall,
            #_noise_sensitivity # TODO: Comprobar si aumenta demasiado el tiempo de evaluación
        ]
        
        df_short = None
        if target in ['both', 'short_only']:
            df_short = self.run_evaluation_subset(
                data_dict=short_dict,
                metrics=short_metrics,
                eval_type_name='short',
                config_name=config_name
            )
        if df_short is not None:
            results_dfs.append(df_short)

        # Evaluar resumen
        df_summary = None
        if target in ['both', 'summary_only']: 
            
            summary_metrics = [
                answer_similarity,    # Ragas Nativo (Semántica por Embeddings)
                rouge_metric,         # Cobertura algorítmica (Sustituto de context_recall)
                hhem_metric,           # Fidelidad NLI (Sustituto de los Critics de Ragas)
                bert_metric,
                #context_recall, 
                #context_entity_recall, 
                #faithfulness          # Funciona a veces 
                #summarization_score # da timeout haga lo que haga
            ]

            df_summary = self.run_evaluation_subset(
                data_dict=summary_dict,
                metrics=summary_metrics, # faithfulness y answer_correctness no funciona, ni su reemplazo aspect critic
                eval_type_name='summary',
                config_name=config_name
            )
            if df_summary is not None and not df_summary.empty:
                results_dfs.append(df_summary)

        if results_dfs:
            df_final = pd.concat(results_dfs, ignore_index=True)
            output_path = os.path.join(self.metrics_dir, f"ragas_{config_name}_system_evaluation.csv")
            df_final.to_csv(output_path, index=False)
            return df_final
        else:
            return pd.DataFrame()
        
    def run_evaluation_subset(self, data_dict, metrics, eval_type_name, config_name, column_map=None):
        '''Convierte un diccionario a Dataset, ejecuta RAGAS y devuelve un DataFrame etiquetado'''
        if not data_dict.get("question"):
            return None
            
        dataset = Dataset.from_dict(data_dict)
        
        # Preparar argumentos base
        kwargs = {
            "dataset": dataset,
            "metrics": metrics,
            "llm": self.evaluator_llm,
            "embeddings": self.evaluator_embeddings,
            "run_config": RunConfig(max_workers=self.run_params.system_workers, 
                                    timeout=self.run_params.system_timeout)
        }
        
        # column_map solo si se proporciona (resumen)
        if column_map:
            kwargs["column_map"] = column_map
            
        result = evaluate(**kwargs)
        df = result.to_pandas()
        df['eval_type'] = eval_type_name
        
        df['evaluation_name'] = config_name if config_name else eval_type_name
        return df

    def generate_answers(self, vector_manager, global_context_json, pregenerated_summary=None, reduced_context=None, target='both'):
        '''Usa el LLM para responder a las preguntas basándose solo en la patrulla'''
        with open(self.quest_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        # Si se puso un diccionario directamente, se envuelve en una lista
        if isinstance(questions_data, dict):
            questions_data = [questions_data]

        short_eval_data = {"question": [], "answer": [], "ground_truth": [], "contexts": []}
        summary_eval_data = {"question": [], "answer": [], "ground_truth": [], "contexts": [], "reference_contexts": []}

        eval_context = EvalContext(
            global_json=global_context_json,
            pregenerated_summary=pregenerated_summary,
            reduced_context=reduced_context # Pasa el parámetro que recibe la función
        )

        rag_chain = vector_manager.get_conversational_chain()

        for item in questions_data:
            if not isinstance(item, dict):
                if self.logger:
                    self.logger.warning(f"Elemento ignorado en quest.json (no es un objeto JSON válido): {item}")
                continue
            question_type = item.get("type", "short") # asume short para retrocompatibilidad con archivos legacy
            
            if question_type == "summary" and target in ['both', 'summary_only']:
                self.process_summary_question(item, eval_context, summary_eval_data)
            elif question_type == "short" and target in ['both', 'short_only']:
                self.process_short_question(item, short_eval_data, rag_chain)
                
        return short_eval_data, summary_eval_data
    
    def process_summary_question(self, item, eval_context, summary_eval_data):
        '''Responde y empaqueta preguntas de resumen'''
        question = item["question"]
        ground_truth = item["ground_truth"]
        
        llm_answer, default_question_for_ragas = self.generate_summary_answer(
            eval_context.global_json, eval_context.pregenerated_summary
        )

        # si hay pregunta en el JSON se usa esa
        if not question or str(question).strip() == "":
            question_for_ragas = default_question_for_ragas
        else:
            question_for_ragas = str(question)

        self.add_record_to_dataset(summary_eval_data, {
            "question": question_for_ragas,
            "answer": llm_answer.strip(),
            "ground_truth": ground_truth,
            "contexts": [eval_context.global_json], 
            "reference_contexts": [eval_context.global_json] 
        })
        
        if self.logger:
            self.logger.debug(f"Resumen generado: {llm_answer.strip()}")
            self.logger.debug("Contextos separados empaquetados para RAGAS.")

    def process_short_question(self, item, short_eval_data, rag_chain):
        '''Responde y empaqueta preguntas cortas usando RAG de LangChain'''
        question = item["question"]
        ground_truth = item["ground_truth"]
        
        # LangChain gestiona la búsqueda en FAISS y el historial
        result = rag_chain.invoke({"question": question})
        answer = result.get("answer", "No hay información").strip()
        
        # Contextos exactos que FAISS entregó al modelo para el prompt
        source_documents = result.get("source_documents", [])
        contexts = [doc.page_content for doc in source_documents]

        if not contexts:
            contexts = ["No se recuperó contexto de la base de datos vectorial"]

        self.add_record_to_dataset(short_eval_data, {
            "question": str(question),
            "answer": answer,
            "ground_truth": ground_truth,
            "contexts": contexts
        })
    
    def generate_summary_answer(self, global_context_json, pregenerated_summary):
        '''Genera o recupera el resumen global y la pregunta formateada para RAGAS'''
        if pregenerated_summary:
            llm_answer = pregenerated_summary
        else: # Fallback
            prompt = f"Genera un reporte de actividades humanas detectadas con estos datos: {global_context_json}"
            llm_answer = call_ollama_api(
                f"{self.ollama_params.ollama_url}/api/generate",
                {"model": "llama3", "prompt": prompt, "stream": False}
            )
        
        question_for_ragas = "Redacta el informe de seguridad global de la patrulla del hospital."
        return llm_answer, question_for_ragas
    
    def generate_short_answer(self, context_str, question):
        '''Genera la respuesta a una pregunta corta usando Ollama'''
        prompt = f"""
        Eres un sistema analizador de actividades humanas en un hospital. 
        Basándote ÚNICAMENTE en este registro visual de tu patrulla:
        {context_str}
        
        Responde de forma breve y concisa a la siguiente pregunta.
        
        Pregunta: {question}
        """
        question_for_ragas = str(question)

        llm_answer = call_ollama_api(
            f"{self.ollama_params.ollama_url}/api/generate",
            {"model": "llama3", "prompt": prompt, "stream": False}
        )
        return llm_answer, question_for_ragas

    def add_record_to_dataset(self, dataset, record):
        '''Añade una nueva fila de datos al diccionario de RAGAS'''
        for key, value in record.items():
            # setdefault crea la lista vacía si la clave no existe, y luego hace el append
            dataset.setdefault(key, []).append(value)
    
    def evaluate_perception(self, eval_dict, config_name="", model_name="perception_model"):
        '''Genera respuestas imagen por imagen y ejecuta Ragas para el perceptor a partir de un diccionario'''
        config_name = model_name if config_name == "" or config_name == "generic_evaluation" else config_name

        if eval_dict["question"]: # nombre de la evaluación
            eval_dict["evaluation_name"] = [config_name] * len(eval_dict["question"])
        
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
        output_path = os.path.join(self.metrics_dir, f"ragas_{config_name}_perception_evaluation.csv")
        df_results = result.to_pandas()
        df_results['evaluation_name'] = config_name # hay que insertarlo después de que pandas lo devuelva en df y RAGAS no lo elimine
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