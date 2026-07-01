#!/usr/bin/env python3
import os
import csv
import math
import shutil

# ==============================================================================
# CONFIGURACIÓN DE EXPERIMENTOS (Fácilmente modificable)
# ==============================================================================
# Distancia base asumida del dataset original
BASE_RESOLUTION_METERS = 0.2  

# Umbral para diferenciar avance lineal de rotación pura (en metros)
LINEAR_THRESHOLD_METERS = 0.15  

# Lista de distancias objetivo para generar los subconjuntos degradados
TARGET_DISTANCES = [0.5, 1.0, 2.0, 4.0]  

# Rutas de entrada y salida del dataset
SOURCE_DATASET_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/datasets/hospital_photos/vuelta_A"
OUTPUT_BASE_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/datasets/hospital_photos"

CSV_FILENAME = "metadata.csv"

# ==============================================================================
# FUNCIONES AUXILIARES (LÓGICA MATEMÁTICA Y DE FILTRADO)
# ==============================================================================

def calculate_distance(p1, p2):
    """Calcula la distancia euclídea 2D entre dos puntos (x, y)."""
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)


def load_metadata(csv_path):
    """Lee el CSV original y parsea los tipos de datos necesarios."""
    rows = []
    with open(csv_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'filename': row['filename'],
                'timestamp_sec': int(row['timestamp_sec']),
                'timestamp_nanosec': int(row['timestamp_nanosec']),
                'x': float(row['x']),
                'y': float(row['y']),
                'z': float(row['z']),
                'qx': float(row['qx']),
                'qy': float(row['qy']),
                'qz': float(row['qz']),
                'qw': float(row['qw']),
                '_original_row': row  # Guardamos la fila intacta para la exportación exacta
            })
    return rows


def filter_dataset_by_odometry(metadata_rows, target_distance):
    """
    Aplica el algoritmo de aproximación por odometría real.
    Mantiene intactas las capturas angulares y realiza un submuestreo por distancia 
    acumulada sobre las capturas lineales.
    """
    filtered_rows = []
    
    if not metadata_rows:
        return filtered_rows

    # La primera captura siempre se procesa e incluye para inicializar el estado
    last_processed_linear_pose = metadata_rows[0]
    filtered_rows.append(metadata_rows[0])
    
    accumulated_distance = 0.0

    for i in range(1, len(metadata_rows)):
        current_row = metadata_rows[i]
        previous_row = metadata_rows[i-1]
        
        # Distancia instantánea con respecto al frame inmediatamente anterior
        instant_dist = calculate_distance(current_row, previous_row)
        
        if instant_dist < LINEAR_THRESHOLD_METERS:
            # Caso A: El robot está girando sobre su eje (rotación angular pura) o detenido
            # Preservamos la captura para no perder la panorámica de la zona/habitación
            filtered_rows.append(current_row)
        else:
            # Caso B: El robot está avanzando en línea recta
            # Acumulamos la distancia recorrida desde la última pose lineal consolidada
            dist_from_last_linear = calculate_distance(current_row, last_processed_linear_pose)
            accumulated_distance = dist_from_last_linear
            
            if accumulated_distance >= target_distance:
                filtered_rows.append(current_row)
                last_processed_linear_pose = current_row
                accumulated_distance = 0.0
                
    return filtered_rows

# ==============================================================================
# PIPELINE DE EJECUCIÓN (PROCESAMIENTO EN DISCO)
# ==============================================================================

def main():
    source_csv = os.path.join(SOURCE_DATASET_DIR, CSV_FILENAME)
    if not os.path.exists(source_csv):
        print(f"[ERROR] No se encuentra el archivo de metadatos de origen en: {source_csv}")
        return

    print(f"[INFO] Cargando metadatos base desde: {source_csv}")
    base_metadata = load_metadata(source_csv)
    print(f"[INFO] Dataset original cargado con {len(base_metadata)} capturas.")

    # Iterar sobre cada uno de los experimentos métricos configurados
    for target_dist in TARGET_DISTANCES:
        folder_name = f"vuelta_A_{str(target_dist).replace('.', '_')}m"
        target_dir = os.path.join(OUTPUT_BASE_DIR, folder_name)
        
        print(f"\n=======================================================")
        print(f"[PROCESO] Generando experimento para intervalo: {target_dist}m")
        print(f"[PROCESO] Directorio destino: {target_dir}")
        print(f"=======================================================")
        
        # Crear la infraestructura de directorios limpia (Clean Slate)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        # Filtrar las filas aplicando el algoritmo odométrico
        selected_rows = filter_dataset_by_odometry(base_metadata, target_dist)
        print(f"[FILTRADO] Reducido de {len(base_metadata)} a {len(selected_rows)} imágenes.")
        
        # Exportar archivos físicos (imágenes) y reconstruir el archivo CSV
        target_csv_path = os.path.join(target_dir, CSV_FILENAME)
        
        with open(target_csv_path, mode='w', newline='', encoding='utf-8') as out_f:
            # Reutilizar exactamente los mismos headers que genera el nodo de ROS 2
            headers = list(base_metadata[0]['_original_row'].keys())
            writer = csv.DictWriter(out_f, fieldnames=headers)
            writer.writeheader()
            
            for row in selected_rows:
                img_name = row['filename']
                src_img_path = os.path.join(SOURCE_DATASET_DIR, img_name)
                dst_img_path = os.path.join(target_dir, img_name)
                
                # Copiar archivo físico de imagen sin alterar el original
                if os.path.exists(src_img_path):
                    shutil.copy2(src_img_path, dst_img_path)
                else:
                    print(f"[ADVERTENCIA] Archivo de imagen faltante en origen: {src_img_path}")
                
                # Escribir fila en el nuevo CSV de metadatos indexados
                writer.writerow(row['_original_row'])
                
        print(f"[ÉXITO] Experimento finalizado y guardado en: {target_dir}")

if __name__ == "__main__":
    main()