#!/usr/bin/env python3
import os
import glob
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Theme configuration for professional plots
sns.set_theme(style="whitegrid", palette="pastel")

# Default Paths
JSON_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/comparativa_modelos.json"
RAGAS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"
OUTPUT_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"

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
            if 'answer_correctness' in df.columns and 'answer_relevancy' in df.columns:
                mean_correctness = df['answer_correctness'].mean()
                mean_relevancy = df['answer_relevancy'].mean()
                final_score = (mean_correctness + mean_relevancy) / 2.0
                
                summary_list.append({
                    'Configuracion': config_name,
                    'Correctness': round(mean_correctness, 3),
                    'Relevancy': round(mean_relevancy, 3),
                    'Final_Score': round(final_score, 3)
                })
        except Exception as e:
            print(f"Error procesando {filename}: {e}")

    if not summary_list:
        return None

    df_summary = pd.DataFrame(summary_list).sort_values(by='Final_Score', ascending=False)
    return df_summary

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
    """Prints and saves the Ragas evaluation summary table."""
    print("\n" + "="*60)
    print("  RESUMEN DE EVALUACIÓN RAGAS (Calidad de Respuesta)")
    print("="*60)
    print(df.to_string(index=False))
    print("="*60 + "\n")
    
    df.to_csv(os.path.join(output_dir, "tabla_resumen_ragas.csv"), index=False)

def generate_performance_plots(df, output_dir):
    """Genera las gráficas de rendimientos """
    # Tiempos de procesamiento
    plt.figure(figsize=(10, 6))
    summary_times = df.groupby('modelo_reportero')[['tiempo_percepcion_segundos', 'tiempo_llm_segundos']].mean()
    summary_times.plot(kind='bar', stacked=True, color=['#4C72B0', '#55A868'], figsize=(10, 6))
    plt.title("Tiempo Medio de Procesamiento por Patrulla", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos", fontsize=12)
    plt.legend(["Percepción (Visión)", "Razonamiento (LLM)"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_desglose_tiempos.png"), dpi=300)
    plt.close()

    # Latencia
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='modelo_reportero', y='segundos_por_imagen', errorbar='sd', capsize=.1)
    plt.title("Latencia del Modelo Visual", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos por Imagen procesada", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_latencia_visual.png"), dpi=300)
    plt.close()

    # Análisis de verbosidad
    plt.figure(figsize=(10, 6))
    summary_chars = df.groupby('modelo_reportero')[['caracteres_contexto_visual', 'caracteres_informe_final']].mean()
    summary_chars.plot(kind='bar', width=0.7, color=['#C44E52', '#8172B3'], figsize=(10, 6))
    plt.title("Análisis de Verbosidad (Texto procesado)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Cantidad de Caracteres", fontsize=12)
    plt.legend(["Contexto Visual Generado", "Informe Final (Llama-3)"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_analisis_verbosidad.png"), dpi=300)
    plt.close()

    # Estabilidad (boxplot)
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='modelo_reportero', y='tiempo_total_segundos', palette="Set2")
    sns.stripplot(data=df, x='modelo_reportero', y='tiempo_total_segundos', color=".3", size=6, alpha=0.6)
    plt.title("Estabilidad del Tiempo de Ejecución (Boxplot)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Tiempo Total (Segundos)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_estabilidad_tiempos.png"), dpi=300)
    plt.close()

def generate_ragas_plots(df, output_dir):
    """Genera las graficas agrupadas"""
    labels = df['Configuracion'].tolist()
    correctness = df['Correctness'].tolist()
    relevancy = df['Relevancy'].tolist()
    final_score = df['Final_Score'].tolist()

    x_positions = np.arange(len(labels))
    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    
    rects1 = ax.bar(x_positions - bar_width, correctness, bar_width, label='Correctness', color='#4C72B0')
    rects2 = ax.bar(x_positions, relevancy, bar_width, label='Relevancy', color='#55A868')
    rects3 = ax.bar(x_positions + bar_width, final_score, bar_width, label='Final Score', color='#C44E52')

    ax.set_ylabel('Puntuación (0.0 - 1.0)')
    ax.set_title('Comparativa de Calidad de Respuestas (Evaluación Ragas)')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylim(0, 1.1) 
    ax.legend()

    ax.bar_label(rects1, padding=3, fmt='%.2f', fontsize=9)
    ax.bar_label(rects2, padding=3, fmt='%.2f', fontsize=9)
    ax.bar_label(rects3, padding=3, fmt='%.2f', fontsize=9)

    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_grafica_comparativa_ragas.png'), dpi=300)
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
        generate_ragas_plots(df_ragas, OUTPUT_DIR)
        print("- Gráficos de evaluación Ragas generados (5).")

if __name__ == "__main__":
    main()