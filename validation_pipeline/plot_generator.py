import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from config import METRICS_MAPPING, Y_LIM_METRICS

def plot_metrics_comparison(metrics_dict_list, labels, output_path, title="Comparativa de Métricas", detailed=True):
    """
    metrics_dict_list: Lista de diccionarios devueltos por normalize_ragas_metrics()
    labels: Lista de nombres de las configuraciones (ej: ['VLM', 'Híbrido'])
    detailed: Si es True, incluye Faithfulness y Answer similarity. Si es False, las omite.
    """
    if detailed:
        # 1. Preguntas Cortas / QA (Índices 0, 1, 2)
        # 2. Contexto (Índices 3, 4)
        # 3. Resumen / Reporte Global (Índices 5, 6, 7, 8)
        ordered_metrics_keys = [
            "answer_correctness",
            "answer_relevancy",
            "faithfulness",
            "context_precision",
            "context_recall",
            "answer_similarity",
            "rouge_score_recall_es",
            "hhem_fidelity_balanced",
            "bert_score_es"
        ]
    else:
        # Versión Simplificada: Sin "faithfulness" ni "answer_similarity"
        # 1. Preguntas Cortas / QA (Índices 0, 1)
        # 2. Contexto (Índices 2, 3)
        # 3. Resumen / Reporte Global (Índices 4, 5, 6)
        ordered_metrics_keys = [
            "answer_correctness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
            "rouge_score_recall_es",
            "hhem_fidelity_balanced",
            "bert_score_es"
        ]

    records = []
    for metrics, label in zip(metrics_dict_list, labels):
        for col in ordered_metrics_keys:
            if col in metrics and col in METRICS_MAPPING:
                records.append({
                    "Configuración": label,
                    "Métrica": METRICS_MAPPING[col],
                    "Puntuación": metrics[col]
                })
                
    df_plot = pd.DataFrame(records)
    
    plt.figure(figsize=(11, 6.5))
    ax = sns.barplot(
        data=df_plot, 
        x="Métrica", 
        y="Puntuación", 
        hue="Configuración",
        zorder=3  # Forzamos las barras a renderizarse por encima de las franjas de fondo
    )
    
    # Restricciones estéticas y de diseño
    ax.set_ylim(0, 110)  # Dejamos un margen superior de cortesía para los títulos de grupo
    ax.set_ylabel("Puntuación (0 - 100)", fontsize=12, labelpad=10)
    ax.set_xlabel("")
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(fontsize=11)
    
    suffix = " (Detallada)" if detailed else " (Resumida)"
    plt.title(title + suffix, pad=25, fontsize=12, weight='bold')
    
    # -----------------------------------------------------------------
    # DELIMITACIÓN VISUAL DE CATEGORÍAS (Preguntas, Contexto, Resumen)
    # -----------------------------------------------------------------
    text_style = dict(ha="center", va="center", color="#2C3E50", weight="bold", fontsize=9.5)
    bbox_style = dict(facecolor='white', alpha=0.85, edgecolor='none', boxstyle='round,pad=0.3')

    if detailed:
        # 1. Franjas de fondo translúcido (axvspan) - 9 Métricas
        ax.axvspan(-0.5, 2.5, color='#F0F4F8', alpha=0.6, zorder=1) # Preguntas Cortas (Fondo Azul sutil, 3 métricas)
        ax.axvspan(2.5, 4.5, color='#F6EEFA', alpha=0.6, zorder=1)  # Contexto (Fondo Violeta sutil, 2 métricas)
        ax.axvspan(4.5, 8.5, color='#EDF7F2', alpha=0.6, zorder=1)  # Resumen (Fondo Verde sutil, 4 métricas)
        
        # 2. Separadores discontinuos verticales (axvline)
        ax.axvline(2.5, color='#7F8C8D', linestyle='--', alpha=0.5, linewidth=1.2, zorder=2)
        ax.axvline(4.5, color='#7F8C8D', linestyle='--', alpha=0.5, linewidth=1.2, zorder=2)
        
        # 3. Etiquetas de cabecera elegantes, centradas en sus rangos
        ax.text(1.0, 104, "Preguntas Cortas", bbox=bbox_style, **text_style)
        ax.text(3.5, 104, "Contexto", bbox=bbox_style, **text_style)
        ax.text(6.5, 104, "Resumen", bbox=bbox_style, **text_style)
    else:
        # 1. Franjas de fondo translúcido (axvspan) - 7 Métricas (Sin Faithfulness ni Answer Similarity)
        ax.axvspan(-0.5, 1.5, color='#F0F4F8', alpha=0.6, zorder=1) # Preguntas Cortas (Fondo Azul sutil, 2 métricas)
        ax.axvspan(1.5, 3.5, color='#F6EEFA', alpha=0.6, zorder=1)  # Contexto (Fondo Violeta sutil, 2 métricas)
        ax.axvspan(3.5, 6.5, color='#EDF7F2', alpha=0.6, zorder=1)  # Resumen (Fondo Verde sutil, 3 métricas)
        
        # 2. Separadores discontinuos verticales (axvline)
        ax.axvline(1.5, color='#7F8C8D', linestyle='--', alpha=0.5, linewidth=1.2, zorder=2)
        ax.axvline(3.5, color='#7F8C8D', linestyle='--', alpha=0.5, linewidth=1.2, zorder=2)
        
        # 3. Etiquetas de cabecera ajustadas para la visualización resumida
        ax.text(0.5, 104, "Preguntas Cortas", bbox=bbox_style, **text_style)
        ax.text(2.5, 104, "Contexto", bbox=bbox_style, **text_style)
        ax.text(5.0, 104, "Resumen", bbox=bbox_style, **text_style)    

    # Limpieza de bordes y rejilla interna
    sns.despine(left=True, bottom=True)
    ax.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
    
    # Ajustar leyenda
    ax.legend(loc='lower left', frameon=True, facecolor='white', edgecolor='none', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_reduction_evolution(dist_data, dist_metrics, mse_data, mse_metrics, output_path):
    """
    Lineplot evolutivo cruzado: Compara la puntuación media de QA (Correctness y Relevancy)
    frente al porcentaje de reducción del dataset.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Preparamos puntos (% Reducción, Score Medio QA)
    def extract_points(data_rows, metrics):
        points = []
        if not data_rows:
            return points
            
        base_mb = data_rows[0][2] # El primer elemento es la 'Base' (Sin filtro)
        
        for row, metric_dict in zip(data_rows, metrics):
            current_mb = row[2]
            
            # Cálculo del porcentaje de reducción relativo a la base
            reduction_pct = ((base_mb - current_mb) / base_mb * 100) if base_mb > 0 else 0.0
            
            if metric_dict:
                # Filtrar y calcular SÓLO la media de preguntas cortas (QA)
                qa_scores = [
                    metric_dict.get("answer_correctness", 0.0),
                    metric_dict.get("answer_relevancy", 0.0)
                ]
                score = np.mean(qa_scores)
            else:
                score = 0.0
                
            points.append((reduction_pct, score))
            
        # Ordenamos de menor a mayor reducción (0% -> 100%)
        return sorted(points, key=lambda x: x[0])

    dist_pts = extract_points(dist_data, dist_metrics)
    mse_pts = extract_points(mse_data, mse_metrics)

    plt.figure(figsize=(10, 6))
    
    # SOTA: Líneas continuas para ambas. La diferenciación recae en el color y el marcador.
    plt.plot([p[0] for p in dist_pts], [p[1] for p in dist_pts], 
             marker='o', linestyle='-', linewidth=2, label='Filtro Distancia', color='#4C72B0')
    plt.plot([p[0] for p in mse_pts], [p[1] for p in mse_pts], 
             marker='s', linestyle='-', linewidth=2, label='Filtro MSE', color='#C44E52')
    
    # Anclaje estricto del eje Y
    plt.ylim(0, 100)
    
    # Ajuste del eje X para que empiece en 0% (con ligero margen) y vaya hasta el máximo
    all_pct = [p[0] for p in dist_pts + mse_pts]
    max_pct = max(all_pct) if all_pct else 100
    plt.xlim(-2, max_pct * 1.05) 
    
    plt.title("Evolución Puntuación Preguntas Cortas vs. Reducción de Contexto", fontsize=14, pad=15)
    plt.xlabel("Porcentaje de Reducción del Dataset (%)", fontsize=12)
    plt.ylabel("Puntuación Media RAGAS (Ans. Correctness y Relevancy)", fontsize=12)
    
    # loc='best' permite al algoritmo calcular el cuadrante más libre de puntos
    plt.legend(loc='best', frameon=True, facecolor='white', edgecolor='none', framealpha=0.9)
    plt.grid(True, linestyle=':', alpha=0.7)
    
    sns.despine()
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_computational_performance(table_rows, output_path, title):
    """Gráfico de barras para el tiempo global de inferencia."""
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    
    labels = [row[0] for row in table_rows]
    times = [row[1].get('tiempo_global', 0.0) for row in table_rows]

    x = np.arange(len(labels))
    plt.figure(figsize=(9, 5))
    
    rects = plt.bar(x, times, width=0.4, color='#55A868')
    plt.title(title, fontsize=14, pad=15)
    plt.ylabel("Tiempo Global de Ejecución (s)", fontsize=12)
    plt.xticks(x, labels, rotation=15 if len(labels)>3 else 0)
    
    # CORRECCIÓN: Se pasa el contenedor 'rects' entero, sin el bucle for
    plt.gca().bar_label(rects, padding=3, fmt='%.1f s', fontsize=9)
        
    sns.despine()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_aggregated_perception(table_rows, output_path_base):
    """Métricas avanzadas para el Experimento 1: Latencia extrema y FPS."""
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    
    labels = [row[0] for row in table_rows]
    medias = [row[3].get('media_segundos', 0) for row in table_rows]
    p99s = [row[3].get('percentil_99', 0) for row in table_rows]
    fps = [row[3].get('fps_equivalente', 0) for row in table_rows]
    
    x = np.arange(len(labels))
    width = 0.35
    
    # 1. Media vs P99
    fig, ax = plt.subplots(figsize=(9, 5))
    rects1 = ax.bar(x - width/2, medias, width, label='Media (s)', color='#4C72B0')
    rects2 = ax.bar(x + width/2, p99s, width, label='P99 (Caso Extremo)', color='#C44E52')
    ax.set_ylabel('Segundos')
    ax.set_title('Latencia de Inferencia Visual: Media vs P99')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left')
    
    # Aquí el bucle SÍ es correcto porque itera sobre una lista de contenedores
    for r in [rects1, rects2]: 
        ax.bar_label(r, padding=3, fmt='%.2f')
        
    sns.despine()
    plt.tight_layout()
    plt.savefig(f"{output_path_base}_latencia.pdf", dpi=300)
    plt.close()
    
    # 2. FPS
    plt.figure(figsize=(8, 4))
    rects_fps = plt.bar(x, fps, width=0.4, color='#E1A95F')
    plt.title('Rendimiento Visual Equivalente (FPS)')
    plt.ylabel('Frames por Segundo')
    plt.xticks(x, labels)
    
    # CORRECCIÓN: Se pasa el contenedor 'rects_fps' entero, sin el bucle for
    plt.gca().bar_label(rects_fps, padding=3, fmt='%.1f')
    
    sns.despine()
    plt.tight_layout()
    plt.savefig(f"{output_path_base}_fps.pdf", dpi=300)
    plt.close()
