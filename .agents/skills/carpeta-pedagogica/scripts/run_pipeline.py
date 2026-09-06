#!/usr/bin/env python3
"""
run_pipeline.py - Ejecuta el pipeline analítico de 4 etapas para una materia
Autor: Luis Alfredo Andia Valverde (luis.andia.valverde@gmail.com)
Licencia: Creative Commons BY-NC 4.0
"""
import sys
import os
import json
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

def run_stage(subject, stage_id):
    url = f"{BACKEND_URL}/api/stages/run/{urllib.parse.quote(subject)}/{stage_id}"
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Ejecutar Pipeline Analitico de Carpeta Pedagogica 2.0")
    parser.add_argument("subject", help="Nombre o codigo de la materia (ej: QUIM101, FIS301, INV101)")
    parser.add_argument("--stage", choices=["e1", "e2", "e3", "e4", "all"], default="all", help="Etapa a ejecutar o 'all'")
    args = parser.parse_args()

    subject = args.subject
    print("=" * 65)
    print(f"  PIPELINE DE ANALITICA DE APRENDIZAJE: {subject}")
    print("  Autor: Luis Alfredo Andia Valverde")
    print("=" * 65)

    stages = [
        ("e1", "Etapa 1: Ingesta, Limpieza y Consolidacion (BASE_INTEGRADA.xlsx)"),
        ("e2", "Etapa 2: Anonimizacion Criptografica Soberana (llave_nombres.json)"),
        ("e3", "Etapa 3: Inferencia Estadistica, ZDP Vygotsky & Deci-Ryan (insights.json)"),
        ("e4", "Etapa 4: Visualizaciones y Panel Interactivo")
    ]

    target_stages = stages if args.stage == "all" else [s for s in stages if s[0] == args.stage]

    for sid, desc in target_stages:
        print(f"\n[*] Ejecutando {desc}...")
        ok, res = run_stage(subject, sid)
        if ok:
            print(f"    [OK] {sid.upper()} completada con exito.")
            if sid == "e3" and isinstance(res, dict):
                insights = res.get("insights", {})
                if "necesidad_andamiaje_vygotsky" in insights:
                    print(f"    -> Diagnostico ZDP: {insights['necesidad_andamiaje_vygotsky']}")
        else:
            print(f"    [X] Error en {sid.upper()}: {res}")
            print("    Asegurate de que el backend este corriendo en http://127.0.0.1:8000")
            break

    print("\n[OK] Proceso finalizado.")

if __name__ == "__main__":
    main()
