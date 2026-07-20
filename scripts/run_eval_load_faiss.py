#!/usr/bin/env python3
import subprocess
import time
import os
import shutil
from datetime import datetime

# ================= CONFIGURACIÓN DE RUTAS LOCALES =================
WORKSPACE_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/"
CONFIG_FILE = f"{WORKSPACE_DIR}src/ruta_hospital/config/reporter_config.yaml"

# Directorios de Datasets
BASE_DATASET_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/datasets/datasets/"
ACTIVE_PHOTOS_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/datasets/hospital_photos/vuelta_A"

# Directorios de Métricas y Archivos Temporales
METRICS_BASE_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/"
TMP_ARCHIVE_BASE_DIR = "/home/alberto/tfg/Datos_tmp/eval/"

# Archivos vivos en /tmp
TMP_RAG_DATA = "/tmp/ruta_hospital_rag_data"
TMP_RAGAS_ANSWERS = "/tmp/ragas_intermediate_answers.json"

# Ruta del resguardo en el Escritorio
DESKTOP_STATUS_FILE = os.path.expanduser("~/Escritorio/estado_pruebas.txt")

# Comando base común para el evaluador:
# Se fuerza resume_session:=true para que, al encontrar FAISS, salte la inferencia.
# Se fuerza evaluation_mode:="full" para generar repuestas + evaluar.
BASE_EVAL_CMD = f"ros2 run ruta_hospital system_evaluator_node --ros-args --params-file {CONFIG_FILE} -p use_reranker:=true -p evaluation_mode:=\"full\" -p resume_session:=true"
ACTION_CMD = 'ros2 action send_goal /evaluate_patrol_system hospital_interfaces/action/GenerateReport "{folder_path: \'\'}"'

# ================= MATRIZ DE PRUEBAS OPTIMIZADA =================
TESTS = [
    # ----------- PRUEBA 1: Híbrido VS Solo VLM (Dataset Grande) -----------
    {
        "category": "1_hybrid_vs_vlm",
        "name": "1_eval_hybrid",
        "dataset": "grande",
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"1_eval_hybrid\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "1_hybrid_vs_vlm",
        "name": "1_eval_vlm",
        "dataset": "grande",
        "perception_cmd": "ros2 run ruta_hospital vlm_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"1_eval_vlm\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },

    # ----------- PRUEBA 2: Tamaños de Dataset (Reducciones VS Grande) -----------
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_estandar_1_0m",
        "dataset": "reduccion_1_0m", # <-- EL NUEVO ESTÁNDAR
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_estandar_1_0m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_grande",
        "dataset": "grande",
        "perception_cmd": None,
        "eval_cmd": None,
        "skip_and_copy_from": {
            "category": "1_hybrid_vs_vlm",
            "name": "1_eval_hybrid" # <-- CLONADO PARA AHORRAR HORAS
        }
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_reduccion_0_5m",
        "dataset": "reduccion_0_5m",
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_reduccion_0_5m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_reduccion_2_0m",
        "dataset": "reduccion_2_0m",
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_reduccion_2_0m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_reduccion_4_0m",
        "dataset": "reduccion_4_0m",
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_reduccion_4_0m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },

    # ----------- PRUEBA 3: Estático (VLM) VS Vídeo (Nuevo Estándar) -----------
    {
        "category": "3_imagen_vs_video",
        "name": "3_eval_vlm_static",
        "dataset": "reduccion_1_0m", # <-- ACTUALIZADO AL NUEVO ESTÁNDAR
        "perception_cmd": None,
        "eval_cmd": None,
        "skip_and_copy_from": {
            "category": "2_size_datasets",
            "name": "2_eval_dataset_estandar_1_0m" # <-- CLONADO DE LA PRUEBA 2 PARA AHORRAR TIEMPO
        }
    },
    {
        "category": "3_imagen_vs_video",
        "name": "3_eval_video",
        "dataset": "video", # <-- CORREGIDO AL DATASET "video" normal
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node --ros-args -p vlm_estimators:=\"['ruta_hospital.perception.video_perception_node.VideoPerceptionNode']\"",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"3_eval_video\" -p perception_mode:=\"video\"",
        "skip_and_copy_from": None
    },

    # ----------- PRUEBA 4: Híbrido Normal (Imagen) con Reportero Qwen3.5:4b -----------
    {
        "category": "4_reporter_models",
        "name": "4_eval_hybrid_qwen",
        "dataset": "reduccion_1_0m", # <-- USANDO EL NUEVO ESTÁNDAR
        "perception_cmd": "ros2 run ruta_hospital hybrid_perception_node",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"4_eval_hybrid_qwen\" -p perception_mode:=\"image\" -p llm_model:=\"qwen3.5:4b\"",
        "skip_and_copy_from": None
    }
]

def update_desktop_status(completed_list, current_test, pending_list):
    """Genera y actualiza dinámicamente un archivo de texto en el Escritorio con el progreso vivo."""
    try:
        os.makedirs(os.path.dirname(DESKTOP_STATUS_FILE), exist_ok=True)
        with open(DESKTOP_STATUS_FILE, "w", encoding="utf-8") as f:
            f.write("==================================================================\n")
            f.write(f" ESTADO DE LA BATERÍA DE PRUEBAS - (ACTUALIZADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write("==================================================================\n\n")
            
            f.write("▶️ EN EJECUCIÓN ACTUALMENTE:\n")
            f.write("------------------------------------------------------------------\n")
            if current_test:
                f.write(f"  * Nombre:    {current_test['name']}\n")
                f.write(f"  * Categoría: {current_test['category']}\n")
                if current_test['skip_and_copy_from']:
                    f.write(f"  * Tipo:      Clonación inteligente (Optimización sin ejecución)\n")
                else:
                    f.write(f"  * Dataset:   {current_test['dataset']}\n")
            else:
                f.write("  None (Batería de pruebas finalizada con éxito)\n")
            f.write("\n\n")
            
            f.write("✅ PRUEBAS YA TERMINADAS:\n")
            f.write("------------------------------------------------------------------\n")
            if completed_list:
                for tc in completed_list:
                    tipo = " [COPIADA]" if tc['skip_and_copy_from'] else " [COMPLETADA]"
                    f.write(f"  - {tc['category']} -> {tc['name']}{tipo}\n")
            else:
                f.write("  (Ninguna prueba completada todavía)\n")
            f.write("\n\n")
            
            f.write("⏳ PRUEBAS PENDIENTES POR EJECUTAR:\n")
            f.write("------------------------------------------------------------------\n")
            if pending_list:
                for tp in pending_list:
                    f.write(f"  - {tp['category']} -> {tp['name']}\n")
            else:
                f.write("  (Cola vacía. Todas las pruebas han concluido)\n")
            f.write("\n==================================================================\n")
    except Exception as e:
        print(f"[ERROR MÉTODOS CONTROL] No se pudo escribir el archivo en el Escritorio: {e}")

def spawn_terminal(title, command):
    """Abre una nueva ventana de terminal física para supervisión en vivo."""
    full_cmd = f"cd {WORKSPACE_DIR} && source install/setup.bash && {command}; exec bash"
    gnome_cmd = ["gnome-terminal", "--title", title, "--", "bash", "-c", full_cmd]
    subprocess.Popen(gnome_cmd)

def kill_ros_nodes():
    """Limpia la memoria del sistema operativo de cualquier nodo ROS colgado."""
    nodes = ["system_evaluator_node", "hybrid_perception_node", "vlm_perception_node", 
             "video_perception_node", "yolo_perception_node", "sequence_perception_node"]
    for n in nodes:
        os.system(f"pkill -f {n} > /dev/null 2>&1")

def prepare_dataset(current_dataset, last_dataset):
    """Intercambia el dataset activo en hospital_photos solo si es estrictamente necesario."""
    if current_dataset == last_dataset:
        print(f"   [DATASET] Reutilizando dataset activo: {current_dataset}")
        return
    
    print(f"   [DATASET] Cambiando dataset activo de '{last_dataset}' a '{current_dataset}'...")
    if os.path.exists(ACTIVE_PHOTOS_DIR):
        shutil.rmtree(ACTIVE_PHOTOS_DIR)
        
    src_folder = os.path.join(BASE_DATASET_DIR, current_dataset, "vuelta_A")
    shutil.copytree(src_folder, ACTIVE_PHOTOS_DIR)
    print("   [DATASET] Dataset clonado correctamente en hospital_photos/vuelta_A")

def clean_and_restore_faiss(test):
    """Limpia /tmp y restaura la FAISS guardada anteriormente para saltarse la inferencia."""
    print("   [FAISS] Limpiando entorno temporal /tmp...")
    if os.path.exists(TMP_RAG_DATA):
        shutil.rmtree(TMP_RAG_DATA)
    if os.path.exists(TMP_RAGAS_ANSWERS):
        os.remove(TMP_RAGAS_ANSWERS)
        
    archive_rag_data = os.path.join(TMP_ARCHIVE_BASE_DIR, test["category"], test["name"], "ruta_hospital_rag_data")
    if os.path.exists(archive_rag_data):
        print(f"   [FAISS] Restaurando índice FAISS previo desde archivo para acelerar la prueba...")
        shutil.copytree(archive_rag_data, TMP_RAG_DATA)
    else:
        print(f"   [FAISS] ⚠️ ADVERTENCIA: No se encontró índice FAISS en {archive_rag_data}. Se ejecutará inferencia desde cero.")

def archive_results(test):
    """Mueve métricas y gestiona el archivado sobreescribiendo si ya existían datos."""
    target_metrics_dir = os.path.join(METRICS_BASE_DIR, test["category"], test["name"])
    os.makedirs(target_metrics_dir, exist_ok=True)
    
    for f in os.listdir(METRICS_BASE_DIR):
        src_path = os.path.join(METRICS_BASE_DIR, f)
        if os.path.isfile(src_path):
            dest_path = os.path.join(target_metrics_dir, f)
            if os.path.exists(dest_path):
                os.remove(dest_path) # Sobrescribir archivo CSV viejo
            shutil.move(src_path, dest_path)

    target_tmp_dir = os.path.join(TMP_ARCHIVE_BASE_DIR, test["category"], test["name"])
    os.makedirs(target_tmp_dir, exist_ok=True)

    print(f"   [ARCHIVAR] Guardando índice RAG y JSON de respuestas (sobreescribiendo si existe)...")
    dest_rag_data = os.path.join(target_tmp_dir, "ruta_hospital_rag_data")
    if os.path.exists(TMP_RAG_DATA):
        if os.path.exists(dest_rag_data):
            shutil.rmtree(dest_rag_data) # Sobrescribir base de datos FAISS vieja
        shutil.move(TMP_RAG_DATA, dest_rag_data)
        
    if os.path.exists(TMP_RAGAS_ANSWERS):
        dest_answers = os.path.join(target_tmp_dir, "ragas_intermediate_answers.json")
        if os.path.exists(dest_answers):
            os.remove(dest_answers) # Sobrescribir JSON de repuestas viejo
        shutil.move(TMP_RAGAS_ANSWERS, dest_answers)

def execute_smart_cloning(test):
    """Clona y renombra inteligentemente los resultados, garantizando sobrescritura segura."""
    src_info = test["skip_and_copy_from"]
    print(f"   [CLONACIÓN INTELIGENTE] Copiando resultados históricos de {src_info['name']}...")
    
    src_metrics_dir = os.path.join(METRICS_BASE_DIR, src_info["category"], src_info["name"])
    src_tmp_archive = os.path.join(TMP_ARCHIVE_BASE_DIR, src_info["category"], src_info["name"])
    
    dest_metrics_dir = os.path.join(METRICS_BASE_DIR, test["category"], test["name"])
    dest_tmp_archive = os.path.join(TMP_ARCHIVE_BASE_DIR, test["category"], test["name"])
    
    os.makedirs(dest_metrics_dir, exist_ok=True)
    os.makedirs(dest_tmp_archive, exist_ok=True)
    
    if os.path.exists(src_metrics_dir):
        for item in os.listdir(src_metrics_dir):
            src_file = os.path.join(src_metrics_dir, item)
            if os.path.isfile(src_file):
                dest_item_name = item.replace(src_info["name"], test["name"])
                dest_file = os.path.join(dest_metrics_dir, dest_item_name)
                
                # Protección contra binarios y sobrescritura segura
                if src_file.endswith(('.json', '.csv', '.txt')):
                    with open(src_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = content.replace(src_info["name"], test["name"])
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    if os.path.exists(dest_file):
                        os.remove(dest_file)
                    shutil.copy2(src_file, dest_file)
                
    if os.path.exists(src_tmp_archive):
        # Si la FAISS del clon ya existe, la borramos para evitar conflictos de copytree
        if os.path.exists(dest_tmp_archive):
            shutil.rmtree(dest_tmp_archive)
        shutil.copytree(src_tmp_archive, dest_tmp_archive)
        
    print(f"   [CLONACIÓN INTELIGENTE] Hecho. Resultados replicados con éxito.")

def run_pipeline():
    last_dataset = None
    completed_tests = []

    while len(completed_tests) < len(TESTS):
        current_idx = len(completed_tests)
        current_test = TESTS[current_idx]
        pending_tests = TESTS[current_idx + 1:]
        
        update_desktop_status(completed_tests, current_test, pending_tests)
        
        print(f"\n{'='*80}")
        print(f"🎬 INICIANDO EXPERIMENTO: {current_test['category']} -> {current_test['name']}")
        print(f"{'='*80}")
        
        if current_test["skip_and_copy_from"] is not None:
            execute_smart_cloning(current_test)
            completed_tests.append(current_test)
            time.sleep(1)
            continue

        prepare_dataset(current_test["dataset"], last_dataset)
        clean_and_restore_faiss(current_test)

        print("[ROS2] Desplegando nodo de Percepción...")
        spawn_terminal(f"Perception Node: {current_test['name']}", current_test["perception_cmd"])
        time.sleep(4)

        print("[ROS2] Desplegando nodo de Evaluación de Sistema...")
        spawn_terminal(f"System Evaluator: {current_test['name']}", current_test["eval_cmd"])
        time.sleep(5)

        print("[ROS2] Enviando Goal de acción de manera síncrona. Procesando...")
        action_full_cmd = f"cd {WORKSPACE_DIR} && source install/setup.bash && {ACTION_CMD}"
        subprocess.run(action_full_cmd, shell=True, executable='/bin/bash')

        print(f"\n[ROS2] Goal completado para {current_test['name']}. Matando procesos secundarios...")
        kill_ros_nodes()
        time.sleep(2)

        print("[SISTEMA] Clasificando reportes y aplicando políticas de archivado...")
        archive_results(current_test)

        last_dataset = current_test["dataset"]
        
        print(f"🎉 EXPERIMENTO {current_test['name']} CONCLUIDO CON ÉXITO.")
        completed_tests.append(current_test)
        time.sleep(5)

    update_desktop_status(completed_tests, None, [])
    print("\n🏁 ¡BATERÍA DE EVALUACIÓN COMPLETADA CON ÉXITO! Comprueba tu Escritorio y Datos_tmp.")

if __name__ == "__main__":
    try:
        kill_ros_nodes()
        run_pipeline()
    except KeyboardInterrupt:
        print("\n[WARN] Automatización cancelada por el usuario. Limpiando nodos...")
        kill_ros_nodes()