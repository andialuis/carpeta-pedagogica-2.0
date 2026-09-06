#!/usr/bin/env python3
"""
export_dossier.py - Descarga el Dossier Oficial Consolidado (.docx)
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
    parser = argparse.ArgumentParser(description="Descargar Dossier Oficial Consolidado")
    parser.add_argument("subject", help="Nombre o codigo de la materia (ej: QUIM101, FIS301)")
    parser.add_argument("--output", help="Ruta de destino del archivo Word (.docx)")
    args = parser.parse_args()

    subject = args.subject
    default_out = f"DOSSIER_OFICIAL_{subject}.docx"
    out_file = args.output or default_out

    url = f"{BACKEND_URL}/api/documents/export-carpeta-completa/{urllib.parse.quote(subject)}"

    print("=" * 65)
    print(f"  COMPILADOR DE DOSSIER OFICIAL: {subject}")
    print("  Autor: Luis Alfredo Andia Valverde")
    print("=" * 65)

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            with open(out_file, "wb") as f:
                f.write(data)
            print(f"\n[OK] Dossier compilado con exito: {os.path.abspath(out_file)}")
            print(f"     Tamano: {len(data)} bytes")
            print("     Contiene: Caratula institucional, Diagnostico analitico, Plan Curricular, Matriz DUA y Protocolo Socratio.")
    except Exception as e:
        print(f"\n[ERROR] No se pudo descargar el Dossier: {e}")
        print("Asegurate de que el servidor este activo en http://127.0.0.1:8000")
        sys.exit(1)

if __name__ == "__main__":
    main()
