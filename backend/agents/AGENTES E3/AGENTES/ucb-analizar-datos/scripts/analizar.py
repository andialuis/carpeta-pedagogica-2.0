"""Etapa 3 — ANALIZAR: punto de entrada unico.

Ejecuta el analisis completo sobre la BASE_DATOS_DEPURADA que dejo la Etapa 2.

    python3 analizar.py "NOMBRE_CARPETA" --raiz "." --plan
    python3 analizar.py "NOMBRE_CARPETA" --raiz "." --hipotesis "..."

Con --plan no analiza nada: muestra las cinco tablas que el docente aprueba en la
segunda pausa y no escribe un solo archivo.

Ni la hipotesis ni la sospecha ni ninguna ruta quedan escritas en el codigo (R6):
entran por la linea de ordenes en cada ejecucion.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paso_analizar_actividad
import paso_clasificar_estudiantes
import paso_comparar_instrumentos
import paso_correlacionar_variables
import paso_detectar_hallazgos
import paso_detectar_perfiles
import paso_evaluar_hipotesis
import paso_generar_indicadores
import paso_leer_depurada
import paso_reportar
from paso_leer_depurada import (CONSTANTE, CONTEXTO, IDENTIDAD, PAPELEO,
                                SIN_EMPAREJAR, normalizar,
                                serie)

VERSION_MINIMA = (3, 8)


def comprobar_entorno():
    if sys.version_info < VERSION_MINIMA:
        print(f"Se necesita Python {'.'.join(map(str, VERSION_MINIMA))} o superior.")
        sys.exit(1)
    faltan = []
    for modulo, paquete in (("openpyxl", "openpyxl"), ("docx", "python-docx"),
                            ("matplotlib", "matplotlib")):
        try:
            __import__(modulo)
        except ImportError:
            faltan.append(paquete)
    if faltan:
        print("Faltan librerias obligatorias. Instalalas con:")
        print(f"  {Path(sys.executable).name} -m pip install {' '.join(faltan)}")
        sys.exit(1)
    import matplotlib
    import openpyxl
    print("\nENTORNO")
    print("-" * 40)
    print(f"  Python           : {'.'.join(map(str, sys.version_info[:3]))}")
    print(f"  openpyxl         : {openpyxl.__version__}")
    print(f"  matplotlib       : {matplotlib.__version__}")
    print("  python-docx      : instalado")


def localizar(carpeta, raiz, nombre_archivo):
    """Encuentra la BASE_DATOS_DEPURADA dentro de la carpeta -REV."""
    rev = Path(raiz) / f"{carpeta}-REV"
    if not rev.is_dir():
        rev = Path(raiz) / carpeta
    bases = rev / "bases_de_datos"
    if not bases.is_dir():
        return None, rev
    candidatos = [c for c in sorted(bases.glob(f"{nombre_archivo}*.xlsx"))
                  if not c.name.startswith("~$")]
    return (candidatos[0] if candidatos else None), rev


# ------------------------------------------------------------------- el plan
def construir_plan(hipotesis, columnas, filas, fichas, senales, explicacion,
                   resumen, config):
    """Las cinco tablas de la segunda pausa: A, B, C, D y E."""
    reescrita, avisos = paso_evaluar_hipotesis.evaluar(
        hipotesis, columnas, filas, fichas, senales, config)

    disponibles = [{"columna": f["columna"], "papel": f["papel"],
                    "con_dato": f["con_dato"]}
                   for f in fichas
                   if f["papel"] not in (IDENTIDAD, CONSTANTE,
                                        SIN_EMPAREJAR, PAPELEO)]
    sin_variacion = [{"columna": f["columna"], "por_que": f["por_que"]}
                     for f in fichas
                     if f["papel"] in (CONSTANTE, SIN_EMPAREJAR, PAPELEO)]

    no_se_puede = []
    if not any(s.get("plataforma") is not None for s in senales):
        no_se_puede.append({
            "analisis": "actividad en el aula virtual",
            "por_que": "ninguna columna de la base registra entradas a la "
                       "plataforma"})
    if not any(s.get("asistencia") is not None for s in senales):
        no_se_puede.append({
            "analisis": "asistencia",
            "por_que": "ninguna columna de la base registra asistencia"})
    if not any(f["papel"] == CONTEXTO for f in fichas):
        no_se_puede.append({
            "analisis": "comparacion entre grupos (turno, modalidad, sede)",
            "por_que": "la base no trae ninguna columna que agrupe a los "
                       "estudiantes en categorias comparables"})
    if explicacion["instrumentos"] == 0:
        no_se_puede.append({
            "analisis": "todo lo que dependa del rendimiento",
            "por_que": "no se reconocio ninguna columna de calificacion"})

    entran = [
        {"analisis": "panorama del curso y perfiles",
         "estudiantes": resumen["total"],
         "detalle": f"{resumen['activos']} activos + {resumen['abandonos']} "
                    "abandonos"},
        {"analisis": "rendimiento",
         "estudiantes": sum(1 for s in senales if s["rendimiento"] is not None),
         "detalle": explicacion["metodo"]},
        {"analisis": "asistencia",
         "estudiantes": sum(1 for s in senales if s["asistencia"] is not None),
         "detalle": f"{explicacion['columnas_de_asistencia']} columna(s)"},
        {"analisis": "actividad en plataforma",
         "estudiantes": sum(1 for s in senales if s["plataforma"] is not None),
         "detalle": f"{explicacion['columnas_de_plataforma']} columna(s)"},
    ]

    return {"hipotesis": reescrita, "avisos": avisos, "disponibles": disponibles,
            "sin_variacion": sin_variacion, "no_se_puede": no_se_puede,
            "entran": entran}


def imprimir_plan(plan, explicacion):
    def tabla(titulo, registros, campos, anchos):
        print(f"\n{titulo}")
        print("-" * len(titulo))
        if not registros:
            print("  (nada que mostrar en este apartado)")
            return
        print("  " + "".join(c[:a - 1].ljust(a) for c, a in zip(campos, anchos)))
        print("  " + "-" * (sum(anchos) - 1))
        for registro in registros[:40]:
            print("  " + "".join(
                str(registro.get(c, ""))[:a - 1].ljust(a)
                for c, a in zip(campos, anchos)))
        if len(registros) > 40:
            print(f"  ... y {len(registros) - 40} mas")

    print("\nA · LA HIPOTESIS, REESCRITA PARA PODER COMPROBARLA")
    print("-" * 49)
    h = plan["hipotesis"]
    if not h:
        print("  No se entrego ninguna hipotesis. El analisis se hara sin ella.")
    else:
        print(f"  Lo que dice     : {h['hipotesis']}")
        print(f"  Que se mide     : {h.get('medida', '(no se reconocio)')}")
        print(f"  A quien compara : {h.get('grupo', '(no se reconocio)')}")
        print(f"  Se puede medir  : "
              f"{'si' if h['veredicto'] != 'no se puede comprobar con estos datos' else 'NO'}")
        if h["veredicto"].startswith("no se puede"):
            print(f"  Por que no      : {h['detalle']}")
    for aviso in plan["avisos"]:
        print(f"  AVISO: {aviso}")

    tabla("B · VARIABLES DISPONIBLES PARA CRUZAR", plan["disponibles"],
          ["columna", "papel", "con_dato"], [52, 26, 10])
    tabla("C · VARIABLES QUE NO SIRVEN (valen lo mismo para todos)",
          plan["sin_variacion"], ["columna", "por_que"], [40, 60])
    tabla("D · ANALISIS QUE NO SE VAN A PODER HACER", plan["no_se_puede"],
          ["analisis", "por_que"], [42, 62])
    tabla("E · CUANTOS ESTUDIANTES ENTRAN EN CADA ANALISIS", plan["entran"],
          ["analisis", "estudiantes", "detalle"], [34, 13, 58])

    print(f"\n  Como se construyo la medida de rendimiento: {explicacion['metodo']}")
    print(f"  {explicacion['vacios']}")
    print("\n" + "=" * 78)
    print(" Si apruebas este plan, ejecuta de nuevo sin --plan.")
    print("=" * 78)


# ---------------------------------------------------------------- ejecucion
def ejecutar(carpeta, raiz, ruta_config, nombre_archivo, hipotesis, sospecha,
             solo_plan):
    config = json.loads(Path(ruta_config).read_text(encoding="utf-8"))
    entrada, rev = localizar(carpeta, raiz, nombre_archivo)
    if entrada is None:
        print(f"\nNo se encontro {nombre_archivo}*.xlsx en "
              f"{rev / 'bases_de_datos'}.")
        print("Esta etapa necesita el resultado de la Etapa 2. Ejecutala primero.")
        sys.exit(1)

    print(f"\nANALIZANDO: {entrada.name}")
    print(f"Carpeta de trabajo: {rev.name}")

    datos = paso_leer_depurada.leer(entrada)
    for aviso in datos["avisos"]:
        print(f"  AVISO: {aviso}")

    columnas, filas, aviso_abandonos = paso_leer_depurada.unir_curso(datos)
    if aviso_abandonos:
        print(f"  AVISO: {aviso_abandonos}")
        datos["avisos"].append(aviso_abandonos)
    if not filas:
        print("\nLa base no tiene ningun estudiante. No hay nada que analizar.")
        sys.exit(1)
    clave = paso_leer_depurada.columna_clave(columnas, filas)
    fichas = paso_leer_depurada.clasificar_columnas(columnas, filas, clave,
                                                    config, datos["reglas"])
    print(f"1. Curso leido: {len(filas)} estudiante(s) y {len(columnas)} "
          "columna(s).")

    senales, explicacion, resumen = paso_clasificar_estudiantes.clasificar(
        columnas, filas, fichas, datos["reglas"], clave, config)
    print(f"2. Curso completo: {resumen['activos']} activo(s) + "
          f"{resumen['abandonos']} abandono(s) = {resumen['total']}.")

    plan = construir_plan(hipotesis, columnas, filas, fichas, senales,
                          explicacion, resumen, config)
    if solo_plan:
        imprimir_plan(plan, explicacion)
        return {"plan": plan}

    hipotesis_docente = plan["hipotesis"]
    hipotesis_programa, avisos_hipotesis = \
        paso_evaluar_hipotesis.hipotesis_del_programa(columnas, filas, fichas,
                                                      senales, config,
                                                      hipotesis_docente)
    sostenidas = sum(1 for h in [hipotesis_docente] + hipotesis_programa
                     if h and str(h.get("veredicto", "")).startswith("se sostiene"))
    print(f"3. Hipotesis puestas a prueba: "
          f"{len(hipotesis_programa) + (1 if hipotesis_docente else 0)}, "
          f"{sostenidas} se sostiene(n).")
    for aviso in avisos_hipotesis:
        print(f"   AVISO: {aviso}")

    cruces = paso_correlacionar_variables.cruzar(columnas, filas, fichas,
                                                 senales, clave, config)
    print(f"4. Relaciones: {len(cruces['relaciones'])} relevante(s), "
          f"{len(cruces['redundantes'])} apartada(s) por triviales, "
          f"{len(cruces['tapadas_por_casos_extremos'])} tapada(s) por casos "
          "extremos.")

    instrumentos = paso_comparar_instrumentos.comparar(columnas, filas, fichas,
                                                       senales, clave, config)
    print(f"5. Instrumentos: "
          f"{instrumentos['resumen']['instrumentos_vigilados']} vigilado(s) "
          f"contra {instrumentos['resumen']['instrumentos_no_vigilados']} por "
          f"cuenta propia; {len(instrumentos['observaciones'])} observacion(es).")

    # La carpeta original de la materia va tambien: el registro del aula que
    # descargo el docente sigue ahi, no en la carpeta de resultados.
    actividad = paso_analizar_actividad.analizar(rev, config,
                                                 Path(raiz) / carpeta)
    if actividad["disponible"]:
        print(f"6. Aula virtual: {actividad['eventos']} evento(s) en "
              f"{actividad['archivo']}.")
    else:
        print(f"6. Aula virtual: {actividad['por_que'][:96]}")

    perfiles, asignacion, avisos_perfiles = paso_detectar_perfiles.detectar(
        senales, config)
    print(f"7. Perfiles ocultos: {len(perfiles)}.")
    for aviso in avisos_perfiles:
        print(f"   AVISO: {aviso}")

    hallazgos, faltantes, que_haria_falta, sobrantes = paso_detectar_hallazgos.reunir(
        resumen, perfiles, cruces, hipotesis_docente, hipotesis_programa,
        instrumentos, actividad, senales, config,
        [dict(zip(datos["abandonos"]["columnas"], f))
         for f in datos["abandonos"]["filas"]])
    print(f"8. Hallazgos que se sostienen: {len(hallazgos)} "
          f"(faltaron {faltantes} para llegar a {config['hallazgos_objetivo']}; "
          f"{sobrantes} quedaron fuera del informe por espacio).")

    lista_indicadores = paso_generar_indicadores.indicadores(
        senales, perfiles, cruces, config)
    lista_acciones = paso_generar_indicadores.acciones(perfiles, hallazgos,
                                                       resumen, config)
    lista_prioridades = paso_generar_indicadores.prioridades(senales, asignacion,
                                                             config)
    print(f"9. Indicadores: {len(lista_indicadores)}; acciones: "
          f"{len(lista_acciones)}; estudiantes priorizados: "
          f"{len(lista_prioridades)}.")

    # ---------------------------------------------------------------- salida
    hipotesis_todas = ([hipotesis_docente] if hipotesis_docente else []) + \
        hipotesis_programa
    no_se_pudo = plan["no_se_puede"] + instrumentos["no_se_pudo"]
    if not actividad["disponible"]:
        no_se_pudo.append({"analisis": "linea de tiempo del aula virtual",
                           "por_que": actividad["por_que"]})

    resultados = {
        "HALLAZGOS": hallazgos,
        "HIPOTESIS": hipotesis_todas,
        "PERFILES": perfiles,
        "RELACIONES": cruces["relaciones"],
        "INDICADORES": lista_indicadores,
        "ACCIONES": lista_acciones,
        "PRIORIDADES": lista_prioridades,
        "COLUMNAS": [{"columna": f["columna"], "papel": f["papel"],
                      "por_que": f["por_que"], "con_dato": f["con_dato"],
                      "distintos": f["distintos"]} for f in fichas],
        "NO_SE_PUDO": no_se_pudo,
        "_senales": senales,
        "_instrumentos": instrumentos,
        "_actividad": actividad,
        "_dispersion": _dispersion(cruces, columnas, filas, fichas, senales, clave),
    }

    bases = entrada.parent
    carpeta_resultados = rev / "RESULTADOS" / "ETAPA 3 - ANALIZAR"
    carpeta_resultados.mkdir(parents=True, exist_ok=True)

    imagenes = paso_reportar.dibujar(carpeta_resultados / "graficos", resultados,
                                     config)
    resultados["DATOS_GRAFICOS"] = paso_reportar.datos_de_graficos(resultados,
                                                                   imagenes)
    ruta_excel = paso_reportar.escribir_resultados(
        bases / "RESULTADOS_ANALISIS.xlsx", resultados)
    codigo_huella = paso_reportar.huella(resultados)

    contenido = {
        "sospecha": sospecha.strip(),
        "panorama": _panorama(resumen, explicacion, cruces),
        "hallazgos": hallazgos,
        "faltantes": faltantes,
        "objetivo": config["hallazgos_objetivo"],
        "que_haria_falta": que_haria_falta,
        "perfiles": perfiles,
        "hipotesis": hipotesis_todas,
        "relaciones": cruces["relaciones"],
        "redundantes": cruces["redundantes"],
        "aviso_tamano": " ".join(x for x in (
            paso_correlacionar_variables.aviso_de_tamano(cruces["relaciones"],
                                                         filas, config),
            cruces["aviso_comparaciones_multiples"]) if x),
        "avisos": datos["avisos"] + avisos_hipotesis + avisos_perfiles,
        "sobrantes": sobrantes,
        "acciones": lista_acciones,
        "indicadores": lista_indicadores,
        "no_se_pudo": no_se_pudo,
        "columnas": resultados["COLUMNAS"],
        "conclusion_tecnica": _conclusion(datos, explicacion, cruces, actividad,
                                          faltantes, que_haria_falta, filas),
    }
    ruta_informe = paso_reportar.escribir_informe(
        carpeta_resultados / "INFORME_FINAL_ANALISIS.docx", carpeta, contenido,
        imagenes)

    intacta = entrada.exists() and entrada.stat().st_size > 0
    resumen_control = [
        ("Estudiantes analizados", resumen["total"]),
        ("  · activos", resumen["activos"]),
        ("  · abandonos", resumen["abandonos"]),
        ("Medida de rendimiento", explicacion["metodo"]),
        ("Hallazgos que se sostienen", len(hallazgos)),
        ("Hallazgos que faltaron", faltantes),
        ("Hallazgos fuera del informe", sobrantes),
        ("Hipotesis puestas a prueba", len(hipotesis_todas)),
        ("  · que se sostienen", sostenidas),
        ("Relaciones relevantes", len(cruces["relaciones"])),
        ("  · parejas comprobadas", cruces["relaciones_probadas"]),
        ("Cruces apartados por triviales", len(cruces["redundantes"])),
        ("Perfiles ocultos", len(perfiles)),
        ("Analisis que no se pudieron hacer", len(no_se_pudo)),
        ("Graficos generados", len(imagenes)),
        ("Base depurada sin modificar", "SI" if intacta else "NO — REVISAR"),
        ("Huella del analisis", codigo_huella),
        ("Resultados", str(ruta_excel)),
        ("Informe", str(ruta_informe)),
    ]
    print("\n" + "=" * 74)
    print(" RESUMEN DE CONTROL")
    print("=" * 74)
    for etiqueta, valor in resumen_control:
        print(f"  {etiqueta:36} {valor}")
    print("=" * 74)
    if no_se_pudo:
        print("\n LO QUE NO SE PUDO ANALIZAR")
        print(" " + "-" * 26)
        for item in no_se_pudo:
            print(f"  · {item['analisis']}: {item['por_que'][:120]}")
    print()
    return {"huella": codigo_huella, "excel": ruta_excel, "informe": ruta_informe}


def _dispersion(cruces, columnas, filas, fichas, senales, clave):
    """Los puntos del grafico de la relacion mas fuerte que se sostuvo."""
    if not cruces["relaciones"]:
        return None
    mejor = cruces["relaciones"][0]

    def valores_de(nombre):
        if nombre == "rendimiento general del estudiante":
            return [s.get("rendimiento") for s in senales]
        if nombre == "asistencia del semestre":
            return [s.get("asistencia") for s in senales]
        if nombre == "actividad total en la plataforma":
            return [s.get("plataforma") for s in senales]
        for ficha in fichas:
            if ficha["columna"] == nombre:
                return serie(filas, ficha["indice"])
        return None

    x = valores_de(mejor["columna_a"])
    y = valores_de(mejor["columna_b"])
    if x is None or y is None:
        return None
    puntos = [(str(f[clave]).strip(), a, b) for f, a, b in zip(filas, x, y)
              if a is not None and b is not None]
    if not puntos:
        return None
    return {
        "titulo": f"Relacion {mejor['fuerza']} ({mejor['relacion']:+.2f})",
        "etiqueta_x": mejor["columna_a"], "etiqueta_y": mejor["columna_b"],
        "codigos": [p[0] for p in puntos],
        "x": [p[1] for p in puntos], "y": [p[2] for p in puntos],
    }


def _panorama(resumen, explicacion, cruces):
    partes = [
        f"El curso tuvo {resumen['total']} estudiantes: {resumen['activos']} "
        f"siguieron hasta el final y {resumen['abandonos']} dejaron de "
        "participar. Los dos grupos entran en todos los analisis de este "
        "informe: dejar fuera a quienes se fueron hace desaparecer justo el "
        "problema que se quiere estudiar."]
    if resumen["rendimiento_medio"] is not None:
        partes.append(
            f"El rendimiento medio del curso es {resumen['rendimiento_medio']:.2f} "
            "en escala 0 a 1. Esta medida se construyo con "
            f"{explicacion['metodo']}, y no es la nota oficial de nadie: es una "
            "variable de analisis para poder comparar instrumentos que estan en "
            "escalas distintas.")
    reparto = ", ".join(f"{g['estudiantes']} en el {g['grupo']}"
                        for g in resumen["grupos"])
    partes.append(f"Repartidos asi: {reparto}.")
    return " ".join(partes)


def _conclusion(datos, explicacion, cruces, actividad, faltantes,
                que_haria_falta, filas):
    partes = []
    if len(filas) < 40:
        partes.append(
            f"Con {len(filas)} estudiantes, este analisis describe a ESTE curso y "
            "no permite generalizar a otros. Cada relacion se acompana del numero "
            "de estudiantes que la sostiene, y ese numero es el que manda.")
    partes.append(
        "Ninguna de las relaciones de este informe demuestra una causa. Que dos "
        "cosas se muevan juntas puede significar que una influye en la otra, que "
        "las dos dependen de una tercera, o que es casualidad.")
    if datos["anomalias_heredadas"]:
        partes.append(
            f"La base todavia arrastra {len(datos['anomalias_heredadas'])} valor(es) "
            "marcados como sospechosos por la etapa anterior. No se corrigieron "
            "aqui: hacerlo dejaria dos versiones distintas de la misma nota y "
            "nadie se enteraria.")
    if not actividad["disponible"]:
        partes.append("No se analizo la linea de tiempo del aula virtual: "
                      + actividad["por_que"])
    if faltantes and que_haria_falta:
        partes.append("Para llegar a mas hallazgos haria falta: "
                      + "; ".join(que_haria_falta) + ".")
    else:
        partes.append("Los datos alcanzaron para sostener todos los hallazgos "
                      "que se reportan.")
    return " ".join(partes)


def main():
    analizador = argparse.ArgumentParser(
        description="Etapa 3 — ANALIZAR: analiza la base depurada de una materia.")
    analizador.add_argument("carpeta", nargs="?",
                            help="nombre de la carpeta de la materia")
    analizador.add_argument("--raiz", default=".",
                            help="carpeta que contiene a la de la materia")
    analizador.add_argument("--archivo", default="BASE_DATOS_DEPURADA",
                            help="nombre del archivo a analizar")
    analizador.add_argument("--config",
                            default=str(Path(__file__).resolve().parent / "config.json"))
    analizador.add_argument("--hipotesis", default="",
                            help="la hipotesis del docente, entre comillas")
    analizador.add_argument("--sospecha", default="",
                            help="el problema que el docente quiere someter a analisis")
    analizador.add_argument("--plan", action="store_true",
                            help="muestra el plan de analisis y no escribe nada")
    argumentos = analizador.parse_args()

    comprobar_entorno()
    carpeta = argumentos.carpeta or input(
        "Nombre exacto de la carpeta de la materia: ").strip()
    ejecutar(carpeta, argumentos.raiz, argumentos.config, argumentos.archivo,
             argumentos.hipotesis, argumentos.sospecha, argumentos.plan)


if __name__ == "__main__":
    main()
