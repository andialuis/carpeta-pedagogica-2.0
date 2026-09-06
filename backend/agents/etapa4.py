"""
etapa4.py - Visualización y Preparación del Dashboard
Verifica la disponibilidad de insights.json y datasets para el dashboard interactivo.
"""
import os
import sys
import json

def run():
    print("Iniciando Etapa 4: Procesamiento de Visualización y Dashboard...")
    subject_name = sys.argv[1] if len(sys.argv) > 1 else "INV101 - Introduccion a la Investigacion"
    
    agents_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(agents_dir)
    root_dir = os.path.dirname(backend_dir)
    target_dir = os.path.join(root_dir, "uploads", f"{subject_name}-REV", "bases_de_datos")
    
    json_output = os.path.join(target_dir, "insights.json")
    
    if not os.path.exists(json_output):
        print(f"Advertencia: No se encontró {json_output}. Generando automáticamente con Etapa 3...")
        # Correr etapa 3 si no existe
        from etapa3 import run as run_e3
        run_e3()
        
    if os.path.exists(json_output):
        try:
            with open(json_output, 'r', encoding='utf-8') as f:
                data = json.load(f)
            total = len(data.get("estudiantes", []))
            prom = data.get("promedio_general", "N/A")
            print(f"Integridad de datos confirmada para '{subject_name}': {total} estudiantes, Promedio: {prom}")
            print("Tableros analíticos listos en el Dashboard (Next.js).")
            print("Etapa 4 completada con éxito.")
        except Exception as e:
            print(f"Error leyendo {json_output}: {e}")
    else:
        print(f"Error: No se pudo preparar la visualización para {subject_name}")
        sys.exit(1)

if __name__ == "__main__":
    run()
