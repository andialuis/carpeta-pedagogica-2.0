#!/usr/bin/env python3
"""
export_lms.py - Exporta retroalimentación formativa y adaptaciones DUA para LMS
Soporta: Moodle (CSV UTF-8 BOM), Google Classroom (CSV), Microsoft Teams (.xlsx)
Autor: Luis Alfredo Andia Valverde (luis.andia.valverde@gmail.com)
Licencia: Creative Commons BY-NC 4.0
"""
import sys
import os
import urllib.request
import urllib.parse
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BACKEND_URL = "http://127.0.0.1:8000"

def main():
    parser = argparse.ArgumentParser(description="Exportar Feedback DUA para Moodle, Classroom o Teams")
    parser.add_argument("subject", help="Nombre o codigo de la materia (ej: QUIM101, FIS301)")
    parser.add_argument("--lms", choices=["moodle", "classroom", "teams"], default="moodle", help="Plataforma de destino")
    parser.add_argument("--output", help="Ruta de destino del archivo descargado")
    args = parser.parse_args()

    subject = args.subject
    lms = args.lms
    ext = ".xlsx" if lms == "teams" else ".csv"
    default_out = f"FEEDBACK_{lms.upper()}_{subject}{ext}"
    out_file = args.output or default_out

    url = f"{BACKEND_URL}/api/lms/export-feedback/{urllib.parse.quote(subject)}?target_lms={lms}"

    print("=" * 65)
    print(f"  EXPORTADOR DE RETROALIMENTACION LMS: {lms.upper()}")
    print(f"  Materia: {subject}")
    print("  Autor: Luis Alfredo Andia Valverde")
    print("=" * 65)

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(out_file, "wb") as f:
                f.write(data)
            print(f"\n[OK] Archivo generado con exito: {os.path.abspath(out_file)}")
            print(f"     Tamano: {len(data)} bytes")

            print("\n[INSTRUCCIONES DE IMPORTACION EN TU LMS]")
            if lms == "moodle":
                print("  1. Entra a tu curso en Moodle.")
                print("  2. Ve a Calificaciones > Pestana 'Importar' > 'Archivo CSV'.")
                print("  3. Sube este archivo.")
                print("  4. Mapea 'Numero de ID' con el ID del estudiante y 'Comentarios de retroalimentacion'.")
                print("  5. Haz clic en 'Subir calificaciones'. Listo!")
            elif lms == "classroom":
                print("  1. Abre tu clase en Google Classroom.")
                print("  2. Abre la tarea de evaluacion correspondiente.")
                print("  3. Usa este archivo CSV estructurado para sincronizar las devoluciones por correo.")
            elif lms == "teams":
                print("  1. Entra al equipo de clase en Microsoft Teams.")
                print("  2. Ve a la pestana 'Notas' (Grades).")
                print("  3. Sincroniza o copia las columnas de notas y comentarios adaptados desde este Excel.")

    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar al backend: {e}")
        print("Asegurate de que el servidor este activo en http://127.0.0.1:8000")
        sys.exit(1)

if __name__ == "__main__":
    main()
