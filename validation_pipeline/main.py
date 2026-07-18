import os
from config import (
    set_academic_style, EXP1_CONFIG, EXP2_DIST_CONFIG, EXP2_MSE_CONFIG, EXP3_CONFIG
)
from extractor import (
    load_ragas_csv, load_merged_performance_data, get_dataset_size_mb, load_raw_perception_times
)
from transformer import (
    normalize_ragas_metrics, extract_performance_stats, calculate_advanced_perception_stats
)
from latex_generator import (
    generate_exp1_table, generate_exp1_advanced_table, generate_exp2_table, generate_exp3_table, generate_ragas_table
)
from plot_generator import (
    plot_metrics_comparison, plot_reduction_evolution, plot_computational_performance, plot_aggregated_perception
)

def procesar_experimento_generico(config_list, output_plot_name, plot_title, latex_generator_funcs, is_mse=False):
    table_rows = []
    plot_metrics = []
    plot_labels = []
    
    for cfg in config_list:
        # E - Extract
        df_ragas = load_ragas_csv(cfg["csv_path"])
        json_data_merged = load_merged_performance_data(cfg["eval_dir"])
        
        size_mb = get_dataset_size_mb(cfg["dataset_path"]) if "dataset_path" in cfg else 0.0
        
        # Carga los datos crudos del perceptor y aplica la lógica de agregación del script original
        raw_times = load_raw_perception_times(cfg["perception_json_path"]) if "perception_json_path" in cfg else []
        adv_stats = calculate_advanced_perception_stats(raw_times)
        
        # T - Transform
        ragas_normalized = normalize_ragas_metrics(df_ragas)
        perf_stats = extract_performance_stats(json_data_merged, adv_stats)
        
        table_rows.append((cfg["label"], perf_stats, size_mb, adv_stats))
        
        if ragas_normalized:
            plot_metrics.append(ragas_normalized)
            plot_labels.append(cfg["label"])
            
    # L - Load (Generar gráficos y tablas LaTeX)
    if plot_metrics:
        # Construimos el nombre detallado usando el sufijo solicitado
        if output_plot_name.endswith(".pdf"):
            detailed_plot_name = output_plot_name[:-4] + "_detallada.pdf"
        else:
            detailed_plot_name = output_plot_name + "_detallada"
            
        # Gráfica Detallada (Incluye todas las métricas RAGAS)
        plot_metrics_comparison(plot_metrics, plot_labels, detailed_plot_name, plot_title, detailed=True)
        
        # Gráfica Resumida (Sin Faithfulness ni Answer similarity; conserva el nombre original)
        plot_metrics_comparison(plot_metrics, plot_labels, output_plot_name, plot_title, detailed=False)
        
    latex_outputs = []
    for func in latex_generator_funcs:
        if func.__name__ == "generate_exp2_table":
            latex_outputs.append(func(table_rows, is_mse=is_mse))
        elif func.__name__ in ["generate_exp1_table", "generate_exp1_advanced_table"]:
            if len(table_rows) >= 2:
                stats_vlm = table_rows[0][1]
                stats_hibrido = table_rows[1][1]
                adv_vlm = table_rows[0][3]
                adv_hibrido = table_rows[1][3]
                if func.__name__ == "generate_exp1_table":
                    latex_outputs.append(func(stats_vlm, stats_hibrido, adv_vlm, adv_hibrido))
                else:
                    latex_outputs.append(func(adv_vlm, adv_hibrido))
        elif func.__name__ == "generate_exp3_table":
            if len(table_rows) >= 2:
                stats_estatico = table_rows[0][1]
                stats_video = table_rows[1][1]
                latex_outputs.append(func(stats_estatico, stats_video))
                
    if plot_metrics:
        if "exp1" in output_plot_name:
            c_ragas = "Evaluación de la calidad de respuesta mediante métricas RAGAS para la comparativa entre VLM Aislado y la Arquitectura Híbrida."
            l_ragas = "tab:exp1_ragas"
        elif "distancia" in output_plot_name:
            c_ragas = "Evaluación de la calidad de respuesta mediante métricas RAGAS para el filtrado por distancia geométrica."
            l_ragas = "tab:exp2_dist_ragas"
        elif "mse" in output_plot_name:
            c_ragas = "Evaluación de la calidad de respuesta mediante métricas RAGAS para el filtrado dinámico mediante MSE."
            l_ragas = "tab:exp2_mse_ragas"
        else:
            c_ragas = "Evaluación de la calidad de respuesta mediante métricas RAGAS para fotogramas estáticos y secuencias de vídeo."
            l_ragas = "tab:exp3_ragas"
            
        tabla_ragas_latex = generate_ragas_table(plot_metrics, plot_labels, c_ragas, l_ragas)
        latex_outputs.append(tabla_ragas_latex)
                
    return "\n".join(latex_outputs), table_rows, plot_metrics


def main():
    set_academic_style()
    os.makedirs("salidas", exist_ok=True)
    
    print("% === EXPERIMENTO 1: HÍBRIDO VS VLM ===")
    latex_exp1, data_exp1, _ = procesar_experimento_generico(
        EXP1_CONFIG, "salidas/exp1_calidad.pdf", "VLM vs Híbrido", 
        [generate_exp1_table, generate_exp1_advanced_table]
    )
    plot_aggregated_perception(data_exp1, "salidas/exp1_percepcion")
    print(latex_exp1)
    
    print("% === EXPERIMENTO 2A: REDUCCIÓN POR DISTANCIA ===")
    latex_exp2_dist, data_dist, metrics_dist = procesar_experimento_generico(
        EXP2_DIST_CONFIG, "salidas/exp2_distancia.pdf", "Reducción por Distancia",
        [generate_exp2_table], is_mse=False
    )
    print(latex_exp2_dist)

    print("% === EXPERIMENTO 2B: REDUCCIÓN POR MSE ===")
    latex_exp2_mse, data_mse, metrics_mse = procesar_experimento_generico(
        EXP2_MSE_CONFIG, "salidas/exp2_mse.pdf", "Reducción por MSE",
        [generate_exp2_table], is_mse=True
    )
    print(latex_exp2_mse)
    
    plot_reduction_evolution(
        data_dist, metrics_dist, 
        data_mse, metrics_mse, 
        "salidas/exp2_evolucion_reducciones.pdf"
    )
    
    print("% === EXPERIMENTO 3: ESTÁTICO VS VÍDEO ===")
    latex_exp3, _, _ = procesar_experimento_generico(
        EXP3_CONFIG, "salidas/exp3_calidad.pdf", "Fotogramas vs Vídeo",
        [generate_exp3_table]
    )
    print(latex_exp3)

if __name__ == "__main__":
    main()
