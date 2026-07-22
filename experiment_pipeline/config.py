import os
import seaborn as sns

# =========================================================
# CONFIGURACIÓN ESTÉTICA (UCLM - Académica)
# =========================================================
def set_academic_style():
    sns.set_theme(style="ticks", context="paper")
    sns.set_palette("colorblind") # Seguro para impresión b/n y daltonismo

Y_LIM_METRICS = (0, 100)
CHARS_PER_TOKEN = 4

METRICS_MAPPING = {
    "answer_correctness": "Ans. Correctness",
    "answer_relevancy": "Ans. Relevancy",
    "faithfulness": "Faithfulness",
    "context_precision": "Context Precision",
    "context_recall": "Context Recall",
    "answer_similarity": "Ans. Similarity",
    "rouge_score_recall_es": "ROUGE-1",
    "hhem_fidelity_balanced": "HHEM",
    "bert_score_es": "BERTScore"
}

# =========================================================
# MAPA DE DIRECTORIOS DE LOS EXPERIMENTOS
# =========================================================
# Resolución dinámica de la raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))

BASE_DIR = os.path.join(project_root, "docs", "autogenerate_metrics")
DATASETS_DIR = os.path.join(project_root, "datasets", "datasets")

# EXPERIMENTO 1: Híbrido vs VLM
EXP1_CONFIG = [
    {
        "label": "VLM (Aislado)",
        "eval_dir": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_vlm"),
        "csv_path": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_vlm/ragas_1_eval_vlm_system_evaluation.csv"),
        "perception_json_path": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_vlm/vlm_perception_node_metrics.json")
    },
    {
        "label": "Percepción Híbrida",
        "eval_dir": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid"),
        "csv_path": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid/ragas_1_eval_hybrid_system_evaluation.csv"),
        "perception_json_path": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid/hybrid_perception_node_metrics.json")
    }
]

# EXPERIMENTO 2A: Reducción por Distancia
EXP2_DIST_CONFIG = [
    {
        "label": "Base (Sin filtro)",
        "eval_dir": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid"), 
        "csv_path": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid/ragas_1_eval_hybrid_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "grande")
    },
    {
        "label": "Reducción 0.5m",
        "eval_dir": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_reduccion_0_5m"),
        "csv_path": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_reduccion_0_5m/ragas_2_eval_dataset_reduccion_0_5m_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "reduccion_0_5m")
    },
    {
        "label": "Reducción 1.0m",
        "eval_dir": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_estandar_1_0m"),
        "csv_path": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_estandar_1_0m/ragas_2_eval_dataset_estandar_1_0m_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "reduccion_1_0m")
    },
    {
        "label": "Reducción 2.0m",
        "eval_dir": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_reduccion_2_0m"),
        "csv_path": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_reduccion_2_0m/ragas_2_eval_dataset_reduccion_2_0m_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "reduccion_2_0m")
    },
    {
        "label": "Reducción 4.0m",
        "eval_dir": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_reduccion_4_0m"),
        "csv_path": os.path.join(BASE_DIR, "2_size_datasets/2_eval_dataset_reduccion_4_0m/ragas_2_eval_dataset_reduccion_4_0m_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "reduccion_4_0m")
    }
]

# EXPERIMENTO 2B: Reducción por MSE
EXP2_MSE_CONFIG = [
    {
        "label": "Base (Sin filtro)",
        "eval_dir": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid"),
        "csv_path": os.path.join(BASE_DIR, "1_hybrid_vs_vlm/1_eval_hybrid/ragas_1_eval_hybrid_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "grande")
    },
    {
        "label": "MSE 0.005",
        "eval_dir": os.path.join(BASE_DIR, "5_mse_datasets/5_eval_dataset_mse_00_5"),
        "csv_path": os.path.join(BASE_DIR, "5_mse_datasets/5_eval_dataset_mse_00_5/ragas_5_eval_dataset_mse_00_5_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "mse_00_5")
    },
    {
        "label": "MSE 0.01",
        "eval_dir": os.path.join(BASE_DIR, "5_mse_datasets/5_eval_dataset_mse_01"),
        "csv_path": os.path.join(BASE_DIR, "5_mse_datasets/5_eval_dataset_mse_01/ragas_5_eval_dataset_mse_01_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "mse_01")
    },
    {
        "label": "MSE 0.05",
        "eval_dir": os.path.join(BASE_DIR, "5_mse_datasets/5_eval_dataset_mse_05"),
        "csv_path": os.path.join(BASE_DIR, "5_mse_datasets/5_eval_dataset_mse_05/ragas_5_eval_dataset_mse_05_system_evaluation.csv"),
        "dataset_path": os.path.join(DATASETS_DIR, "mse_05")
    }
]

# EXPERIMENTO 3: Vídeo vs Estático
EXP3_CONFIG = [
    {
        "label": "VLM Estático (Base)",
        "eval_dir": os.path.join(BASE_DIR, "3_imagen_vs_video/3_eval_vlm_static"),
        "csv_path": os.path.join(BASE_DIR, "3_imagen_vs_video/3_eval_vlm_static/ragas_3_eval_vlm_static_system_evaluation.csv"),
        "perception_json_path": os.path.join(BASE_DIR, "3_imagen_vs_video/3_eval_vlm_static/hybrid_perception_node_metrics.json")
    },
    {
        "label": "VLM Vídeo",
        "eval_dir": os.path.join(BASE_DIR, "3_imagen_vs_video/3_eval_video"),
        "csv_path": os.path.join(BASE_DIR, "3_imagen_vs_video/3_eval_video/ragas_3_eval_video_system_evaluation.csv"),
        "perception_json_path": os.path.join(BASE_DIR, "3_imagen_vs_video/3_eval_video/hybrid_perception_node_metrics.json")
    }
]
