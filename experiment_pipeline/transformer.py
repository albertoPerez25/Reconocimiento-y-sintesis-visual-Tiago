import pandas as pd
from config import CHARS_PER_TOKEN, METRICS_MAPPING
import statistics

def _calc_stats(times_list):
    """Subrutina matemática para calcular estadísticas sobre una lista de tiempos."""
    if not times_list:
        return {}
    
    n = len(times_list)
    times_sorted = sorted(times_list)
    mean_val = statistics.mean(times_list)
    median_val = statistics.median(times_list)
    std_dev_val = statistics.stdev(times_list) if n > 1 else 0.0
    variance_val = statistics.variance(times_list) if n > 1 else 0.0

    rounded_times = [round(t, 2) for t in times_list]
    try:
        mode_val = statistics.mode(rounded_times)
    except statistics.StatisticsError:
        mode_val = rounded_times[0]

    p90_idx = int(0.90 * n)
    p99_idx = int(0.99 * n)
    fps = (1.0 / mean_val) if mean_val > 0 else 0.0

    return {
        "media_segundos": round(mean_val, 3),
        "mediana_segundos": round(median_val, 3),
        "desviacion_tipica": round(std_dev_val, 3),
        "varianza": round(variance_val, 3),
        "maximo_segundos": round(times_sorted[-1], 3),
        "minimo_segundos": round(times_sorted[0], 3),
        "moda_aprox_segundos": round(mode_val, 3),
        "percentil_90": round(times_sorted[p90_idx] if p90_idx < n else times_sorted[-1], 3),
        "percentil_99": round(times_sorted[p99_idx] if p99_idx < n else times_sorted[-1], 3),
        "fps_equivalente": round(fps, 2),
        "total_frames": n
    }


def calculate_advanced_perception_stats(raw_data):
    """
    Usa las claves reales navegando correctamente por la jerarquía anidada del JSON.
    Soporta tanto el formato antiguo (acumulativo por frame) como el nuevo (sesión única).
    """
    if not raw_data:
        return {}

    tiempos_globales = []
    tiempos_vacia = []
    tiempos_evento = []
    tiempos_vlm = []

    # --- DETECCIÓN Y ADAPTACIÓN DE FORMATO (RETROCOMPATIBILIDAD) ---
    # Si hay más de un elemento principal en la lista y la primera entrada ya contiene 
    # una lista en "tiempos_procesado", estamos ante el formato antiguo duplicado.
    es_formato_antiguo_exponencial = (
        isinstance(raw_data, list) and 
        len(raw_data) > 1 and 
        isinstance(raw_data[0], dict) and 
        isinstance(raw_data[0].get("tiempos_procesado"), list)
    )

    if es_formato_antiguo_exponencial:
        # Modo histórico: Nos quedamos únicamente con la última entrada (la foto final completa)
        datos_a_procesar = [raw_data[-1]]
    else:
        # Modo limpio (un solo objeto de sesión) o listas aplanadas directas
        datos_a_procesar = raw_data

    # El resto del bucle se mantiene intacto, fiel a tu estructura original
    for entry in datos_a_procesar:
        procesados = entry.get("tiempos_procesado", []) if isinstance(entry, dict) else [entry]
        
        for record in procesados:
            # Caso 1: VLM Aislado (lista de números simples sin keys de YOLO)
            if isinstance(record, (int, float)):
                t_total = record
                if t_total > 0:
                    tiempos_globales.append(t_total)
                
            # Caso 2: Arquitectura Híbrida (lista de diccionarios)
            elif isinstance(record, dict):
                t_total = record.get("total_seconds", 0.0)
                t_yolo = record.get("yolo_seconds", 0.0)
                t_vlm = record.get("vlm_seconds", 0.0)
                
                if t_total > 0:
                    tiempos_globales.append(t_total)
                
                if t_vlm == 0 and t_yolo > 0:
                    tiempos_vacia.append(t_yolo)
                elif t_vlm > 0:
                    tiempos_evento.append(t_total)
                    tiempos_vlm.append(t_vlm)

    if not tiempos_globales:
        return {}

    stats = _calc_stats(tiempos_globales)
    
    # Si no hay diferenciación, todo es la media global
    if not tiempos_vacia and not tiempos_evento:
        stats["media_segundos_vacia"] = stats.get("media_segundos", 0.0)
        stats["media_segundos_evento"] = stats.get("media_segundos", 0.0)
        stats["media_segundos_vlm"] = stats.get("media_segundos", 0.0)
    else:
        stats["media_segundos_vacia"] = _calc_stats(tiempos_vacia).get("media_segundos", 0.0)
        stats["media_segundos_evento"] = _calc_stats(tiempos_evento).get("media_segundos", 0.0)
        stats["media_segundos_vlm"] = statistics.mean(tiempos_vlm) if tiempos_vlm else 0.0
        
    return stats

def normalize_ragas_metrics(df_ragas):
    if df_ragas.empty:
        return {}
    means = {}
    for col in METRICS_MAPPING.keys():
        if col in df_ragas.columns:
            means[col] = round(df_ragas[col].mean() * 100, 2)
        else:
            means[col] = 0.00
    return means


def extract_performance_stats(merged_data, adv_stats=None):
    if not merged_data:
        return {}
        
    caracteres = merged_data.get("caracteres_contexto_visual", 0)
    tokens = caracteres // CHARS_PER_TOKEN
    
    # CORRECCIÓN DE LATENCIA GLOBAL:
    # Priorizamos el tiempo total del reportero (tiempo real físico).
    t_reporter = merged_data.get("tiempo_total_segundos", 0.0)
    t_eval_inferencia = merged_data.get("tiempo_inferencia_total_segundos", 0.0)
    tiempo_global = t_reporter if t_reporter > 0 else t_eval_inferencia
    
    if adv_stats and adv_stats.get("media_segundos", 0) > 0:
        latencia_percepcion = adv_stats.get("media_segundos")
    else:
        latencia_percepcion = merged_data.get("tiempo_percepcion_segundos", 0.0)
        
    stats = {
        "tiempo_global": round(tiempo_global, 2),
        "capturas_totales": merged_data.get("total_imagenes_procesadas", 0),
        "tokens_promedio": tokens,
        "latencia_media_percepcion": round(latencia_percepcion, 2)
    }
    return stats