#!/usr/bin/env python3
import os
import json
import pandas as pd
import numpy as np

# ================= CONFIGURACIÓN DE RUTAS =================
METRICS_BASE_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/metrics_history_data/eval_OLD/6_size_datasets"
DATASETS_PHYSICAL_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/datasets/datasets/"

# Orden lógico de los datasets con la nomenclatura final
DATASETS = [
    {
        "name": "Dataset Reducido (4.0m)", 
        "metrics_folder": "6_eval_dataset_reduccion_4_0m", 
        "data_folder": "reduccion_4_0m",
        "description": "Captura de imágenes cada 4 metros recorridos por el robot."
    },
    {
        "name": "Dataset Reducido (2.0m)", 
        "metrics_folder": "6_eval_dataset_reduccion_2_0m", 
        "data_folder": "reduccion_2_0m",
        "description": "Captura de imágenes cada 2 metros recorridos por el robot."
    },
    {
        "name": "Dataset Reducido (1.0m - antiguo estándar)", 
        "metrics_folder": "6_eval_dataset_estandar_1_0m", 
        "data_folder": "reduccion_1_0m",
        "description": "Captura de imágenes cada 1 metro recorrido por el robot."
    },
    {
        "name": "Dataset Reducido (0.5m)", 
        "metrics_folder": "6_eval_dataset_reduccion_0_5m", 
        "data_folder": "reduccion_0_5m",
        "description": "Captura de imágenes cada 0.5 metros recorridos por el robot."
    },
    {
        "name": "Dataset Original", 
        "metrics_folder": "6_eval_dataset_grande", 
        "data_folder": "grande",
        "description": "Captura de imágenes continua a alta frecuencia."
    }
]

METRICS_TO_EXTRACT = {
    'answer_correctness': 'Correctness',
    'answer_relevancy': 'Relevancy',
    'faithfulness': 'Faithfulness',
    'context_precision': 'Context Precision',
    'context_recall': 'Context Recall',
    'context_entity_recall': 'Entity Recall'
}

def get_short_metrics(csv_path):
    """Calcula la media de las métricas SOLO para las preguntas cortas (short)"""
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return None

    results = {}
    if 'eval_type' in df.columns:
        df_short = df[df['eval_type'] == 'short']
    else:
        df_short = df 

    if df_short.empty:
        return None

    for col, print_name in METRICS_TO_EXTRACT.items():
        if col not in df_short.columns:
            results[print_name] = "N/A"
            continue
            
        col_data = df_short[col].replace(0.0, np.nan)
        if col_data.isna().all():
            results[print_name] = "N/A"
        else:
            results[print_name] = f"{col_data.mean():.2f}"
            
    return results

def get_total_time(json_path):
    """Extrae el tiempo total de la prueba desde comparativa_modelos.json"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        item = data[0] if isinstance(data, list) and len(data) > 0 else data
        if isinstance(item, dict):
            # Priorizamos el tiempo total real de la prueba
            t = item.get('tiempo_total_segundos', "N/A")
            if t == "N/A":
                # Fallback por si la métrica se llama diferente en alguna versión
                t = item.get('tiempo_inferencia_total_segundos', "N/A")
            return str(int(t)) if t != "N/A" else "N/A"
            
    except Exception as e:
        pass
    return "N/A"

def get_dataset_stats(data_folder):
    """Cuenta el número de imágenes reales y su tamaño."""
    target_path = os.path.join(DATASETS_PHYSICAL_DIR, data_folder, "vuelta_A")
    num_images, total_size_bytes = 0, 0
    
    if os.path.exists(target_path):
        for f in os.listdir(target_path):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(target_path, f)
                if os.path.isfile(filepath):
                    num_images += 1
                    total_size_bytes += os.path.getsize(filepath)
                    
    return num_images, total_size_bytes / (1024 * 1024)

def generate_report():
    print("Cómo afecta el uso de un menor número de imágenes para agilizar el proceso:")
    print("En todas las evaluaciones se ha usado el nodo híbrido con YOLO.\n")
    print("=" * 60 + "\n")
    
    for ds in DATASETS:
        metrics_folder_path = os.path.join(METRICS_BASE_DIR, ds['metrics_folder'])
        if not os.path.exists(metrics_folder_path):
            continue
            
        csv_files = [f for f in os.listdir(metrics_folder_path) if f.startswith("ragas_") and f.endswith(".csv")]
        csv_path = os.path.join(metrics_folder_path, csv_files[0]) if csv_files else None
        model_json_path = os.path.join(metrics_folder_path, "comparativa_modelos.json")
        
        # 1. Bloque RAGAS
        print(f"Mediciones RAGAS con el {ds['name']}")
        if csv_path:
            metrics = get_short_metrics(csv_path)
            if metrics:
                for name, value in metrics.items():
                    if value != "N/A":
                        print(f"{name}: {value}")
            else:
                print("No se encontraron métricas 'short' válidas.")
        else:
            print("No se encontró el CSV de RAGAS.")
            
        # 2. Bloque de Rendimiento (Solo Tiempo Total)
        print(f"\nMétricas de rendimiento con el {ds['name']}")
        total_time = get_total_time(model_json_path)
        print(f"Tiempo total de la prueba: {total_time} segundos.")
        
        # 3. Bloque Físico del Dataset
        print(f"\nDatos del {ds['name']}")
        print(f"{ds['description']}")
        num_imgs, size_mb = get_dataset_stats(ds['data_folder'])
        print(f"{num_imgs} imágenes.")
        print(f"{size_mb:.1f} MB\n")
        
        print("-" * 60 + "\n")

if __name__ == "__main__":
    generate_report()