import os
import shutil

def delete_folder(path, logger):
    '''Borra una carpeta'''
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            # logger.info(f"Carpeta eliminada: {path}")
    except Exception as e:
        logger.error(f"Fallo al eliminar carpeta {path}: {e}")