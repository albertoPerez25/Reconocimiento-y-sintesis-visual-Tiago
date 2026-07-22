from config import METRICS_MAPPING

def generate_exp1_table(stats_vlm, stats_hibrido, adv_vlm, adv_hibrido):
    # Usamos las claves calculadas en transformer.py para rellenar los ceros
    vac_vlm = adv_vlm.get('media_segundos_vacia', '0.00')
    eve_vlm = adv_vlm.get('media_segundos_evento', '0.00')
    vac_hib = adv_hibrido.get('media_segundos_vacia', '0.00')
    eve_hib = adv_hibrido.get('media_segundos_evento', '0.00')

    latex = f"""
    \\begin{{table}}[htpb]
        \\centering
        \\begin{{tabular}}{{lcc}}
            \\toprule
            \\textbf{{Métrica de Rendimiento}} & \\textbf{{VLM (Aislado)}} & \\textbf{{Percepción Híbrida}} \\\\
            \\midrule
            Tiempo de ejecución global (s) & {stats_vlm.get('tiempo_global', '0.00')} & {stats_hibrido.get('tiempo_global', '0.00')} \\\\
            Tiempo medio por captura vacía (s) & {vac_vlm} & {vac_hib} \\\\
            Tiempo medio por captura con eventos (s) & {eve_vlm} & {eve_hib} \\\\
            \\bottomrule
        \\end{{tabular}}
        \\caption{{Comparativa de tiempos de ejecución entre la percepción basada exclusivamente en VLM y la arquitectura híbrida.}}
        \\label{{tab:exp1_tiempos}}
    \\end{{table}}
    """
    return latex

def generate_exp1_advanced_table(adv_vlm, adv_hibrido):
    """Genera una tabla con el análisis estadístico profundo de la inferencia visual."""
    latex = f"""
    \\begin{{table}}[htpb]
        \\centering
        \\begin{{tabular}}{{lcc}}
            \\toprule
            \\textbf{{Estadística de Inferencia}} & \\textbf{{VLM (Aislado)}} & \\textbf{{Percepción Híbrida}} \\\\
            \\midrule
            Fotogramas Analizados & {adv_vlm.get('total_frames', 0)} & {adv_hibrido.get('total_frames', 0)} \\\\
            Media (s) / Mediana (s) & {adv_vlm.get('media_segundos', '0.00')} / {adv_vlm.get('mediana_segundos', '0.00')} & {adv_hibrido.get('media_segundos', '0.00')} / {adv_hibrido.get('mediana_segundos', '0.00')} \\\\
            Moda (s) & {adv_vlm.get('moda_aprox_segundos', '0.00')} & {adv_hibrido.get('moda_aprox_segundos', '0.00')} \\\\
            Desviación Típica (s) & {adv_vlm.get('desviacion_tipica', '0.00')} & {adv_hibrido.get('desviacion_tipica', '0.00')} \\\\
            Percentil 90 (s) & {adv_vlm.get('percentil_90', '0.00')} & {adv_hibrido.get('percentil_90', '0.00')} \\\\
            Percentil 99 (s) & {adv_vlm.get('percentil_99', '0.00')} & {adv_hibrido.get('percentil_99', '0.00')} \\\\
            FPS Equivalente & {adv_vlm.get('fps_equivalente', '0.00')} & {adv_hibrido.get('fps_equivalente', '0.00')} \\\\
            \\bottomrule
        \\end{{tabular}}
        \\caption{{Análisis estadístico avanzado del rendimiento de inferencia visual frame a frame.}}
        \\label{{tab:exp1_inferencia_avanzada}}
    \\end{{table}}
    """
    return latex

def generate_exp2_table(rows_data, is_mse=False):
    """
    rows_data: lista de tuplas (Nombre_Config, stats_dict, size_mb, adv_stats)
    """
    label = "tab:exp2_mse_recursos" if is_mse else "tab:exp2_distancia_recursos"
    caption = ("Evaluación del consumo de recursos y tamaño del dataset fotográfico "
               "para el filtrado dinámico mediante MSE.") if is_mse else \
              ("Evaluación del consumo de recursos y tamaño del dataset fotográfico "
               "para el filtrado por distancia geométrica.")
    
    if not rows_data:
        return ""

    base_mb = rows_data[0][2]
    
    rows_latex = ""
    # Desempaquetamos los 4 elementos. Ignoramos adv_stats (el cuarto) si no se usa.
    for config_name, stats, size_mb, _ in rows_data:
        reduction_pct = ((base_mb - size_mb) / base_mb * 100) if base_mb > 0 else 0.0
        
        # Columnas: Config | Capturas | Tamaño (MB) | Red. (%) | Tokens | Latencia (s)
        rows_latex += (
            f"            {config_name:<22} & {stats.get('capturas_totales', 0)} & "
            f"{size_mb:.2f} & {reduction_pct:.1f}\% & {stats.get('tokens_promedio', 0)} & "
            f"{stats.get('tiempo_global', '0.00')} \\\\\n"
        )
        
    latex = f"""
    \\begin{{table}}[htpb]
        \\centering
        \\begin{{tabular}}{{lccccc}}
            \\toprule
            \\textbf{{Configuración}} & \\textbf{{Capturas}} & \\textbf{{MB}} & \\textbf{{Red. (\%)}} & \\textbf{{Tokens}} & \\textbf{{Latencia (s)}} \\\\
            \\midrule
{rows_latex.rstrip()}
            \\bottomrule
        \\end{{tabular}}
        \\caption{{{caption}}}
        \\label{{{label}}}
    \\end{{table}}
    """
    return latex

def generate_exp3_table(stats_estatico, stats_video):
    """Genera la tabla comparativa entre imagen estática y secuencias de vídeo."""
    latex = f"""
    \\begin{{table}}[htpb]
        \\centering
        \\begin{{tabular}}{{lccc}}
            \\toprule
            \\textbf{{Configuración}} & \\textbf{{Tokens}} & \\textbf{{Latencia Inferencia (s)}} & \\textbf{{Tiempo Global (s)}} \\\\
            \\midrule
            VLM Estático (1.0m) & {stats_estatico.get('tokens_promedio', 0)} & {stats_estatico.get('latencia_media_percepcion', '0.00')} & {stats_estatico.get('tiempo_global', '0.00')} \\\\
            VLM Vídeo & {stats_video.get('tokens_promedio', 0)} & {stats_video.get('latencia_media_percepcion', '0.00')} & {stats_video.get('tiempo_global', '0.00')} \\\\
            \\bottomrule
        \\end{{tabular}}
        \\caption{{Comparativa de consumo de recursos y latencia entre el análisis de fotogramas estáticos y secuencias de vídeo.}}
        \\label{{tab:exp3_recursos}}
    \\end{{table}}
    """
    return latex

def generate_ragas_table(metrics_dict_list, labels, table_caption, table_label):
    """Genera de forma dinámica una tabla con todas las métricas RAGAS mapeadas."""
    metrics_keys = list(METRICS_MAPPING.keys())
    metrics_names = list(METRICS_MAPPING.values())
    
    # Formato de cabeceras. Usamos resizebox para que quepa en el ancho de la página
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
