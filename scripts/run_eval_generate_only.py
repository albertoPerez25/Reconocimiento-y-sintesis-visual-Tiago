#!/usr/bin/env python3
import subprocess
import time
import os
import shutil
from datetime import datetime

# ================= CONFIGURACIÓN DE RUTAS LOCALES =================
WORKSPACE_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace/"
CONFIG_FILE = f"{WORKSPACE_DIR}src/ruta_hospital/config/reporter_config.yaml"

# Directorios de Métricas y Archivos Temporales
METRICS_BASE_DIR = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/docs/autogenerate_metrics/"
TMP_ARCHIVE_BASE_DIR = "/home/alberto/tfg/Datos_tmp/eval/"

# Archivos vivos en /tmp
TMP_RAG_DATA = "/tmp/ruta_hospital_rag_data"
TMP_RAGAS_ANSWERS = "/tmp/ragas_intermediate_answers.json"

# Ruta del resguardo en el Escritorio
DESKTOP_STATUS_FILE = os.path.expanduser("~/Escritorio/estado_pruebas_generate.txt")

# Comando base adaptado para GENERATE_ONLY y RESUME_SESSION
BASE_EVAL_CMD = f"ros2 run ruta_hospital system_evaluator_node --ros-args --params-file {CONFIG_FILE} -p use_reranker:=true -p evaluation_mode:=\"generate_only\" -p resume_session:=true"
ACTION_CMD = 'ros2 action send_goal /evaluate_patrol_system hospital_interfaces/action/GenerateReport "{folder_path: \'\'}"'

# ================= MATRIZ DE PRUEBAS =================
TESTS = [
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_estandar_1_0m",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_estandar_1_0m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_grande",
        "eval_cmd": None,
        "skip_and_copy_from": {
            "category": "1_hybrid_vs_vlm",
            "name": "1_eval_hybrid"
        }
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_reduccion_0_5m",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_reduccion_0_5m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_reduccion_2_0m",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_reduccion_2_0m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "2_size_datasets",
        "name": "2_eval_dataset_reduccion_4_0m",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"2_eval_dataset_reduccion_4_0m\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    
]

def update_desktop_status(completed_list, current_test, pending_list):
    try:
        os.makedirs(os.path.dirname(DESKTOP_STATUS_FILE), exist_ok=True)
        with open(DESKTOP_STATUS_FILE, "w", encoding="utf-8") as f:
            f.write("==================================================================\n")
            f.write(f" ESTADO DE GENERACIÓN LLM ONLY - (ACTUALIZADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write("==================================================================\n\n")
            
            f.write("▶️ EN EJECUCIÓN ACTUALMENTE:\n")
            if current_test:
                f.write(f"  * Nombre:    {current_test['name']}\n")
            else:
                f.write("  None (Batería finalizada)\n\n")
            
            f.write("✅ COMPLETADAS:\n")
            for tc in completed_list:
                f.write(f"  - {tc['name']}\n")
            
            f.write("\n⏳ PENDIENTES:\n")
            for tp in pending_list:
                f.write(f"  - {tp['name']}\n")
            f.write("\n==================================================================\n")
    except Exception as e:
        pass

def spawn_terminal(title, command):
    full_cmd = f"cd {WORKSPACE_DIR} && source install/setup.bash && {command}; exec bash"
    gnome_cmd = ["gnome-terminal", "--title", title, "--", "bash", "-c", full_cmd]
    subprocess.Popen(gnome_cmd)

def kill_ros_nodes():
    nodes = ["system_evaluator_node", "hybrid_perception_node", "vlm_perception_node", "yolo_perception_node"]
    for n in nodes:
        os.system(f"pkill -f {n} > /dev/null 2>&1")

def restore_faiss_context(test):
    """Copia la BD FAISS archivada a /tmp para que el evaluador la encuentre y evite inferencia."""
    print("   [FAISS] Restaurando contexto FAISS desde histórico...")
    
    # 1. Limpiar el /tmp actual
    if os.path.exists(TMP_RAG_DATA):
        shutil.rmtree(TMP_RAG_DATA)
    if os.path.exists(TMP_RAGAS_ANSWERS):
        os.remove(TMP_RAGAS_ANSWERS)

    # 2. Copiar desde el archivo
    archived_rag_data = os.path.join(TMP_ARCHIVE_BASE_DIR, test["category"], test["name"], "ruta_hospital_rag_data")
    if not os.path.exists(archived_rag_data):
        raise FileNotFoundError(f"¡FATAL! No se encontró el FAISS archivado en: {archived_rag_data}")
        
    shutil.copytree(archived_rag_data, TMP_RAG_DATA)
    print("   [FAISS] Contexto restaurado con éxito en /tmp.")

def archive_results(test):
    """Solo mueve el archivo de respuestas JSON, dejando intacto el FAISS original del archivo."""
    target_tmp_dir = os.path.join(TMP_ARCHIVE_BASE_DIR, test["category"], test["name"])
    os.makedirs(target_tmp_dir, exist_ok=True)

    print(f"   [ARCHIVAR] Guardando respuestas generadas en {target_tmp_dir}...")
    if os.path.exists(TMP_RAGAS_ANSWERS):
        shutil.move(TMP_RAGAS_ANSWERS, os.path.join(target_tmp_dir, "ragas_intermediate_answers.json"))

def execute_smart_cloning(test):
    """Solo clona el archivo JSON generado, ya que el FAISS ya existe."""
    src_info = test["skip_and_copy_from"]
    print(f"   [CLONACIÓN INTELIGENTE] Copiando respuestas de {src_info['name']}...")
    
    src_json = os.path.join(TMP_ARCHIVE_BASE_DIR, src_info["category"], src_info["name"], "ragas_intermediate_answers.json")
    dest_json = os.path.join(TMP_ARCHIVE_BASE_DIR, test["category"], test["name"], "ragas_intermediate_answers.json")
    
    if os.path.exists(src_json):
        shutil.copy2(src_json, dest_json)
        print("   [CLONACIÓN INTELIGENTE] JSON copiado con éxito.")
    else:
        print("   [ERROR] No se pudo clonar porque el JSON origen no existe.")

def run_pipeline():
    completed_tests = []

    while len(completed_tests) < len(TESTS):
        current_idx = len(completed_tests)
        current_test = TESTS[current_idx]
        pending_tests = TESTS[current_idx + 1:]
        
        update_desktop_status(completed_tests, current_test, pending_tests)
        
        print(f"\n{'='*80}")
        print(f"🎬 GENERANDO RESPUESTAS: {current_test['category']} -> {current_test['name']}")
        print(f"{'='*80}")
        
        if current_test["skip_and_copy_from"] is not None:
            execute_smart_cloning(current_test)
            completed_tests.append(current_test)
            time.sleep(1)
            continue

        try:
            restore_faiss_context(current_test)
        except Exception as e:
            print(f"❌ SALTANDO PRUEBA: {e}")
            completed_tests.append(current_test)
            continue

        print("[ROS2] Desplegando nodo de Evaluación de Sistema (Modo LLM Only)...")
        spawn_terminal(f"System Evaluator: {current_test['name']}", current_test["eval_cmd"])
        time.sleep(5)

        print("[ROS2] Enviando Goal de acción de manera síncrona. Procesando...")
        action_full_cmd = f"cd {WORKSPACE_DIR} && source install/setup.bash && {ACTION_CMD}"
        subprocess.run(action_full_cmd, shell=True, executable='/bin/bash')

        print(f"\n[ROS2] Goal completado para {current_test['name']}. Matando procesos secundarios...")
        kill_ros_nodes()
        time.sleep(2)

        print("[SISTEMA] Extrayendo y archivando respuestas JSON...")
        archive_results(current_test)

        print(f"🎉 GENERACIÓN PARA {current_test['name']} CONCLUIDA CON ÉXITO.")
        completed_tests.append(current_test)
        time.sleep(5)

    update_desktop_status(completed_tests, None, [])
    print("\n🏁 ¡BATERÍA DE GENERACIÓN COMPLETADA! Sube las carpetas a Google Colab.")

if __name__ == "__main__":
    try:
        kill_ros_nodes()
        run_pipeline()
    except KeyboardInterrupt:
        print("\n[WARN] Automatización cancelada por el usuario. Limpiando nodos...")
        kill_ros_nodes()




'''
    {
        "category": "1_hybrid_vs_vlm",
        "name": "1_eval_hybrid",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"1_eval_hybrid\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "1_hybrid_vs_vlm",
        "name": "1_eval_vlm",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"1_eval_vlm\" -p perception_mode:=\"image\"",
        "skip_and_copy_from": None
    },
    {
        "category": "3_imagen_vs_video",
        "name": "3_eval_vlm_static",
        "eval_cmd": None,
        "skip_and_copy_from": {
            "category": "2_size_datasets",
            "name": "2_eval_dataset_estandar_1_0m" 
        }
    },
    {
        "category": "3_imagen_vs_video",
        "name": "3_eval_video",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"3_eval_video\" -p perception_mode:=\"video\"",
        "skip_and_copy_from": None
    },
    {
        "category": "4_reporter_models",
        "name": "4_eval_hybrid_qwen",
        "eval_cmd": f"{BASE_EVAL_CMD} -p evaluation_name:=\"4_eval_hybrid_qwen\" -p perception_mode:=\"image\" -p evaluator_llm_model:=\"qwen3.5:4b\"",
        "skip_and_copy_from": None
    }'''