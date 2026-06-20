#!/usr/bin/env python3
import os
import json
import argparse
import statistics
import datetime

DEFAULT_METRICS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/"

class PerceptionMetricsAggregator:
    '''Script externo para agregar y analizar estadísticamente los tiempos de los perceptores visuales.'''
    
    def __init__(self, metrics_dir):
        self.metrics_dir = metrics_dir

    def run(self):
        '''Orquesta la lectura de archivos, el procesamiento y el guardado.'''
        if not os.path.exists(self.metrics_dir):
            print(f"[ERROR] El directorio {self.metrics_dir} no existe.")
            return

        print(f"\n[INFO] Iniciando agregación de métricas en: {self.metrics_dir}")
        processed_count = 0

        for filename in os.listdir(self.metrics_dir):
            if filename.endswith("_metrics.json") and not filename.startswith("aggregated_"):
                filepath = os.path.join(self.metrics_dir, filename)
                self._process_file(filepath, filename)
                if os.path.exists(os.path.join(self.metrics_dir, f"aggregated_{filename}")):
                    processed_count += 1

        print(f"[INFO] Proceso completado. Se han generado {processed_count} reportes agregados.\n")

    def _process_file(self, filepath, filename):
        '''Abre el archivo JSON crudo, determina su tipo y genera el reporte agregado.'''
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Si el JSON es una lista (histórico de ROS), coge el último guardado
            if isinstance(data, list) and len(data) > 0:
                data = data[-1]

            if "tiempos_procesado" not in data or not data["tiempos_procesado"]:
                print(f"[WARN] Saltando {filename}: No tiene la clave 'tiempos_procesado' o está vacía.")
                return

            # Determinar si es un nodo estándar o el nodo híbrido
            is_hybrid = data.get("modelo_usado") == "hybrid_model"
            
            if is_hybrid:
                aggregated_data = self._build_hybrid_report(data)
            else:
                aggregated_data = self._build_standard_report(data)

            # Guardar el nuevo archivo
            output_filename = f"aggregated_{filename}"
            output_filepath = os.path.join(self.metrics_dir, output_filename)
            
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(aggregated_data, f, ensure_ascii=False, indent=4)
                
            print(f"[OK] Generado reporte agregado: {output_filename}")

        except Exception as e:
            print(f"[ERROR] Fallo al procesar el archivo {filename}: {e}")

    def _build_standard_report(self, data):
        '''Construye el reporte para perceptores individuales (YOLO, VLM, etc.)'''
        tiempos = data["tiempos_procesado"]
        
        report = {
            "fecha_agregacion": str(datetime.datetime.now()),
            "nodo_ejecutor": data.get("nodo_ejecutor", "Desconocido"),
            "modelo_usado": data.get("modelo_usado", "Desconocido"),
            "total_muestras": len(tiempos),
            "estadisticas_globales": self._calculate_statistics(tiempos)
        }
        return report

    def _build_hybrid_report(self, data):
        '''Construye el reporte desglosado para el orquestador híbrido'''
        tiempos = data["tiempos_procesado"]
        
        # Desempaquetar la lista de diccionarios en listas planas individuales
        yolo_times = [item["yolo_seconds"] for item in tiempos if "yolo_seconds" in item]
        vlm_times = [item["vlm_seconds"] for item in tiempos if "vlm_seconds" in item]
        total_times = [item["total_seconds"] for item in tiempos if "total_seconds" in item]

        # Calcular estadísticas por separado
        stats_yolo = self._calculate_statistics(yolo_times)
        stats_vlm = self._calculate_statistics(vlm_times)
        stats_total = self._calculate_statistics(total_times)

        # Calcular el porcentaje de cuello de botella (Cuánto tiempo acapara el VLM frente al total)
        if stats_total["media_segundos"] > 0:
            cuello_vlm = (stats_vlm["media_segundos"] / stats_total["media_segundos"]) * 100
        else:
            cuello_vlm = 0.0

        stats_total["cuello_de_botella_vlm_porcentaje"] = f"{round(cuello_vlm, 2)}%"

        report = {
            "fecha_agregacion": str(datetime.datetime.now()),
            "nodo_ejecutor": data.get("nodo_ejecutor", "Desconocido"),
            "modelo_usado": "Modelo Híbrido Acoplado",
            "modelos_acoplados": data.get("modelos_acoplados", {}),
            "total_muestras": len(tiempos),
            "estadisticas_yolo": stats_yolo,
            "estadisticas_vlm": stats_vlm,
            "estadisticas_totales": stats_total
        }
        return report

    def _calculate_statistics(self, times_list):
        '''Motor matemático puro para extraer las métricas de rendimiento'''
        if not times_list:
            return {}

        n = len(times_list)
        times_sorted = sorted(times_list)
        
        mean_val = statistics.mean(times_sorted)
        median_val = statistics.median(times_sorted)
        
        # Varianza y Desviación Típica requieren al menos 2 muestras
        variance_val = statistics.variance(times_sorted) if n > 1 else 0.0
        std_dev_val = statistics.stdev(times_sorted) if n > 1 else 0.0

        # Para la moda, redondeamos a 2 decimales para agrupar tiempos muy parecidos
        rounded_times = [round(t, 2) for t in times_sorted]
        try:
            mode_val = statistics.mode(rounded_times)
        except statistics.StatisticsError:
            mode_val = rounded_times[0] # Fallback si todos son únicos

        # Cálculo de percentiles (P90 y P99 garantizan la latencia máxima esperable)
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
            "fps_equivalente": round(fps, 2)
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script para agregar estadísticas de tiempos de percepción visual.")
    parser.add_argument(
        '--dir', 
        type=str, 
        default=DEFAULT_METRICS_DIR,
        help=f"Directorio donde se encuentran los archivos _metrics.json (Por defecto: {DEFAULT_METRICS_DIR})"
    )
    
    args = parser.parse_args()
    
    aggregator = PerceptionMetricsAggregator(metrics_dir=args.dir)
    aggregator.run()