import subprocess
import logging
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Formato de los mensajes en la terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# CONSTANTES DE CONFIGURACIÓN 
DIAGRAMS_FOLDER = "diagrams/s6/mermaid/" 
OUTPUT_FOLDER = "diagrams/s6"             
DEFAULT_FORMAT = "png"                    # Formatos soportados por mmdc: png, svg, pdf
CHROME_INSTALLATION = "/usr/bin/google-chrome-stable" # Como paquete es preferible a snap o flatpak


class MermaidCLIConverter:
    """
    Clase para convertir diagramas Mermaid a imágenes utilizando Node.js 
    y la herramienta oficial @mermaid-js/mermaid-cli (mmdc)
    """
    def __init__(self, source_dir: str, output_dir: str, output_format: str):
        self.source_dir = Path(source_dir)
        self.output_format = output_format.lower().strip('.')
        self.output_dir = Path(output_dir) / self.output_format

    def convert_file(self, input_path: Path) -> bool:
        """Ejecuta el comando mmdc en el sistema para procesar el archivo"""
        
        output_filename = input_path.with_suffix(f".{self.output_format}").name
        output_path = self.output_dir / output_filename

        # Comando: mmdc -i archivo_entrada.mmd -o archivo_salida.png -s 15
        cmd = [
            "mmdc",
            "-p", "scripts/configs/puppeteer-config.json",
            "-i", str(input_path),
            "-o", str(output_path),
            "-s", "9"  
        ]

        # Inyectamos la ruta del Chrome oficial
        env = os.environ.copy()
        env["PUPPETEER_EXECUTABLE_PATH"] = CHROME_INSTALLATION


        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
            logging.info(f"Convertido: {input_path.name} -> {output_filename}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error en {input_path.name}:\n{e.stderr}")
            return False
        except FileNotFoundError:
            logging.error("No se encuentra el comando 'mmdc'. ¿Se encuentra instalado Node.js y @mermaid-js/mermaid-cli ?")
            return False
        except Exception as e:
            logging.error(f"Error inesperado procesando {input_path.name}: {str(e)}")
            return False

    def run(self):
        """Ejecuta el pipeline iterando sobre la carpeta origen en paralelo"""
        if not self.source_dir.exists():
            logging.error(f"La carpeta origen '{self.source_dir}' no existe")
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        files = list(self.source_dir.glob("*.mmd"))

        if not files:
            logging.warning(f"No se encontraron archivos .mmd en '{self.source_dir}'")
            return

        # Total de CPUs menos 1 y mínimo 1
        cpu_count = os.cpu_count() or 2
        max_workers = min(len(files), max(1, cpu_count - 1))

        logging.info(f"Encontrados {len(files)} archivos. Guardando en: {self.output_dir}")
        logging.info(f"Iniciando conversión usando {max_workers} hilos...")

        success_count = 0
        
        # Ejecución paralela
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Archivos al pool de hilos
            futures = {executor.submit(self.convert_file, file): file for file in files}
            
            # Resultados conforme van terminando (sin importar el orden)
            for future in as_completed(futures):
                if future.result():
                    success_count += 1

        logging.info(f"Proceso finalizado. {success_count}/{len(files)} diagramas convertidos con éxito")

if __name__ == "__main__":
    converter = MermaidCLIConverter(
        source_dir=DIAGRAMS_FOLDER,
        output_dir=OUTPUT_FOLDER,
        output_format=DEFAULT_FORMAT
    )
    converter.run()
