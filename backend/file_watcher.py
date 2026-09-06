import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ai_service import analyze_spreadsheet_structure

UPLOAD_DIR = "uploads"

class FileUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            filepath = event.src_path
            filename = os.path.basename(filepath)
            if filename.endswith(".xlsx") or filename.endswith(".csv"):
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Nuevo archivo detectado: {filename}")
                print("Iniciando análisis de IA para inferir esquema...")
                
                # Simular tiempo de carga si el archivo está siendo copiado
                time.sleep(2) 
                
                # Lanzar el pipeline
                result = analyze_spreadsheet_structure(filepath)
                
                # Aquí normalmente enviaríamos un evento por WebSocket al frontend
                # para avisarle al usuario que el archivo está listo para revisión (Human-in-the-loop)
                print(f"Análisis completado para {filename}. Esperando autorización humana.")
                print(f"Resultado IA: {result}")

def start_watcher():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    event_handler = FileUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_DIR, recursive=False)
    observer.start()
    print(f"Observador de archivos iniciado en el directorio: {UPLOAD_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
