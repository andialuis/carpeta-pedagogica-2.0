import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AutoReactHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        print(f"[WATCHDOG] Detectado nuevo archivo: {file_path}")
        
        # Ignorar archivos temporales
        if "~$" in file_path or ".tmp" in file_path:
            return
            
        # Si se suelta un archivo crudo en la raíz de una materia, lanzar Etapa 1
        # Ejemplo: uploads/QUIM101 - Química Analítica/PARTICIPACION EN AULA.jpg
        # Si es un JPG o XLSX en la base, disparamos
        
        if file_path.endswith((".jpg", ".png", ".xlsx", ".csv")):
            print(f"[WATCHDOG] Disparando Agente E1 (Auto-react)...")
            try:
                # Usar requests para llamar a nuestro propio backend
                response = requests.post("http://localhost:8000/api/agents/run/e1")
                print(f"[WATCHDOG] Respuesta: {response.json()}")
            except Exception as e:
                print(f"[WATCHDOG] Error al disparar el agente: {e}")

def start_watcher():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    event_handler = AutoReactHandler()
    observer = Observer()
    observer.schedule(event_handler, base_dir, recursive=True)
    observer.start()
    print(f"👀 Auto-react activado vigilando: {base_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
