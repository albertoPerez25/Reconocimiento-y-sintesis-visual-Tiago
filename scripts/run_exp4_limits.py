#!/usr/bin/env python3

'''
Para que funcione es necesario ejecutarlo desde la carpeta raíz del paquete patrulla_hospital, o modificar los import.

'''

import os
import json
import time
import pandas as pd
import ast

# Importaciones directas de la lógica de tu proyecto (Sin ROS 2)
from ruta_hospital.utils.shared.vector_manager import VectorManager
from ruta_hospital.evaluation.utils.ragas_evaluator import RagasEvaluator, OllamaParams, EvaluatorRunParams
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.summarize.chain import load_summarize_chain
from langchain_ollama import ChatOllama

# ================= CONFIGURACIÓN =================
# Usamos el FAISS generado en el experimento 1 (Dataset Grande) como base constante
FAISS_SOURCE_DIR = "/home/alberto/tfg/Datos_tmp/eval/1_hybrid_vs_vlm/1_eval_hybrid/ruta_hospital_rag_data"
QUESTIONS_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/src/ruta_hospital/config/quest.json"
OUTPUT_METRICS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/exp4_limites_palabras"

# Parámetros del LLM
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "llama3"#"qwen3.5:4b"  # El modelo que genera el resumen
RAGAS_LLM_MODEL = "llama3.1" # El modelo que actúa como juez en RAGAS

WORD_LIMITS = [100,200,300,400] #,500,600,700,800
# =================================================

def build_hospital_data_dict(vector_manager):
    """
    Extrae todos los eventos del FAISS con soporte a múltiples formatos de parseo.
    """
    if getattr(vector_manager, 'vector_store', None) is None:
        print("❌ ERROR: El VectorStore no se ha inicializado.")
        return {}
        
    docs = list(vector_manager.vector_store.docstore._dict.values())
    hospital_data_dict = {}
    total_events = 0
    
    for doc in docs:
        # Extraer zona buscando posibles variantes de la clave
        zone = doc.metadata.get("zone_name") or doc.metadata.get("zona") or "Desconocida"
        
        event_data = None
        
        # 1. Intentar parsear como JSON estricto
        try:
            event_data = json.loads(doc.page_content)
        except Exception:
            # 2. Intentar parsear como diccionario literal de Python
            try:
                event_data = ast.literal_eval(doc.page_content)
            except Exception:
                # 3. Si es texto crudo, lo encapsulamos en la estructura esperada
                event_data = {"actividad": doc.page_content, "alerta": False, "hora": "N/A"}
        
        if event_data is not None:
            if zone not in hospital_data_dict:
                hospital_data_dict[zone] = {"eventos_recientes": []}
                
            if event_data not in hospital_data_dict[zone]["eventos_recientes"]:
                hospital_data_dict[zone]["eventos_recientes"].append(event_data)
                total_events += 1
            
    print(f"✅ Memoria rehidratada: {total_events} eventos agrupados en {len(hospital_data_dict)} zonas.")
    return hospital_data_dict

def extract_alerts_document(hospital_data_dict):
    """Réplica de self._extract_alerts_document de VectorManager"""
    todas_alertas = []
    for zone, info in hospital_data_dict.items():
        eventos = info.get("eventos_recientes", [])
        for ev in eventos:
            if isinstance(ev, dict) and ev.get("alerta") == True:
                alerta_simplificada = {
                    "tipo": ev.get("actividad", "Desconocida"),
                    "zona": zone,
                    "hora": ev.get("hora", "Desconocida"),
                    "gravedad": ev.get("gravedad", "Desconocida")
                }
                todas_alertas.append(alerta_simplificada)
    if todas_alertas:
        content = "RESUMEN DE ALARMAS CRÍTICAS:\n" + json.dumps(todas_alertas, ensure_ascii=False)
        return Document(page_content=content, metadata={"zona": "ALARMAS_CRITICAS"})
    return None

def generate_summary_langchain(hospital_data_dict, llm, max_words):
    """Genera el resumen utilizando la cadena map_reduce"""
    if not hospital_data_dict:
        return "Todas las zonas patrulladas se encuentran despejadas"

    docs = []
    for zone, info in hospital_data_dict.items():
        if info.get("eventos_recientes"):
            content = f"ZONA: {zone}\n{json.dumps(info, ensure_ascii=False)}"
        else:
            content = f"ZONA: {zone}\nSin eventos detectados, despejada."
        docs.append(Document(page_content=content, metadata={"zona": zone}))

    alerts_doc = extract_alerts_document(hospital_data_dict)
    if alerts_doc:
        docs.append(alerts_doc)

    map_prompt = PromptTemplate(
        template="Resume brevemente las actividades de este reporte de zona. Mantén detalles de personas, horas y alertas.\nReporte:\n{text}\nRESUMEN EN ESPAÑOL:",
        input_variables=["text"]
    )

    combine_prompt_template = "Eres la IA de reconocimiento de actividades y humanos del hospital. Escribe un resumen global profesional combinando los siguientes reportes. "
    if max_words:
        combine_prompt_template += f"Hazlo en una extensión máxima de {max_words} palabras. "
    combine_prompt_template += "\nReportes:\n{text}\nRESUMEN GLOBAL EN ESPAÑOL:"

    combine_prompt = PromptTemplate(
        template=combine_prompt_template,
        input_variables=["text"]
    )

    chain = load_summarize_chain(
        llm, 
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt
    )
    
    summary = chain.invoke(docs)
    return summary["output_text"].strip()


def main():
    os.makedirs(OUTPUT_METRICS_DIR, exist_ok=True)
    
    print(f"🔍 1. Cargando base de datos vectorial desde: {FAISS_SOURCE_DIR}")
    vector_manager = VectorManager(base_dir=FAISS_SOURCE_DIR, ollama_url=OLLAMA_URL)
    vector_manager.get_highest_round_in_disk()
    
    # 2. Reconstruimos el diccionario tal y como lo ve el reportero
    hospital_data_dict = build_hospital_data_dict(vector_manager)
    
    # Preparamos el JSON stringificado puro para RAGAS (evaluación de contexto)
    eventos_crudos = []
    for zone, info in hospital_data_dict.items():
        eventos_crudos.extend(info.get("eventos_recientes", []))
    contexto_global_json = json.dumps(eventos_crudos, ensure_ascii=False)

    print("⚙️ 3. Inicializando Motor de Evaluación RAGAS...")
    ragas_params = OllamaParams(
        ollama_url=OLLAMA_URL,
        evaluator_llm_model=RAGAS_LLM_MODEL,
        evaluator_embed_model="nomic-embed-text"
    )
    
    # Instanciamos los RunParams puros para configurar los hilos de RAGAS
    run_params = EvaluatorRunParams(
        system_workers=1, 
        system_timeout=420
    )

    # Instanciamos el evaluador pasándole explícitamente todos los parámetros requeridos
    evaluator = RagasEvaluator(
        ollama_params=ragas_params, 
        run_params=run_params,
        metrics_dir=OUTPUT_METRICS_DIR,  
        quest_path=QUESTIONS_PATH
    )

    # Instanciamos el LLM generador (Qwen) para LangChain
    generador_llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_URL, temperature=0.1)

    resultados = []

    # ================= BUCLE DEL EXPERIMENTO =================
    for limite in WORD_LIMITS:
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO PRUEBA PARA LÍMITE: {limite} PALABRAS")
        print(f"{'='*60}")

        # A) Generación del Resumen con la cadena Map-Reduce (LangChain)
        print(f"Generando resumen con LangChain ({LLM_MODEL})...")
        t_ini_gen = time.time()
        resumen_texto = generate_summary_langchain(hospital_data_dict, generador_llm, limite)
        t_fin_gen = time.time()
        
        palabras_reales = len(resumen_texto.split())
        tiempo_generacion = round(t_fin_gen - t_ini_gen, 2)
        print(f"✅ Resumen completado en {tiempo_generacion}s. Palabras reales: {palabras_reales}")

        # B) Preparar respuestas de Evaluación RAGAS (Solo para summary)
        print("Invocando a RAGAS para evaluar el resumen frente a las Ground Truths...")
        t_ini_ragas_ans = time.time()
        
        short_dict, summary_dict = evaluator.generate_answers(
            vector_manager=vector_manager,
            global_context_json=contexto_global_json,
            pregenerated_summary=resumen_texto,
            target="summary_only"
        )
        
        # C) Ejecutar el cálculo de las métricas puras de RAGAS
        t_ini_ragas_calc = time.time()
        
        # Llamamos al método correcto: evaluate_system
        df_metricas = evaluator.evaluate_system(
            short_dict={}, 
            summary_dict=summary_dict, 
            config_name=f"limite_{limite}", 
            target="summary_only"
        )
        
        t_fin_ragas_calc = time.time()
        
        tiempo_ragas_total = round(t_fin_ragas_calc - t_ini_ragas_ans, 2)
        print(f"✅ Evaluación RAGAS completada en {tiempo_ragas_total}s.")

        # D) Almacenar resultados de la iteración
        fila_resultado = {
            "limite_solicitado": limite,
            "palabras_reales": palabras_reales,
            "tiempo_generacion_llm": tiempo_generacion,
            "tiempo_evaluacion_ragas": tiempo_ragas_total,
            "resumen_generado": resumen_texto
        }
        
        # Extraemos la media de las métricas que nos ha devuelto RAGAS en el DataFrame
        if df_metricas is not None and not df_metricas.empty:
            # Seleccionamos solo las columnas numéricas (evita hacer medias de strings)
            columnas_numericas = df_metricas.select_dtypes(include='number').columns
            diccionario_medias = df_metricas[columnas_numericas].mean().to_dict()
            fila_resultado.update(diccionario_medias)
            
        resultados.append(fila_resultado)
    # ================= GUARDADO FINAL =================
    df_final = pd.DataFrame(resultados)
    ruta_final = os.path.join(OUTPUT_METRICS_DIR, "experimento_4_limite_palabras_resultados.csv")
    df_final.to_csv(ruta_final, index=False)
    
    print(f"\n🏁 Experimento 4 finalizado con éxito.")
    print(f"📊 Resultados guardados en: {ruta_final}")

if __name__ == "__main__":
    main()
