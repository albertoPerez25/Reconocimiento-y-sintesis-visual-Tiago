import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Reutilización directa de la extracción (sin tocar el código base compartido)
from config import set_academic_style
from extractor import load_ragas_csv
from transformer import normalize_ragas_metrics

# ================= CONFIGURACIÓN =================
# Resolución dinámica de la raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

BASE_DIR = os.path.join(project_root, "docs", "autogenerate_metrics", "exp4_limites_palabras")
RESULTS_CSV = os.path.join(BASE_DIR, "experimento_4_limite_palabras_resultados.csv")

# Se ordenan para asegurar coherencia visual en las gráficas y tablas
WORD_LIMITS = sorted([100, 200, 300, 400, 500, 600, 700, 800]) #[50, 100, 150, 200, 250, 300, 350, 400]

# Diccionario exclusivo para el Exp 4 (Filtrando las métricas de QA y Contexto a 0)
EXP4_METRICS = {
    "answer_similarity": "Ans. Similarity",
    "rouge_score_recall_es": "ROUGE-1",
    "hhem_fidelity_balanced": "HHEM",
    "bert_score_es": "BERTScore"
}
# =================================================

def generate_exp4_performance_table(csv_path):
    """
    Genera una tabla LaTeX específica para el Experimento 4, evaluando 
    la adherencia del LLM a las directrices y el tiempo de respuesta.
    """
    df = pd.read_csv(csv_path)
    df = df.sort_values(by="limite_solicitado")
    
    rows_latex = ""
    for _, row in df.iterrows():
        lim_solicitado = int(row['limite_solicitado'])
        
        # Filtro: Ignorar los límites que no estén en tu lista WORD_LIMITS
        if lim_solicitado not in WORD_LIMITS:
            continue
            
        palabras_reales = int(row['palabras_reales'])
        t_gen_llm = row['tiempo_generacion_llm']
        
        # Se elimina la columna de RAGAS
        rows_latex += f"            {lim_solicitado} pal. & {palabras_reales} & {t_gen_llm:.2f} \\\\\n"
        
    latex = f"""
    \\begin{{table}}[htpb]
        \\centering
        \\begin{{tabular}}{{lcc}}
            \\toprule
            \\textbf{{Límite Solicitado}} & \\textbf{{Palabras Generadas}} & \\textbf{{Tiempo Generación (s)}} \\\\
            \\midrule
{rows_latex.rstrip()}
            \\bottomrule
        \\end{{tabular}}
        \\caption{{Evaluación del rendimiento y adherencia a los límites de longitud impuestos al modelo generador (Qwen3.5/Llama3).}}
        \\label{{tab:exp4_rendimiento_llm}}
    \\end{{table}}
    """
    return latex


def generate_exp4_ragas_table(metrics_dict_list, labels, table_caption, table_label):
    """Genera la tabla LaTeX filtrada exclusivamente con las 4 métricas válidas del Exp 4."""
    metrics_keys = list(EXP4_METRICS.keys())
    metrics_names = list(EXP4_METRICS.values())
    
    header_cols = "l" + "c" * len(metrics_names)
    header_names = " & ".join([f"\\textbf{{{name}}}" for name in metrics_names])
    
    rows_latex = ""
    for metrics, label in zip(metrics_dict_list, labels):
        row_vals = [f"{metrics.get(k, 0.0):.2f}" for k in metrics_keys]
        rows_latex += f"            {label} & " + " & ".join(row_vals) + " \\\\\n"
        
    latex = f"""
    \\begin{{table}}[htpb]
        \\centering
        \\resizebox{{\\textwidth}}{{!}}{{
            \\begin{{tabular}}{{{header_cols}}}
                \\toprule
                \\textbf{{Configuración}} & {header_names} \\\\
                \\midrule
{rows_latex.rstrip()}
                \\bottomrule
            \\end{{tabular}}
        }}
        \\caption{{{table_caption}}}
        \\label{{{table_label}}}
    \\end{{table}}
    """
    return latex


def plot_exp4_metrics(metrics_dict_list, labels, output_path, title):
    """Renderiza una gráfica adaptada a las 4 métricas de resumen del Exp 4."""
    records = []
    for metrics, label in zip(metrics_dict_list, labels):
        for col, name in EXP4_METRICS.items():
            if col in metrics:
                records.append({
                    "Configuración": label,
                    "Métrica": name,
                    "Puntuación": metrics[col]
                })
                
    df_plot = pd.DataFrame(records)
    
    plt.figure(figsize=(10, 6.5))
    ax = sns.barplot(
        data=df_plot, 
        x="Métrica", 
        y="Puntuación", 
        hue="Configuración",
        zorder=3
    )
    
    ax.set_ylim(0, 110)
    ax.set_xlabel("")
    ax.set_ylabel("Puntuación (0 - 100)", fontsize=12, labelpad=10)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)
    
    plt.title(title, pad=25, fontsize=12, weight='bold')
    
    # Delimitación visual para el bloque único de resumen
    ax.axvspan(-0.5, 3.5, color='#EDF7F2', alpha=0.6, zorder=1) # Fondo Verde sutil
    
    text_style = dict(ha="center", va="center", color="#2C3E50", weight="bold", fontsize=10)
    bbox_style = dict(facecolor='white', alpha=0.85, edgecolor='none', boxstyle='round,pad=0.3')
    ax.text(1.5, 104, "Resumen Global", bbox=bbox_style, **text_style)

    sns.despine(left=True, bottom=True)
    ax.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
    
    # Legend adaptada para no pisar las barras
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=True, facecolor='white', edgecolor='none', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    set_academic_style()
    os.makedirs("salidas", exist_ok=True)
    
    plot_metrics = []
    plot_labels = []
    
    # 1. Extracción y Transformación
    for limit in WORD_LIMITS:
        csv_filename = f"ragas_limite_{limit}_system_evaluation.csv"
        csv_path = os.path.join(BASE_DIR, csv_filename)
        
        df_ragas = load_ragas_csv(csv_path)
        
        if not df_ragas.empty:
            ragas_normalized = normalize_ragas_metrics(df_ragas)
            plot_metrics.append(ragas_normalized)
            plot_labels.append(f"{limit} pal.")
        else:
            print(f"[WARNING] No se encontró o está vacío el archivo: {csv_filename}")
            
    # 2. Generación de Gráficas y Tablas RAGAS
    if plot_metrics:
        # Usamos nuestra propia función de dibujado local (1 sola gráfica, no hace falta detallada/resumida porque ya son 4)
        plot_exp4_metrics(
            metrics_dict_list=plot_metrics, 
            labels=plot_labels, 
            output_path="salidas/exp4_calidad_resumen.pdf", 
            title="Impacto del Límite de Palabras en la Calidad del Resumen"
        )
        
        # Usamos nuestra propia función de tabla local
        ragas_table_latex = generate_exp4_ragas_table(
            metrics_dict_list=plot_metrics, 
            labels=plot_labels, 
            table_caption="Evaluación de la calidad cognitiva mediante RAGAS según el límite de palabras del resumen.", 
            table_label="tab:exp4_ragas_calidad"
        )
        print("% === EXPERIMENTO 4: CALIDAD RAGAS ===")
        print(ragas_table_latex)

    # 3. Generación de Tabla de Rendimiento Específica
    if os.path.exists(RESULTS_CSV):
        perf_table_latex = generate_exp4_performance_table(RESULTS_CSV)
        print("\n% === EXPERIMENTO 4: RENDIMIENTO LLM ===")
        print(perf_table_latex)
    else:
        print(f"\n[ERROR CRÍTICO] Archivo base no encontrado: {RESULTS_CSV}")

if __name__ == "__main__":
    main()
