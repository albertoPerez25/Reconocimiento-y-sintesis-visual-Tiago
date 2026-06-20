import subprocess
import logging
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Formato de los mensajes en la terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# CONSTANTES DE CONFIGURACIÓN 
DIAGRAMS_FOLDER = "docs/diagrams/s8/mermaid/" 
OUTPUT_FOLDER = "docs/diagrams/s8/"             
DEFAULT_FORMAT = "png"                    # Formatos soportados por mmdc: png, svg, pdf
CHROME_INSTALLATION = "/usr/bin/google-chrome-stable" # Como paquete es preferible a snap o flatpak
SCALE_FACTOR = 12                         # Escala configurable


class MermaidCLIConverter:
    """
    Clase para convertir diagramas Mermaid a imágenes utilizando Node.js 
    y la herramienta oficial @mermaid-js/mermaid-cli (mmdc)
    """
    def __init__(self, source_dir: str, output_dir: str, output_format: str, scale: int):
        self.source_dir = Path(source_dir)
        self.output_format = output_format.lower().strip('.')
        self.output_dir = Path(output_dir) / self.output_format
        self.scale = scale # Guardamos la escala en la instancia

    def convert_file(self, input_path: Path) -> bool:
        """Ejecuta el comando mmdc en el sistema para procesar el archivo"""
        
        output_filename = input_path.with_suffix(f".{self.output_format}").name
        output_path = self.output_dir / output_filename

        # Comando: mmdc -i archivo_entrada.mmd -o archivo_salida.png -s [escala]
        cmd = [
            "mmdc",
            "-p", "scripts/configs/puppeteer-config.json",
            "-i", str(input_path),
            "-o", str(output_path),
            "-s", str(self.scale)  # 9 menos calidad pero aceptable, 15 mucha calidad
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
        """Ejecuta el pipeline iterando sobre la carpeta origen con paralelismo dinámico"""
        if not self.source_dir.exists():
            logging.error(f"La carpeta origen '{self.source_dir}' no existe")
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        files = list(self.source_dir.glob("*.mmd"))

        if not files:
            logging.warning(f"No se encontraron archivos .mmd en '{self.source_dir}'")
            return

        cpu_count = os.cpu_count() or 2
        
        # Chrome sin cabeza consume mucha RAM. A mayor escala, menos hilos debemos usar.
        if self.scale >= 10:
            # Escala masiva: Restringimos a 1 o 2 Chrome a la vez para evitar colapso de RAM
            safe_workers = min(2, max(1, cpu_count // 4)) 
        elif self.scale >= 7:
            # Escala alta: Usamos un tercio de la CPU
            safe_workers = max(1, cpu_count // 3)
        elif self.scale >= 4:
            # Escala media: Usamos la mitad de la CPU
            safe_workers = max(1, cpu_count // 2)
        else:
            # Escala baja: Podemos usar casi toda la CPU
            safe_workers = max(1, cpu_count - 1)

        max_workers = min(len(files), safe_workers)

        logging.info(f"Encontrados {len(files)} archivos. Guardando en: {self.output_dir}")
        logging.info(f"Escala configurada: {self.scale}x")
        logging.info(f"Iniciando conversión usando {max_workers} hilos concurrentes...")

        success_count = 0
        
        # Ejecución paralela controlada (Cola automática)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Metemos todos los archivos al pool. Si hay más archivos que workers, 
            # se quedan esperando su turno inteligentemente sin crashear el PC.
            futures = {executor.submit(self.convert_file, file): file for file in files}
            
            for future in as_completed(futures):
                if future.result():
                    success_count += 1

        logging.info(f"Proceso finalizado. {success_count}/{len(files)} diagramas convertidos con éxito")

if __name__ == "__main__":
    converter = MermaidCLIConverter(
        source_dir=DIAGRAMS_FOLDER,
        output_dir=OUTPUT_FOLDER,
        output_format=DEFAULT_FORMAT,
        scale=SCALE_FACTOR
    )
    converter.run()