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
JSON_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/comparativa_modelos.json"
RAGAS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"
OUTPUT_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"

FINAL_SCORE_WITH_FAITHFULNESS = False

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
    """Carga los resultados de RAGAS y calcula varias metricas"""
    csv_files = glob.glob(os.path.join(ragas_dir, '*.csv'))
    
    if not csv_files:
        print(f"Warning: Archivo CSV de Ragas no encontrado en {ragas_dir}")
        return None

    summary_list = []
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        config_name = os.path.splitext(filename)[0]

        try:
            df = pd.read_csv(file_path)

            mean_correctness = df['answer_correctness'].mean() if 'answer_correctness' in df.columns else 0.0
            mean_relevancy = df['answer_relevancy'].mean() if 'answer_relevancy' in df.columns else 0.0
            mean_summ = df['summarization_score'].mean() if 'summarization_score' in df.columns else 0.0
            mean_faithfulness = df['faithfulness'].mean() if 'faithfulness' in df.columns else 0.0

            if FINAL_SCORE_WITH_FAITHFULNESS:
                final_score = (mean_correctness + mean_relevancy + mean_summ + mean_faithfulness) / 3.0
            else:# archivos csv legacy
                final_score = (mean_correctness + mean_relevancy + mean_summ) / 2.0 
            
            summary_list.append({
                'Configuracion': config_name,
                'Correctness': round(mean_correctness, 3),
                'Relevancy': round(mean_relevancy, 3),
                'Summarization': round(mean_summ, 3),
                'Faithfulness': round(mean_faithfulness, 3),
                'Final_Score': round(final_score, 3)
            })
        except Exception as e:
            print(f"Error procesando {filename}: {e}")

    if not summary_list:
        return None

    df_summary = pd.DataFrame(summary_list).sort_values(by='Final_Score', ascending=False)
    return df_summary

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
    
    summary = df.groupby('modelo_reportero').mean(numeric_only=True).round(2)
    
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
    unique_models = df['modelo_reportero'].unique() # para ordenarlos
    ordered_labels = sorted(unique_models, key=lambda x: (x.replace('_JSON', ''), x))

    rot, align = get_dynamic_rotation(ordered_labels)
    
    # Tiempos de procesamiento
    plt.figure(figsize=(10, 6))
    summary_times = df.groupby('modelo_reportero')[['tiempo_percepcion_segundos', 'tiempo_llm_segundos']].mean()
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
    sns.barplot(data=df, x='modelo_reportero', y='segundos_por_imagen', order=ordered_labels, errorbar='sd', capsize=.1)
    plt.title("Latencia del Modelo Visual", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos por Imagen procesada", fontsize=12)
    plt.xticks(rotation=rot, ha=align)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_latencia_visual.png"), dpi=300)
    plt.close()

    # Análisis de verbosidad
    plt.figure(figsize=(10, 6))
    summary_chars = df.groupby('modelo_reportero')[['caracteres_contexto_visual', 'caracteres_informe_final']].mean()
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
    sns.boxplot(data=df, x='modelo_reportero', y='tiempo_total_segundos', order=ordered_labels, palette="Set2")
    sns.stripplot(data=df, x='modelo_reportero', y='tiempo_total_segundos', color=".3", size=6, alpha=0.6)
    plt.title("Estabilidad del Tiempo de Ejecución (Boxplot)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Tiempo Total (Segundos)", fontsize=12)
    plt.xticks(rotation=rot, ha=align)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_estabilidad_tiempos.png"), dpi=300)
    plt.close()

def generate_ragas_system_plot(df, output_dir):
    """Genera la gráfica con Faithfulness solo para el sistema completo"""
    labels = df['Configuracion'].tolist()
    correctness = df['Correctness'].tolist()
    relevancy = df['Relevancy'].tolist()
    summarization = df['Summarization'].tolist()
    faithfulness = df['Faithfulness'].tolist()
    final_score = df['Final_Score'].tolist()
    
    rot, align = get_dynamic_rotation(labels)

    x_positions = np.arange(len(labels))
    bar_width = 0.2 

    fig, ax = plt.subplots(figsize=(11, 6))
    
    rects1 = ax.bar(x_positions - 2.0 * bar_width, correctness, bar_width, label='Correctness (Sistema)', color='#4C72B0')
    rects2 = ax.bar(x_positions - 1.0 * bar_width, relevancy, bar_width, label='Relevancy', color='#55A868')
    rects3 = ax.bar(x_positions + 0.0 * bar_width, faithfulness, bar_width, label='Summarization (LLM)', color="#D25FE1")
    rects4 = ax.bar(x_positions + 1.0 * bar_width, faithfulness, bar_width, label='Faithfulness (LLM)', color='#E1A95F')
    rects5 = ax.bar(x_positions + 2.0 * bar_width, final_score, bar_width, label='Final Score', color='#C44E52')

    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Evaluación Ragas: Sistema Completo')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, rotation=rot, ha=align)
    ax.set_ylim(0, 1.15) 
    ax.legend(loc='upper right', ncol=2)

    ax.bar_label(rects1, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects2, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects3, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects4, padding=3, fmt='%.2f', fontsize=8)
    ax.bar_label(rects5, padding=3, fmt='%.2f', fontsize=8)

    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_grafica_ragas_sistema.png'), dpi=300)
    plt.close()

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
        df_system = df_ragas[df_ragas['Configuracion'].str.contains('system')].copy()
        df_percept = df_ragas[~df_ragas['Configuracion'].str.contains('system')].copy()
        
        if not df_system.empty:
            generate_ragas_system_plot(df_system, OUTPUT_DIR)
        
        if not df_percept.empty:
            generate_ragas_perception_plot(df_percept, OUTPUT_DIR)

        print("- Gráficos de evaluación Ragas generados (5 y 6).")

if __name__ == "__main__":
    main()