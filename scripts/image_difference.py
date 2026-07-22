import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
IMG_DIFF_DIR = os.path.join(PROJECT_ROOT, "docs", "diagrams", "s9", "mermaid", "memoria", "image_difference")

# --- 1. CONFIGURACIÓN ---
# Rutas de ejemplo (cámbialas por dos fotos consecutivas de tu dataset del hospital)
PATH_IMG_1 = os.path.join(IMG_DIFF_DIR, "antes.png")
PATH_IMG_2 = os.path.join(IMG_DIFF_DIR, "despues.png")
THRESHOLD = 1 # Porcentaje de diferencia mínimo requerido (0-100)

def calculate_mse_percentage(img1, img2):
    """Calcula el MSE normalizado como porcentaje (0-100%)"""
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 1. Calcular el MSE absoluto
    err = np.sum((gray2.astype("float") - gray1.astype("float")) ** 2)
    err /= float(gray2.shape[0] * gray2.shape[1])
    
    # 2. Normalizar a porcentaje (MSE max = 255^2 = 65025)
    mse_percentage = (err / 65025.0) * 100.0
    
    return mse_percentage, gray1, gray2

def generate_comparison_figure(img1_path, img2_path):
    # Cargar imágenes
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        print("Error: No se pudieron cargar las imágenes. Verifica las rutas.")
        return

    # Redimensionar img2 al tamaño de img1 por seguridad
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # --- 2. LÓGICA DE SIMILITUD (Actualizada) ---
    mse_percentage, gray1, gray2 = calculate_mse_percentage(img1, img2)
    is_different = mse_percentage > THRESHOLD
    
    estado_texto = "GUARDADA" if is_different else "DESCARTADA"
    color_texto = "green" if is_different else "red"

    # --- 3. GENERAR MAPA DE DIFERENCIAS ---
    diff = cv2.absdiff(gray1, gray2)
    
    # --- 4. CREAR LA FIGURA PARA MATPLOTLIB ---
    img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Filtro de Redundancia de Imágenes (OpenCV)', fontsize=16, fontweight='bold')

    axes[0].imshow(img1_rgb)
    axes[0].set_title('Última Imagen Guardada')
    axes[0].axis('off')

    axes[1].imshow(img2_rgb)
    axes[1].set_title('Captura Actual')
    axes[1].axis('off')

    im = axes[2].imshow(diff, cmap='hot', interpolation='nearest')
    axes[2].set_title('Mapa de Diferencias (AbsDiff)')
    axes[2].axis('off')

    # Añadir texto con el resultado del MSE normalizado a porcentaje
    resultado_str = f"Diferencia: {mse_percentage:.2f}% / Umbral: {THRESHOLD}%\nAcción: {estado_texto}"
    fig.text(0.5, 0.05, resultado_str, ha='center', fontsize=14, 
             bbox=dict(facecolor='white', edgecolor=color_texto, boxstyle='round,pad=0.5'))

    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    output_filename = 'opencv_diff_comparison.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Imagen generada con éxito: {output_filename}")
    
    plt.show()

if __name__ == '__main__':
    generate_comparison_figure(PATH_IMG_1, PATH_IMG_2)