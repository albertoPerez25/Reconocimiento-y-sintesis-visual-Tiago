#!/usr/bin/env python3
import os
import glob
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Tema para los gráficos
sns.set_theme(style="whitegrid", palette="pastel")

# Rutas por defecto
JSON_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/P1/comparativa_modelos.json"
RAGAS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/P1/"
OUTPUT_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/P1/res"

FINAL_SCORE_WITH_FAITHFULNESS = False

GLOBAL_EVAL_WEIGHTS = {
    'short_eval': 0.50,
    'summary_eval': 0.50
}

def load_performance_data(json_path):
    """Carga el JSON de rendimientos y calcula métricas a partir de él"""
    if not os.path.exists(json_path):
        print(f"Error: Archivo JSON no encontrado en {json_path}")
        return None
    
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    
    if 'total_imagenes_procesadas' in df.columns and 'tiempo_percepcion_segundos' in df.columns:
        df['segundos_por_imagen'] = df.apply(
            lambda row: row['tiempo_percepcion_segundos'] / row['total_imagenes_procesadas'] 
            if row['total_imagenes_procesadas'] > 0 else 0, axis=1
        )
    return df

def load_ragas_data(ragas_dir):
    csv_files = glob.glob(os.path.join(ragas_dir, 'ragas_*.csv'))
    data_with_scores = []
    
    for file in csv_files:
        df = pd.read_csv(file)
        base_name = os.path.basename(file)
        
        if base_name.endswith('_perception_evaluation.csv'):
            eval_category = 'perception'
        elif 'system' in base_name.lower():
            eval_category = 'system'
        else:
            continue 
            
        display_name = base_name.replace('.csv', '') # Fallback por defecto
        display_name = display_name.replace('ragas_', '')
        
        if 'evaluation_name' in df.columns and not df['evaluation_name'].isnull().all():
            val = str(df['evaluation_name'].iloc[0]).strip()
            if val and val.lower() != 'nan':
                display_name = val

        # Configuracion es lo que usa matplotlib
        df['Configuracion'] = display_name
        df['Eval_Category'] = eval_category 

        metric_cols = [col for col in ['answer_correctness', 'answer_relevancy', 'faithfulness', 'summary_score'] if col in df.columns]
        
        # nota media general del archivo
        sort_score = df[metric_cols].mean().mean() if metric_cols else 0.0
        
        # (nota, dataframe)
        data_with_scores.append((sort_score, df))
        
    # Mayor a Menor nota 
    data_with_scores.sort(key=lambda x: x[0], reverse=True)
        
    all_data = [item[1] for item in data_with_scores]
        
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def load_aggregated_perception_data(directory):
    """Carga los datos agregados de los perceptores desde los archivos JSON"""
    json_files = glob.glob(os.path.join(directory, 'aggregated_*_metrics.json'))
    data_list = []
    
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            is_hybrid = data.get("modelo_usado") == "Modelo Híbrido Acoplado"
            stats_key = "estadisticas_totales" if is_hybrid else "estadisticas_globales"
            
            if stats_key in data:
                stats = data[stats_key]
                etiqueta = data.get("nodo_ejecutor", "Híbrido") if is_hybrid else data.get("modelo_usado", "Desconocido")
                
                row = {
                    "etiqueta": etiqueta,
                    "media_segundos": stats.get("media_segundos", 0.0),
                    "percentil_99": stats.get("percentil_99", 0.0),
                    "fps_equivalente": stats.get("fps_equivalente", 0.0),
                    "desviacion_tipica": stats.get("desviacion_tipica", 0.0),
                    "is_hybrid": is_hybrid
                }
                
                if is_hybrid:
                    stats_yolo = data.get("estadisticas_yolo", {})
                    stats_vlm = data.get("estadisticas_vlm", {})
                    row["yolo_media"] = stats_yolo.get("media_segundos", 0.0)
                    row["vlm_media"] = stats_vlm.get("media_segundos", 0.0)
                    cuello = stats.get("cuello_de_botella_vlm_porcentaje", "0%")
                    row["vlm_porcentaje"] = float(str(cuello).replace('%', ''))
                    
                data_list.append(row)
        except Exception as e:
            print(f"Error cargando {file}: {e}")
            
    return pd.DataFrame(data_list)

def calculate_system_metrics(df, config_name):
    """Extrae la lógica de cálculo de métricas para el evaluador del sistema"""
    df_short = df[df['eval_type'] == 'short']
    df_summ = df[df['eval_type'] == 'summary']

    # Preguntas Cortas End-to-End (Nota Final)
    short_correctness_score = df_short['answer_correctness'].mean() if not df_short.empty and 'answer_correctness' in df_short.columns else 0.0
    short_relevancy_score = df_short['answer_relevancy'].mean() if not df_short.empty and 'answer_relevancy' in df_short.columns else 0.0
    
    short_metrics_for_final = [short_correctness_score, short_relevancy_score]
    final_short = sum(short_metrics_for_final) / float(len(short_metrics_for_final)) if not df_short.empty else 0.0

    # Diagnóstico Generador
    short_faithfulness_score = df_short['faithfulness'].mean() if not df_short.empty and 'faithfulness' in df_short.columns else 0.0

    # Diagnóstico Recuperador (Retriever)
    ctx_precision = get_safe_mean(df_short, 'context_precision')
    ctx_recall = get_safe_mean(df_short, 'context_recall')
    ctx_entity = get_safe_mean(df_short, 'context_entity_recall')
    final_retriever = (ctx_precision + ctx_recall + ctx_entity) / 3.0 if not df_short.empty else 0.0
    

    # Resumen
    summary_correctness_score = df_summ['answer_correctness'].mean() if not df_summ.empty and 'answer_correctness' in df_summ.columns else 0.0
    summary_summarization_score = df_summ['summary_score'].mean() if not df_summ.empty and 'summary_score' in df_summ.columns else 0.0

    summary_metrics_for_final = [summary_correctness_score, summary_summarization_score]
    final_summ = sum(summary_metrics_for_final) / float(len(summary_metrics_for_final)) if not df_summ.empty else 0.0

    # Diagnóstico Generador
    summary_faithfulness_score = df_summ['faithfulness'].mean() if not df_summ.empty and 'faithfulness' in df_summ.columns else 0.0

    # Global de métricas puras
    global_corr = df['answer_correctness'].mean(skipna=True) if 'answer_correctness' in df.columns else 0.0
    global_rel = df['answer_relevancy'].mean(skipna=True) if 'answer_relevancy' in df.columns else 0.0
    global_faith = df['faithfulness'].mean(skipna=True) if 'faithfulness' in df.columns else 0.0
    global_summ = df['summary_score'].mean(skipna=True) if 'summary_score' in df.columns else 0.0
    
    final_global = (final_short * GLOBAL_EVAL_WEIGHTS['short_eval']) + (final_summ * GLOBAL_EVAL_WEIGHTS['summary_eval'])

    return {
        'Configuracion': config_name,
        # Cortas
        'Sh_Corr': round(short_correctness_score, 3), 'Sh_Rel': round(short_relevancy_score, 3), 'Sh_Faith': round(short_faithfulness_score, 3), 'Final_Short': round(final_short, 3),
        # Retriever
        'Sh_Ctx_Prec': round(ctx_precision, 3), 'Sh_Ctx_Rec': round(ctx_recall, 3), 'Sh_Ctx_Ent': round(ctx_entity, 3), 'Final_Retriever': round(final_retriever, 3),
        # Resumen
        'Su_Faith': round(summary_faithfulness_score, 3), 'Su_Summ': round(summary_summarization_score, 3), 'Su_Corr': round(summary_correctness_score, 3), 'Final_Summ': round(final_summ, 3),
        # Globales
        'G_Corr': round(global_corr, 3), 'G_Rel': round(global_rel, 3), 'G_Faith': round(global_faith, 3), 'G_Summ': round(global_summ, 3),
        'Final_Global': round(final_global, 3)
    }

def get_safe_mean(df, col_name):
    """Extraer medias de forma segura frente a NaNs"""
    if col_name in df.columns:
        val = df[col_name].mean()
        return 0.0 if pd.isna(val) else val
    return 0.0

def calculate_legacy_metrics(df, config_name):
    """Extrae la lógica de cálculo de métricas para perceptores aislados o CSVs antiguos"""

    mean_correctness = get_safe_mean(df,'answer_correctness')
    mean_relevancy = get_safe_mean(df,'answer_relevancy')
    mean_summ = get_safe_mean(df,'summary_score')
    mean_faithfulness = get_safe_mean(df,'faithfulness')

    if FINAL_SCORE_WITH_FAITHFULNESS:
        final_score = (mean_correctness + mean_relevancy + mean_summ + mean_faithfulness) / 3.0
    else: # archivos csv legacy
        final_score = (mean_correctness + mean_relevancy + mean_summ) / 2.0 
    
    return {
        'Configuracion': config_name,
        'Correctness': round(mean_correctness, 3),
        'Relevancy': round(mean_relevancy, 3),
        'Summarization': round(mean_summ, 3),
        'Faithfulness': round(mean_faithfulness, 3),
        'Final_Score': round(final_score, 3)
    }

def get_dynamic_rotation(labels):
    """Devuelve la rotacion de etiqueta óptima según el número y logitud de estas"""
    num_labels = len(labels)
    max_len = max([len(str(label)) for label in labels]) if num_labels > 0 else 0
    
    # Si hay pocos modelos y sus nombres son cortos horizontales
    if num_labels <= 3 and max_len <= 18:
        return 0, 'center'
    # Si son muchos o muy largos rotacion de 45 grados
    else:
        return 45, 'right'

def generate_performance_summary(df, output_dir):
    """Imprime y guarda los resultados"""
    print("\n" + "="*60)
    print("   RESUMEN DE MÉTRICAS DE RENDIMIENTO (Valores Medios)")
    print("="*60)
    
    summary = df.groupby('evaluacion_nombre').mean(numeric_only=True).round(2)
    
    columns_to_show = {
        'tiempo_total_segundos': 'Tiempo Total (s)',
        'segundos_por_imagen': 'Latencia Visión (s/img)',
        'caracteres_contexto_visual': 'Contexto Generado (Caract.)',
        'tiempo_llm_segundos': 'Tiempo Redacción LLM (s)'
    }
    
    display_table = summary[list(columns_to_show.keys())].rename(columns=columns_to_show)
    print(display_table.to_string())
    print("="*60 + "\n")
    
    display_table.to_csv(os.path.join(output_dir, "tabla_resumen_rendimiento.csv"))

def generate_ragas_summary(df, output_dir):
    """Guarda la evaluacion de RAFAS"""
    print("\n" + "="*60)
    print("  RESUMEN DE EVALUACIÓN RAGAS (Calidad de Respuesta)")
    print("="*60)
    print(df.to_string(index=False))
    print("="*60 + "\n")
    
    df.to_csv(os.path.join(output_dir, "tabla_resumen_ragas.csv"), index=False)

def generate_performance_plots(df, output_dir):
    """Genera las gráficas de rendimientos """
    unique_models = df['evaluacion_nombre'].unique() # para ordenarlos
    ordered_labels = sorted(unique_models, key=lambda x: (x.replace('_JSON', ''), x))

    rot, align = get_dynamic_rotation(ordered_labels)
    
    # Tiempos de procesamiento
    plt.figure(figsize=(10, 6))
    summary_times = df.groupby('evaluacion_nombre')[['tiempo_percepcion_segundos', 'tiempo_llm_segundos']].mean()
    summary_times = summary_times.reindex(ordered_labels)

    summary_times.plot(kind='bar', stacked=True, color=['#4C72B0', '#55A868'], figsize=(10, 6))
    plt.title("Tiempo Medio de Procesamiento por Patrulla", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos", fontsize=12)
    plt.legend(["Percepción (Visión)", "Razonamiento (LLM)"])
    plt.xticks(rotation=rot, ha=align)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_desglose_tiempos.png"), dpi=300)
    plt.close()

    # Latencia
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='evaluacion_nombre', y='segundos_por_imagen', order=ordered_labels, errorbar='sd', capsize=.1)
    plt.title("Latencia del Modelo Visual", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos por Imagen procesada", fontsize=12)
    plt.xticks(rotation=rot, ha=align)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_latencia_visual.png"), dpi=300)
    plt.close()

    # Análisis de verbosidad
    plt.figure(figsize=(10, 6))
    summary_chars = df.groupby('evaluacion_nombre')[['caracteres_contexto_visual', 'caracteres_informe_final']].mean()
    summary_chars = summary_chars.reindex(ordered_labels)
    summary_chars.plot(kind='bar', width=0.7, color=['#C44E52', '#8172B3'], figsize=(10, 6))
    plt.title("Análisis de Verbosidad (Texto procesado)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Cantidad de Caracteres", fontsize=12)
    plt.legend(["Contexto Visual Generado", "Informe Final (Llama-3)"])
    plt.xticks(rotation=rot, ha=align)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_analisis_verbosidad.png"), dpi=300)
    plt.close()

    # Estabilidad (boxplot)
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='evaluacion_nombre', y='tiempo_total_segundos', order=ordered_labels, palette="Set2")
    sns.stripplot(data=df, x='evaluacion_nombre', y='tiempo_total_segundos', color=".3", size=6, alpha=0.6)
    plt.title("Estabilidad del Tiempo de Ejecución (Boxplot)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Tiempo Total (Segundos)", fontsize=12)
    plt.xticks(rotation=rot, ha=align)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_estabilidad_tiempos.png"), dpi=300)
    plt.close()

def generate_ragas_system_plots(df, output_dir): # TODO
    """Genera 4 gráficas distintas para la evaluación del sistema"""
    labels = df['Configuracion'].tolist()
    rot, align = get_dynamic_rotation(labels)
    x = np.arange(len(labels))

    # 5a Preguntas Cortas (Chatbot)
    fig, ax = plt.subplots(figsize=(11, 6))
    w = 0.2
    rects1 = ax.bar(x - 1.5*w, df['Sh_Corr'], w, label='Correctness', color='#4C72B0')
    rects2 = ax.bar(x - 0.5*w, df['Sh_Rel'], w, label='Relevancy', color='#55A868')
    rects3 = ax.bar(x + 0.5*w, df['Sh_Faith'], w, label='Faithfulness', color='#E1A95F')
    rects4 = ax.bar(x + 1.5*w, df['Final_Short'], w, label='Final Cortas', color='#C44E52')
    
    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Ragas Sistema: Preguntas Cortas')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot, ha=align); ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', ncol=2)
    for r in [rects1, rects2, rects3, rects4]: ax.bar_label(r, padding=3, fmt='%.2f', fontsize=8)
    fig.tight_layout(); plt.savefig(os.path.join(output_dir, '5a_ragas_sistema_cortas.png'), dpi=300); plt.close()

    # 5b Resumen (Reportero) 
    fig, ax = plt.subplots(figsize=(10, 6))
    w = 0.2
    rects1 = ax.bar(x - 1.5*w, df['Su_Faith'], w, label='Faithfulness', color='#E1A95F')
    rects2 = ax.bar(x - 0.5*w, df['Su_Summ'], w, label='Summarization', color='#D25FE1')
    rects3 = ax.bar(x + 0.5*w, df['Su_Corr'], w, label='Correctness', color='#4C72B0')
    rects4 = ax.bar(x + 1.5*w, df['Final_Summ'], w, label='Final Resumen', color='#C44E52')
    
    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Ragas Sistema: Calidad del Resumen')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot, ha=align); ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', ncol=4)
    for r in [rects1, rects2, rects3, rects4]: ax.bar_label(r, padding=3, fmt='%.2f', fontsize=8)
    fig.tight_layout(); plt.savefig(os.path.join(output_dir, '5b_ragas_sistema_resumen.png'), dpi=300); plt.close()

    # 5c Puntuaciones Finales (Cortas vs Resumen vs Ponderado Global)
    fig, ax = plt.subplots(figsize=(9, 6))
    w = 0.25
    rects1 = ax.bar(x - w, df['Final_Short'], w, label='Final Cortas', color='#8172B3')
    rects2 = ax.bar(x, df['Final_Summ'], w, label='Final Resumen', color='#64B5CD')
    
    # Relación de pesos en la leyenda
    peso_corta = int(GLOBAL_EVAL_WEIGHTS['short_eval'] * 100)
    peso_resum = int(GLOBAL_EVAL_WEIGHTS['summary_eval'] * 100)
    rects3 = ax.bar(x + w, df['Final_Global'], w, label=f'Global ({peso_corta}/{peso_resum})', color='#C44E52')
    
    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Ragas Sistema: Comparativa de Puntuaciones Finales')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot, ha=align); ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', ncol=3)
    for r in [rects1, rects2, rects3]: ax.bar_label(r, padding=3, fmt='%.2f', fontsize=8)
    fig.tight_layout(); plt.savefig(os.path.join(output_dir, '5c_ragas_sistema_totales.png'), dpi=300); plt.close()

    # 5d Todo Combinado 
    fig, ax = plt.subplots(figsize=(12, 6))
    w = 0.15
    rects1 = ax.bar(x - 2*w, df['G_Corr'], w, label='Corr. Global', color='#4C72B0')
    rects2 = ax.bar(x - w, df['G_Rel'], w, label='Rel. Global', color='#55A868')
    rects3 = ax.bar(x, df['G_Faith'], w, label='Faith. Global', color='#E1A95F')
    rects4 = ax.bar(x + w, df['G_Summ'], w, label='Summ. Global', color='#D25FE1')
    rects5 = ax.bar(x + 2*w, df['Final_Global'], w, label='Final Global', color='#C44E52')
    rects6 = ax.bar(x + 2*w, df['Sh_Ctx_Rec'], w, label='Ctx Recall (Diag)', color='#64B5CD')
    rects7 = ax.bar(x + 3*w, df['Final_Global'], w, label='Final Global', color='#C44E52')
    
    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Ragas Sistema: Todas las Métricas Globales')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot, ha=align); ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', ncol=5)
    for r in [rects1, rects2, rects3, rects4, rects5, rects6, rects7]: ax.bar_label(r, padding=3, fmt='%.2f', fontsize=7)
    fig.tight_layout(); plt.savefig(os.path.join(output_dir, '5d_ragas_sistema_completo.png'), dpi=300); plt.close()

    # 5e Métricas de Contexto (Evaluación exclusiva del Retriever / FAISS)
    fig, ax = plt.subplots(figsize=(11, 6))
    w = 0.2
    rects1 = ax.bar(x - 1.5*w, df['Sh_Ctx_Prec'], w, label='Context Precision', color='#8172B3')
    rects2 = ax.bar(x - 0.5*w, df['Sh_Ctx_Rec'], w, label='Context Recall', color='#64B5CD')
    rects3 = ax.bar(x + 0.5*w, df['Sh_Ctx_Ent'], w, label='Entity Recall', color='#E1A95F')
    rects4 = ax.bar(x + 1.5*w, df['Final_Retriever'], w, label='Media Retriever', color='#C44E52')
    
    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Ragas Sistema: Calidad del Contexto Recuperado (Retriever)')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot, ha=align); ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', ncol=4)
    for r in [rects1, rects2, rects3, rects4]: ax.bar_label(r, padding=3, fmt='%.2f', fontsize=8)
    fig.tight_layout(); plt.savefig(os.path.join(output_dir, '5e_ragas_sistema_retriever.png'), dpi=300); plt.close()

def generate_ragas_perception_plot(df, output_dir):
    """Genera la gráfica clásica de 3 barras para los perceptores aislados"""
    labels = df['Configuracion'].tolist()
    correctness = df['Correctness'].tolist()
    relevancy = df['Relevancy'].tolist()
    final_score = df['Final_Score'].tolist()
    
    rot, align = get_dynamic_rotation(labels)

    x_positions = np.arange(len(labels))
    bar_width = 0.25 

    fig, ax = plt.subplots(figsize=(11, 6))
    
    rects1 = ax.bar(x_positions - bar_width, correctness, bar_width, label='Correctness (Visión)', color='#4C72B0')
    rects2 = ax.bar(x_positions, relevancy, bar_width, label='Relevancy', color='#55A868')
    rects3 = ax.bar(x_positions + bar_width, final_score, bar_width, label='Final Score', color='#C44E52')

    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Evaluación Ragas: Modelos de Percepción Aislados')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, rotation=rot, ha=align)
    ax.set_ylim(0, 1.15) 
    ax.legend(loc='upper right', ncol=3) 

    ax.bar_label(rects1, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects2, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects3, padding=3, fmt='%.2f', fontsize=8)

    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, '6_grafica_ragas_percepcion.png'), dpi=300)
    plt.close()

def generate_aggregated_perception_plots(df, output_dir):
    """Genera gráficas para las métricas agregadas de los perceptores"""
    if df.empty:
        return

    labels = df['etiqueta'].tolist()
    rot, align = get_dynamic_rotation(labels)
    x = np.arange(len(labels))
    
    # Gráfica A (7_percepcion_latencia_extrema.png): Media vs P99
    fig, ax = plt.subplots(figsize=(10, 6))
    w = 0.35
    rects1 = ax.bar(x - w/2, df['media_segundos'], w, label='Media (s)', color='#4C72B0')
    rects2 = ax.bar(x + w/2, df['percentil_99'], w, label='P99 (s)', color='#C44E52')
    
    ax.set_ylabel('Segundos')
    ax.set_title('Latencia de Percepción: Media vs Caso Extremo (P99)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=rot, ha=align)
    ax.legend(loc='upper right')
    for r in [rects1, rects2]: ax.bar_label(r, padding=3, fmt='%.2f', fontsize=8)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, '7_percepcion_latencia_extrema.png'), dpi=300)
    plt.close()

    # Gráfica B (8_percepcion_fps.png): FPS Equivalente
    df_fps = df.sort_values(by='fps_equivalente', ascending=False)
    labels_fps = df_fps['etiqueta'].tolist()
    x_fps = np.arange(len(labels_fps))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects = ax.bar(x_fps, df_fps['fps_equivalente'], 0.5, color='#55A868')
    ax.set_ylabel('Frames Por Segundo (FPS)')
    ax.set_title('Rendimiento en FPS Equivalente')
    ax.set_xticks(x_fps)
    ax.set_xticklabels(labels_fps, rotation=get_dynamic_rotation(labels_fps)[0], ha=get_dynamic_rotation(labels_fps)[1])
    ax.bar_label(rects, padding=3, fmt='%.2f', fontsize=9)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, '8_percepcion_fps.png'), dpi=300)
    plt.close()

    # Gráfica C (9_hibrido_cuello_botella.png): Desglose Híbrido
    df_hybrid = df[df['is_hybrid'] == True]
    if not df_hybrid.empty:
        h_labels = df_hybrid['etiqueta'].tolist()
        hx = np.arange(len(h_labels))
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(hx, df_hybrid['yolo_media'], 0.5, label='YOLO (Espacial)', color='#4C72B0')
        ax.bar(hx, df_hybrid['vlm_media'], 0.5, bottom=df_hybrid['yolo_media'], label='VLM (Semántico)', color='#E1A95F')
        
        ax.set_ylabel('Segundos (Media)')
        ax.set_title('Desglose de Cuello de Botella (Nodo Híbrido)')
        ax.set_xticks(hx)
        ax.set_xticklabels(h_labels, rotation=get_dynamic_rotation(h_labels)[0], ha=get_dynamic_rotation(h_labels)[1])
        ax.legend(loc='upper right')
        
        # Anotar porcentaje
        for i, row in enumerate(df_hybrid.itertuples()):
            ax.text(i, row.yolo_media + row.vlm_media/2, f"{row.vlm_porcentaje:.1f}%", ha='center', va='center', color='black', fontsize=9, fontweight='bold')

        fig.tight_layout()
        plt.savefig(os.path.join(output_dir, '9_hibrido_cuello_botella.png'), dpi=300)
        plt.close()

def aggregate_metrics(df, calc_function):
    """
    Agrupa un DataFrame de RAGAS por 'Configuracion' y aplica 
    la función de cálculo de métricas especificada.
    """
    metrics_list = []
    for config_name, group_df in df.groupby('Configuracion'):
        metrics_list.append(calc_function(group_df, config_name))
        
    return pd.DataFrame(metrics_list)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Datos sobre el rendimiento
    df_performance = load_performance_data(JSON_PATH)
    if df_performance is not None and not df_performance.empty:
        generate_performance_summary(df_performance, OUTPUT_DIR)
        generate_performance_plots(df_performance, OUTPUT_DIR)
        print("- Gráficos de rendimiento generados (1 al 4).")
    
    # Datos de RAGAS
    df_ragas = load_ragas_data(RAGAS_DIR)
    if df_ragas is not None and not df_ragas.empty:
        generate_ragas_summary(df_ragas, OUTPUT_DIR)

        # Si el nombre del CSV incluye "system", va a la gráfica A. Si no a la B.
        df_system = df_ragas[df_ragas['Eval_Category'] == 'system'].copy()
        df_perception = df_ragas[df_ragas['Eval_Category'] == 'perception'].copy()
        
        # Procesar y dibujar métricas de sistema
        if not df_system.empty:
            df_system_agg = aggregate_metrics(df_system, calculate_system_metrics)
            generate_ragas_system_plots(df_system_agg, OUTPUT_DIR)
        
        # Procesar y dibujar métricas de percepción
        if not df_perception.empty:
            df_perception_agg = aggregate_metrics(df_perception, calculate_legacy_metrics)
            generate_ragas_perception_plot(df_perception_agg, OUTPUT_DIR)

        print("- Gráficos de evaluación Ragas generados (5 y 6).")

    # Datos de Percepción Agregada
    df_aggregated = load_aggregated_perception_data(OUTPUT_DIR)
    if df_aggregated is not None and not df_aggregated.empty:
        generate_aggregated_perception_plots(df_aggregated, OUTPUT_DIR)
        print("- Gráficos de perceptores agregados generados (7 al 9).")

if __name__ == "__main__":
    main()