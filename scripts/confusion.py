import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import f1_score, precision_score, recall_score
import os

# Crear carpeta para guardar las imágenes si no existe
os.makedirs("./matrices_confusion", exist_ok=True)

# Configuración basada en evaluación por zonas
# Total Zonas con Alertas Reales = 2
# Total Zonas Normales (Negativas) = 13 (Ajustar si tu simulación tiene otro número de estancias sin incidentes)
TOTAL_NEGATIVES = 20

experimentos = {
    # EXPERIMENTO 1
    'Exp1_VLM_Aislado': {'TP': 1, 'FN': 1, 'FP': 0}, 
    'Exp1_Hibrido':     {'TP': 2, 'FN': 0, 'FP': 1}, 

    # EXPERIMENTO 2 (Representativos para la figura comparativa)
    'Exp2_Distancia_4m': {'TP': 0, 'FN': 2, 'FP': 0}, # Omite todo
    'Exp2_MSE_005':      {'TP': 1, 'FN': 1, 'FP': 0}, # Omite caída, retiene fumar, depura FPs

    # EXPERIMENTO 3
    'Exp3_Video': {'TP': 2, 'FN': 0, 'FP': 3}, # Detecta ambas, 3 zonas con falsos positivos
}

def plot_confusion_matrix(tp, fn, fp, tn, name, title):
    matrix = np.array([[tn, fp], [fn, tp]])
    plt.figure(figsize=(5, 4))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Normal', 'Alerta'],
                yticklabels=['Normal', 'Alerta'],
                annot_kws={"size": 16})
    plt.title(title, pad=15)
    plt.ylabel('Realidad (Ground Truth)')
    plt.xlabel('Predicción del Sistema')
    plt.tight_layout()
    plt.savefig(f'matrices_confusion/{name}.png', dpi=300)
    plt.close()

print("="*40)
print("RESULTADOS DE MÉTRICAS DE ALERTAS")
print("="*40)

for name, data in experimentos.items():
    tp = data['TP']
    fn = data['FN']
    fp = data['FP']
    tn = TOTAL_NEGATIVES - fp
    
    # Reconstrucción de arrays para cálculo exacto
    y_true = [1]*(tp+fn) + [0]*(fp+tn)
    y_pred = [1]*tp + [0]*fn + [1]*fp + [0]*tn
    
    f1 = f1_score(y_true, y_pred, zero_division=0)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    
    print(f"\n[{name}]")
    print(f"TP: {tp} | FN: {fn} | FP: {fp} | TN: {tn}")
    print(f"Precision: {precision:.2f} | Recall: {recall:.2f} | F1-Score: {f1:.2f}")
    
    title = name.replace('_', ' ')
    plot_confusion_matrix(tp, fn, fp, tn, name, title)

print("\nImágenes generadas en la carpeta 'matrices_confusion'.")
