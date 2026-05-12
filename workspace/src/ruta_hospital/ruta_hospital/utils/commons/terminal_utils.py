import sys
import select
import tty
import termios

def get_key_non_blocking():
    '''Lee una tecla sin pulsar Enter asíncronamente'''
    try:
        file_descriptor_stdin = sys.stdin.fileno()
        # En caso de un crasheo, guardar para restaurar después
        old_settings = termios.tcgetattr(file_descriptor_stdin) 
        try:
            # El modo cbreak no necesita pulsar enter
            tty.setcbreak(file_descriptor_stdin) 
            # Input en cada instante, asíncrono
            if select.select([sys.stdin], [], [], 0.2)[0]: 
                return sys.stdin.read(1)
        finally:
            # Restaura terminal a su estado original
            termios.tcsetattr(file_descriptor_stdin, termios.TCSADRAIN, old_settings) 
    except Exception:
        pass # Falla silenciosamente si la terminal no soporta lectura cruda
    return None