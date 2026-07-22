import json
import os
import pandas as pd

def load_ragas_csv(filepath):
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath)

def load_merged_performance_data(eval_dir):
    merged_data = {}
    if not os.path.exists(eval_dir):
        return merged_data
        
    files_in_dir = [f for f in os.listdir(eval_dir) if f.startswith("comparativa_") and f.endswith(".json")]
    files_in_dir.sort(key=lambda x: "evaluadores" in x) # Prioridad al evaluador
    
    for filename in files_in_dir:
        filepath = os.path.join(eval_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_to_merge = data[0] if isinstance(data, list) and len(data) > 0 else data if isinstance(data, dict) else {}
                    
                for k, v in data_to_merge.items():
                    if k not in merged_data:
                        merged_data[k] = v
                    else:
                        if v not in [0, 0.0, "", None]:
                            merged_data[k] = v
                        elif merged_data[k] in [0, 0.0, "", None] and v in [0, 0.0]:
                            merged_data[k] = v
        except Exception as e:
            print(f"[EXTRACTOR] Error al leer {filepath}: {e}")
            
    return merged_data

def get_dataset_size_mb(folder_path):
    if not os.path.exists(folder_path):
        return 0.0
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, f))
        for dirpath, _, filenames in os.walk(folder_path)
        for f in filenames if not os.path.islink(os.path.join(dirpath, f))
    )
    return round(total_size / (1024 * 1024), 2)

def load_raw_perception_times(filepath):
    """Carga los datos crudos. Si el archivo no existe, lanza un error."""
    if not os.path.exists(filepath):
        #  ERROR: Devolver [] ocultaba que el archivo no existía
        raise FileNotFoundError(f"[ERROR CRÍTICO] No se encuentra el archivo de métricas: {filepath}")
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Retornamos los datos. Si el JSON estuviera mal formado, el error será evidente.
            return data
    except Exception as e:
        print(f"[EXTRACTOR] Error al leer el archivo JSON: {e}")
        raise