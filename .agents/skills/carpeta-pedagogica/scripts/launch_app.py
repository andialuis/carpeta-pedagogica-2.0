#!/usr/bin/env python3
"""
launch_app.py - Inicia y verifica la suite Carpeta Pedagógica 2.0
Autor: Luis Alfredo Andia Valverde (luis.andia.valverde@gmail.com)
Licencia: Creative Commons BY-NC 4.0
"""
import sys
import os
import subprocess
import urllib.request
import json
import time
import webbrowser

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = r"C:\Users\RcRd.03\Desktop\Carpeta Pedagógica 2.0"

def is_service_running(url):
    try:
        res = urllib.request.urlopen(url, timeout=2)
        return res.getcode() == 200
    except Exception:
        return False

def main():
    print("=" * 60)
    print("  CARPETA PEDAGOGICA 2.0 - VERIFICADOR & LANZADOR")
    print("  Autor: Luis Alfredo Andia Valverde")
    print("=" * 60)

    backend_ok = is_service_running("http://127.0.0.1:8000/api/system/stats")
    frontend_ok = is_service_running("http://localhost:3001/")

    if backend_ok and frontend_ok:
        print("[OK] Ambos servicios ya se encuentran en ejecucion:")
        print("    - Backend:  http://127.0.0.1:8000")
        print("    - Frontend: http://localhost:3001")
    else:
        print("[!] Uno o mas servicios no estan activos. Iniciando suite...")
        bat_file = os.path.join(PROJECT_ROOT, "Iniciar_Carpeta.bat")
        if os.path.exists(bat_file):
            subprocess.Popen(["cmd.exe", "/c", bat_file], cwd=PROJECT_ROOT)
            print("[*] Script Iniciar_Carpeta.bat ejecutado. Esperando arranque...")
            time.sleep(6)
        else:
            print(f"[ERROR] No se encontro {bat_file}")
            sys.exit(1)

    # Verificar de nuevo
    retries = 5
    while retries > 0:
        backend_ok = is_service_running("http://127.0.0.1:8000/api/system/stats")
        frontend_ok = is_service_running("http://localhost:3001/")
        if backend_ok and frontend_ok:
            break
        time.sleep(2)
        retries -= 1

    if backend_ok and frontend_ok:
        # Obtener estadísticas
        try:
            res = urllib.request.urlopen("http://127.0.0.1:8000/api/system/stats")
            stats = json.loads(res.read().decode("utf-8"))
            print("\n[ESTADO DEL SISTEMA]")
            print(f"  * Autor:      {stats.get('autor')}")
            print(f"  * Version:    {stats.get('version')}")
            print(f"  * Materias:   {stats.get('total_materias')} activas")
            print(f"  * Motor IA:   {stats.get('gemini_modelo')}")
            print(f"  * Almacenaje: {stats.get('espacio_utilizado_mb')} MB")
        except Exception:
            pass

        print("\n[OK] Plataforma operativa en: http://localhost:3001")
        try:
            webbrowser.open("http://localhost:3001")
        except Exception:
            pass
    else:
        print("\n[ALERTA] Los servicios tardaron en responder. Verifica la consola de Windows.")

if __name__ == "__main__":
    main()
