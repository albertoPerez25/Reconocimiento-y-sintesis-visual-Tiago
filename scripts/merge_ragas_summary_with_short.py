import pandas as pd
from pathlib import Path

def merge_ragas_metrics_by_structure(dir_viejo, dir_nuevo, dir_salida):
    # Convertir a objetos Path para un manejo arquitectónico limpio
    path_viejo = Path(dir_viejo)
    path_nuevo = Path(dir_nuevo)
    path_salida = Path(dir_salida)

    # Guardrail 1: Validar que los directorios base existen
    if not path_viejo.is_dir() or not path_nuevo.is_dir():
        print("Error: Los directorios de origen no existen. Verifica las rutas.")
        return

    # Buscar recursivamente todos los csv que empiecen por ragas_ en el directorio viejo
    archivos_viejos = list(path_viejo.rglob('ragas_*.csv'))
    
    if not archivos_viejos:
        print(f"No se encontraron archivos 'ragas_*.csv' en {path_viejo}")
        return

    for csv_viejo in archivos_viejos:
        # Extraer la ruta relativa (ej: 1_hybrid_vs_vlm/1_eval_hybrid/ragas_1_eval_hybrid_system_evaluation.csv)
        ruta_relativa = csv_viejo.relative_to(path_viejo)
        
        # Proyectar esa misma ruta en el directorio nuevo y de salida
        csv_nuevo = path_nuevo / ruta_relativa
        csv_salida = path_salida / ruta_relativa

        # Guardrail 2: Si aún no has ejecutado las pruebas para este directorio, lo saltamos limpiamente
        if not csv_nuevo.is_file():
            print(f"[-] Saltando (faltan pruebas nuevas): {ruta_relativa}")
            continue

        try:
            # Leer ambos DataFrames
            df_viejo = pd.read_csv(csv_viejo)
            df_nuevo = pd.read_csv(csv_nuevo)

            # Guardrail 3: Verificar que la columna de tipo exista (asumimos 'eval_type' por tu CSV)
            columna_tipo = 'eval_type'
            if columna_tipo not in df_viejo.columns or columna_tipo not in df_nuevo.columns:
                print(f"[!] Error en {ruta_relativa.name}: No se encuentra la columna '{columna_tipo}'.")
                continue

            # Identificar dinámicamente cuál es el tipo correspondiente a los resúmenes.
            # Como el CSV nuevo solo tiene resúmenes, cogemos el valor único de esa columna.
            tipos_en_nuevo = df_nuevo[columna_tipo].unique()
            
            if len(tipos_en_nuevo) == 0:
                print(f"[!] Archivo nuevo vacío: {ruta_relativa.name}")
                continue
                
            # Asumimos que todos los registros del nuevo son del mismo tipo (ej. 'resumen' o 'summary')
            tipo_resumen = tipos_en_nuevo[0] 

            # Filtrar el viejo: nos quedamos estrictamente con las filas que NO sean de tipo resumen
            df_cortas = df_viejo[df_viejo[columna_tipo] != tipo_resumen]

            # Concatenar las preguntas cortas (viejas) con los resúmenes (nuevos)
            df_merged = pd.concat([df_cortas, df_nuevo], ignore_index=True)

            # Crear los subdirectorios en la carpeta de salida si no existen
            csv_salida.parent.mkdir(parents=True, exist_ok=True)

            # Guardar el resultado
            df_merged.to_csv(csv_salida, index=False)
            
            print(f"[+] Fusionado con éxito: {ruta_relativa.parent.name} -> {csv_salida.name}")
            print(f"    Cortas mantenidas: {len(df_cortas)} | Resúmenes insertados: {len(df_nuevo)} | Total: {len(df_merged)}")

        except Exception as e:
            # Guardrail 4: Evitar que un error de codificación en un archivo detenga todo el batch
            print(f"[!] Error crítico procesando {ruta_relativa}: {e}")

# --- Configuración de rutas ---
# Ajusta estas rutas a tu estructura local
DIRECTORIO_VIEJO = "viejo_todas"
DIRECTORIO_NUEVO = "nuevo_resumen"
DIRECTORIO_SALIDA = "fusionado_completo"

# Ejecutar
print(f"Iniciando proceso de fusión. Salida en: {DIRECTORIO_SALIDA}\n" + "-"*50)
merge_ragas_metrics_by_structure(DIRECTORIO_VIEJO, DIRECTORIO_NUEVO, DIRECTORIO_SALIDA)
