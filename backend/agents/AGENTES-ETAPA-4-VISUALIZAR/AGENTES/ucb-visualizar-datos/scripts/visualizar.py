"""Etapa 4 — VISUALIZAR: punto de entrada unico.

Convierte el RESULTADOS_ANALISIS.xlsx de la Etapa 3 en un tablero de tres pestañas
que se abre con doble clic, sin internet y sin servidor.

    python3 visualizar.py "NOMBRE_CARPETA" --raiz "." --plan
    python3 visualizar.py "NOMBRE_CARPETA" --raiz "." --destacar "..."

Con --plan no construye nada: muestra las cuatro tablas que el docente aprueba en la
segunda pausa y no escribe un solo archivo.

Ni la metrica que se pide destacar, ni rutas, ni cifras quedan escritas en el codigo
(R6): todo entra por la linea de ordenes en cada ejecucion.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paso_construir_tab_general
import paso_construir_tab_hipotesis
import paso_construir_tab_intervencion
import paso_leer_resultados
import paso_verificar_tablero
import plantilla
from paso_leer_resultados import clasificar_veredicto, entero, plural

VERSION_MINIMA = (3, 8)


def comprobar_entorno():
    if sys.version_info < VERSION_MINIMA:
        print(f"Se necesita Python {'.'.join(map(str, VERSION_MINIMA))} o superior.")
        sys.exit(1)
    try:
        import openpyxl
    except ImportError:
        print("Falta la unica libreria obligatoria. Instalala con:")
        print(f"  {Path(sys.executable).name} -m pip install openpyxl")
        sys.exit(1)
    print("\nENTORNO")
    print("-" * 40)
    print(f"  Python           : {'.'.join(map(str, sys.version_info[:3]))}")
    print(f"  openpyxl         : {openpyxl.__version__}")
    print("  graficos         : SVG propio, sin librerias externas")


# ------------------------------------------------------------------- el plan
def construir_plan(datos, config, metrica):
    hip = datos.get("HIPOTESIS", [])
    conteo = {"confirmada": 0, "descartada": 0, "sin_comprobar": 0}
    for f in hip:
        conteo[clasificar_veredicto(f.get("veredicto"), config)] += 1

    inventario = [
        {"hoja": "HALLAZGOS", "trae": len(datos.get("HALLAZGOS", []))},
        {"hoja": "HIPOTESIS", "trae": len(hip)},
        {"hoja": "PERFILES", "trae": len(datos.get("PERFILES", []))},
        {"hoja": "INDICADORES", "trae": len(datos.get("INDICADORES", []))},
        {"hoja": "ACCIONES", "trae": len(datos.get("ACCIONES", []))},
        {"hoja": "PRIORIDADES", "trae": len(datos.get("PRIORIDADES", []))},
    ]
    pestanas = [
        {"pestana": "1 · Vision general",
         "contenido": "cifras de cabecera, reparto en grupos, nube de estudiantes "
                      "y tabla de prioridades"},
        {"pestana": "2 · Hipotesis y hallazgos",
         "contenido": f"marcador ({conteo['confirmada']} confirmadas / "
                      f"{conteo['descartada']} descartadas / "
                      f"{conteo['sin_comprobar']} sin comprobar) y una tarjeta "
                      f"por hipotesis y por hallazgo"},
        {"pestana": "3 · Plan de intervencion",
         "contenido": f"{plural(len(datos.get('ACCIONES', [])), 'tarjeta')} de "
                      f"accion y la tabla de señales de alerta"},
    ]
    no_se_puede = []
    for hoja, para_que in (("PERFILES", "el reparto del curso en grupos"),
                           ("INDICADORES", "la tabla de señales de alerta"),
                           ("DATOS_GRAFICOS", "la nube donde cada punto es un estudiante")):
        if not datos.get(hoja):
            no_se_puede.append({"no_se_podra_mostrar": para_que,
                                "por_que": f"el analisis no dejo la hoja {hoja}"})
    for fila in datos.get("NO_SE_PUDO", []):
        no_se_puede.append({"no_se_podra_mostrar": str(fila.get("analisis", "")),
                            "por_que": str(fila.get("por_que", ""))[:110]})
    return {"inventario": inventario, "pestanas": pestanas,
            "metrica": metrica, "no_se_puede": no_se_puede}


def imprimir_plan(plan):
    def tabla(titulo, registros, campos, anchos):
        print(f"\n{titulo}")
        print("-" * len(titulo))
        if not registros:
            print("  (nada que mostrar en este apartado)")
            return
        print("  " + "".join(c[:a - 1].ljust(a) for c, a in zip(campos, anchos)))
        print("  " + "-" * (sum(anchos) - 1))
        for r in registros:
            print("  " + "".join(str(r.get(c, ""))[:a - 1].ljust(a)
                                 for c, a in zip(campos, anchos)))

    tabla("A · QUE TRAE EL ANALISIS", plan["inventario"], ["hoja", "trae"], [22, 8])
    tabla("B · QUE VA A CONTENER CADA PESTAÑA", plan["pestanas"],
          ["pestana", "contenido"], [28, 74])
    print("\nC · LA CIFRA DEL LUGAR DESTACADO")
    print("-" * 32)
    print(f"  {plan['metrica'] or 'no se pidio destacar ninguna: ira el numero de hallazgos'}")
    tabla("D · LO QUE NO SE VA A PODER MOSTRAR", plan["no_se_puede"],
          ["no_se_podra_mostrar", "por_que"], [46, 56])
    print("\n" + "=" * 78)
    print(" Si apruebas esto, ejecuta de nuevo sin --plan.")
    print("=" * 78)


# ---------------------------------------------------------------- ejecucion
def ejecutar(carpeta, raiz, ruta_config, nombre_archivo, metrica, solo_plan):
    config = json.loads(Path(ruta_config).read_text(encoding="utf-8"))
    entrada, rev = paso_leer_resultados.localizar(carpeta, raiz, nombre_archivo)
    if entrada is None:
        print(f"\nNo se encontro {nombre_archivo}*.xlsx en {rev / 'bases_de_datos'}.")
        print("Esta etapa necesita el resultado de la Etapa 3. Ejecutala primero.")
        sys.exit(1)

    print(f"\nCONSTRUYENDO EL TABLERO DE: {entrada.name}")
    print(f"Carpeta de trabajo: {rev.name}")

    datos = paso_leer_resultados.leer(entrada, config)
    problemas = paso_leer_resultados.comprobar(datos, config)
    if problemas:
        print("\nNo se puede construir el tablero:")
        for p in problemas:
            print(f"  · {p}")
        print("\nVuelve a ejecutar la Etapa 3 antes de continuar.")
        sys.exit(1)
    if datos["faltantes"]:
        print(f"  AVISO: el analisis no trae {', '.join(datos['faltantes'])}; "
              "esas partes del tablero se omiten y se dice en pantalla.")
    print(f"1. Resultados leidos: {len(config['hojas_esperadas'])} hoja(s) esperadas, "
          f"{len(datos['faltantes'])} ausente(s).")

    plan = construir_plan(datos, config, metrica)
    if solo_plan:
        imprimir_plan(plan)
        return {"plan": plan}

    html1, bloques1, resumen1 = paso_construir_tab_general.construir(
        datos, config, metrica)
    print(f"2. Pestaña 1 armada: {resumen1['detalle']}.")
    html2, bloques2, resumen2 = paso_construir_tab_hipotesis.construir(datos, config)
    print(f"3. Pestaña 2 armada: {resumen2['detalle']}.")
    html3, bloques3, resumen3 = paso_construir_tab_intervencion.construir(datos, config)
    print(f"4. Pestaña 3 armada: {resumen3['detalle']}.")

    por_pestana = {"general": bloques1, "hipotesis": bloques2, "intervencion": bloques3}
    equilibrios, equilibrio_ok = paso_verificar_tablero.revisar_equilibrio(
        por_pestana, config)
    print("5. Equilibrio grafico/texto:")
    for fila in equilibrios:
        print(f"   {fila['pestana']:14} {fila['grafico']:>5} grafico · "
              f"{fila['texto']:>5} texto   [{fila['veredicto']}]")

    pie = (f"Tablero generado por la Etapa 4 del ciclo de analitica del aprendizaje "
           f"de la UCB a partir de {entrada.name}. Todas las cifras salen de ese "
           f"archivo: esta etapa no calcula ninguna. Los estudiantes se identifican "
           f"por su codigo.")
    documento = plantilla.armar(
        config, f"Tablero de analitica · {carpeta}",
        "Tres pestañas: como esta el curso, que se comprobo y que hacer.",
        [html1, html2, html3], pie)

    controles = paso_verificar_tablero.revisar_archivo(documento, datos, config)
    print("6. Comprobaciones del archivo:")
    for c in controles:
        print(f"   {'[OK]  ' if c['bien'] else '[FALLO]'} {c['control']}: {c['resultado']}")

    rastro = paso_verificar_tablero.buscar_datos_en_el_codigo(
        Path(__file__).resolve().parent, [metrica] if metrica else [])
    if rastro:
        print(f"   [FALLO] quedo un dato del docente en el codigo: {rastro}")
    else:
        print("   [OK]   nada de lo que se entrego quedo escrito en el programa")

    if not all(c["bien"] for c in controles):
        print("\nHay comprobaciones que fallaron. El tablero NO se guarda: "
              "corrija lo anterior y vuelva a ejecutar.")
        sys.exit(1)

    carpeta_salida = rev / "RESULTADOS" / "ETAPA 4 - VISUALIZAR"
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    salida = carpeta_salida / "DASHBOARD_ANALISIS.html"
    salida.write_text(documento, encoding="utf-8")

    intacta = entrada.exists() and entrada.stat().st_size > 0
    resumen = [
        ("Pestaña 1", f"{resumen1['elementos']} elemento(s) · {resumen1['fuentes']}"),
        ("Pestaña 2", f"{resumen2['elementos']} elemento(s) · {resumen2['fuentes']}"),
        ("Pestaña 3", f"{resumen3['elementos']} elemento(s) · {resumen3['fuentes']}"),
        ("Cifra destacada", metrica or "ninguna pedida: se muestra el n.º de hallazgos"),
        ("Equilibrio 60/40", "SI" if equilibrio_ok else "REVISAR — ver el detalle de arriba"),
        ("Comprobaciones superadas", f"{sum(1 for c in controles if c['bien'])} de {len(controles)}"),
        ("Analisis sin modificar", "SI" if intacta else "NO — REVISAR"),
        ("Peso del archivo", f"{len(documento) / 1024:.0f} KB"),
        ("Tablero", str(salida)),
    ]
    print("\n" + "=" * 74)
    print(" RESUMEN DE CONTROL")
    print("=" * 74)
    for etiqueta, valor in resumen:
        print(f"  {etiqueta:26} {valor}")
    print("=" * 74)
    if plan["no_se_puede"]:
        print("\n LO QUE NO SE PUDO MOSTRAR")
        print(" " + "-" * 25)
        for item in plan["no_se_puede"]:
            print(f"  · {item['no_se_podra_mostrar']}: {item['por_que'][:110]}")
    print(f"\n Abralo con doble clic: {salida.name}\n")
    return {"salida": salida, "equilibrios": equilibrios, "controles": controles}


def main():
    a = argparse.ArgumentParser(
        description="Etapa 4 — VISUALIZAR: construye el tablero de una materia.")
    a.add_argument("carpeta", nargs="?", help="nombre de la carpeta de la materia")
    a.add_argument("--raiz", default=".", help="carpeta que contiene a la de la materia")
    a.add_argument("--archivo", default="RESULTADOS_ANALISIS")
    a.add_argument("--config",
                   default=str(Path(__file__).resolve().parent / "config.json"))
    a.add_argument("--destacar", default="",
                   help="la cifra que debe ir en el lugar mas visible")
    a.add_argument("--plan", action="store_true",
                   help="muestra que se va a construir y no escribe nada")
    args = a.parse_args()

    comprobar_entorno()
    carpeta = args.carpeta or input("Nombre exacto de la carpeta de la materia: ").strip()
    ejecutar(carpeta, args.raiz, args.config, args.archivo, args.destacar, args.plan)


if __name__ == "__main__":
    main()
