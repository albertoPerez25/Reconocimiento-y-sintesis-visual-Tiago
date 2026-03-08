#!/usr/bin/env python3
# ARCHIVO GENERADO CON GEMINI 3.1 PRO

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo para gráficos más profesionales
sns.set_theme(style="whitegrid", palette="pastel")

# Rutas
JSON_PATH = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/comparativa_modelos.json"
OUTPUT_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/"

def cargar_datos():
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: No se encontró el archivo JSON en {JSON_PATH}")
        return None
    
    with open(JSON_PATH, 'r') as f:
        datos = json.load(f)
    
    df = pd.DataFrame(datos)
    
    # Crear métricas derivadas útiles
    if 'total_imagenes_procesadas' in df.columns and 'tiempo_percepcion_segundos' in df.columns:
        # Evitar división por cero
        df['segundos_por_imagen'] = df.apply(
            lambda row: row['tiempo_percepcion_segundos'] / row['total_imagenes_procesadas'] 
            if row['total_imagenes_procesadas'] > 0 else 0, axis=1
        )
        
    return df

def generar_tabla_resumen(df):
    print("\n" + "="*60)
    print(" 📊 RESUMEN DE MÉTRICAS POR MODELO (Valores Medios)")
    print("="*60)
    
    # Agrupamos por modelo y calculamos la media de cada columna numérica
    resumen = df.groupby('modelo_reportero').mean(numeric_only=True).round(2)
    
    # Seleccionamos y renombramos las columnas que nos importan para imprimir
    columnas_mostrar = {
        'tiempo_total_segundos': 'Tiempo Total (s)',
        'segundos_por_imagen': 'Latencia Visión (s/img)',
        'caracteres_contexto_visual': 'Contexto Generado (Caract.)',
        'tiempo_llm_segundos': 'Tiempo Redacción LLM (s)'
    }
    
    tabla_imprimir = resumen[list(columnas_mostrar.keys())].rename(columns=columnas_mostrar)
    print(tabla_imprimir.to_string())
    print("="*60 + "\n")
    
    # Guardar también en CSV para poder meterlo en Excel o Word fácilmente
    tabla_imprimir.to_csv(os.path.join(OUTPUT_DIR, "tabla_resumen.csv"))

def generar_graficos(df):
    # Crear carpeta de salida si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Gráfico de Tiempos Acumulados (Percepción vs Redacción)
    plt.figure(figsize=(10, 6))
    resumen = df.groupby('modelo_reportero')[['tiempo_percepcion_segundos', 'tiempo_llm_segundos']].mean()
    resumen.plot(kind='bar', stacked=True, color=['#4C72B0', '#55A868'], figsize=(10, 6))
    plt.title("Tiempo Medio de Procesamiento por Patrulla", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos", fontsize=12)
    plt.legend(["Percepción (Visión)", "Razonamiento (LLM)"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "1_desglose_tiempos.png"), dpi=300)
    plt.close()

    # 2. Gráfico de Latencia Visual (Segundos por Imagen)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='modelo_reportero', y='segundos_por_imagen', ci='sd', capsize=.1)
    plt.title("Latencia del Modelo Visual", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Segundos por Imagen procesada", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "2_latencia_visual.png"), dpi=300)
    plt.close()

    # 3. Gráfico de Verbosidad (Tamaño del contexto vs Tamaño del Informe)
    plt.figure(figsize=(10, 6))
    resumen_chars = df.groupby('modelo_reportero')[['caracteres_contexto_visual', 'caracteres_informe_final']].mean()
    resumen_chars.plot(kind='bar', width=0.7, color=['#C44E52', '#8172B3'], figsize=(10, 6))
    plt.title("Análisis de Verbosidad (Texto procesado)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Cantidad de Caracteres", fontsize=12)
    plt.legend(["Contexto Visual Generado", "Informe Final (Llama-3)"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "3_analisis_verbosidad.png"), dpi=300)
    plt.close()

    # 4. Boxplot para ver la estabilidad/variabilidad del tiempo total
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='modelo_reportero', y='tiempo_total_segundos', palette="Set2")
    # Añadimos los puntos reales encima para ver la distribución exacta
    sns.stripplot(data=df, x='modelo_reportero', y='tiempo_total_segundos', color=".3", size=6, alpha=0.6)
    plt.title("Estabilidad del Tiempo de Ejecución (Boxplot)", fontsize=14, pad=15)
    plt.xlabel("Modelo Utilizado", fontsize=12)
    plt.ylabel("Tiempo Total (Segundos)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "4_estabilidad_tiempos.png"), dpi=300)
    plt.close()

    print(f"✅ ¡Se han generado 4 gráficos de alta calidad en la carpeta: {OUTPUT_DIR}!")

if __name__ == "__main__":
    df_metricas = cargar_datos()
    if df_metricas is not None and not df_metricas.empty:
        generar_tabla_resumen(df_metricas)
        generar_graficos(df_metricas)
    else:
        print("⚠️ No hay datos suficientes en el JSON para generar gráficos.")
