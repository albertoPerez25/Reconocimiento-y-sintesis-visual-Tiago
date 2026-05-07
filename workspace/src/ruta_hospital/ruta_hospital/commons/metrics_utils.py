import json
import os

def save_metrics_to_file(metrics_dir, data_to_save, logger, file_name='comparativa_modelos.json'):
    '''Guarda un diccionario de métricas en un archivo JSON para comparativas'''
    metrics_file = os.path.join(metrics_dir, file_name)
    all_metrics = []

    if os.path.isfile(metrics_file):
        with open(metrics_file, 'r') as f:
            try:
                all_metrics = json.load(f)
            except json.JSONDecodeError:
                pass
    
    all_metrics.append(data_to_save)
    
    with open(metrics_file, 'w') as f:
        json.dump(all_metrics, f, indent=4)
        
    logger.info(f"Métricas guardadas en {metrics_file}")