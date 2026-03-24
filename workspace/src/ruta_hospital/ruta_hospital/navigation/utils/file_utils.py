import os
import shutil

def clean_all_orphan_folders(base_photos_dir, logger):
    '''Borra todas las subcarpetas que empiezan por "vuelta_"'''
    if not os.path.exists(base_photos_dir):
        return
    for item in os.listdir(base_photos_dir):
        if item.startswith("vuelta_"):
            path_to_remove = os.path.join(base_photos_dir, item)
            shutil.rmtree(path_to_remove)
            logger.info(f"Borrada subcarpeta {item}")

def get_next_available_folder(base_photos_dir, logger):
    '''Busca la primera letra disponible (A-Z) y crea la carpeta'''
    if not os.path.exists(base_photos_dir):
        os.makedirs(base_photos_dir)
        
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        folder_name = f"vuelta_{char}"
        folder_path = os.path.join(base_photos_dir, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return folder_path
            
    logger.error("Búffer de carpetas lleno")
    return None