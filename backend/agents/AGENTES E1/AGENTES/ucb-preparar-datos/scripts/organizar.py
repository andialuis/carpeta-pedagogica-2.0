"""organizacion_carpeta_docente — ETAPA 1: PREPARAR

Punto de entrada unico. Ordena una carpeta de materia, reconoce a cada estudiante
entre planillas que lo escriben distinto, y une todo en un solo archivo Excel con
sus hojas de auditoria.

Esta etapa SOLO PREPARA: no limpia, no rellena vacios, no convierte escalas, no
calcula notas y no separa a nadie. Todo eso corresponde a la etapa siguiente.

Uso:
    python organizar.py NOMBRE_CARPETA [--raiz RUTA] [--aprobados archivo.json]

El programa no contiene ningun dato de ninguna materia: todo entra al ejecutarlo.
"""

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_clasificar import clasificar, huella_archivo
from skill_descubrir_reglas import anclar_a_columnas, descubrir
from skill_extraer_datos import (procesar_documentos,
                                 procesar_para_transcripcion)
from skill_identidad import Reconocedor
from skill_integrar import construir_estudiantes, elegir_lista_oficial, integrar
from skill_leer_planillas import VACIO, _tipo, leer_csv, leer_fuente
from skill_reportar import (contar_columnas_plegables, escribir_base,
                            escribir_informe, huella_contenido)

EXTENSIONES_TABULARES = {".xlsx", ".xlsm", ".csv", ".tsv"}
EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".heic"}
EXTENSIONES_TEXTO = {".txt", ".md", ".docx", ".pptx"}
# El PDF no se abre desde aqui: lo transcribe el agente, igual que una
# imagen. Por eso cuenta como analizable y no como formato ilegible.
EXTENSIONES_PDF = {".pdf"}

# Todo lo que el programa sabe abrir. Un formato fuera de este conjunto se copia
# igual, pero tiene que quedar REPORTADO: R6 prohibe que algo se pierda en silencio.
EXTENSIONES_ANALIZABLES = (EXTENSIONES_TABULARES | EXTENSIONES_IMAGEN
                          | EXTENSIONES_TEXTO | EXTENSIONES_PDF)


def _es_tabla_de_verdad(hoja):
    """Distingue una planilla en texto de una frase con comas.

    'Sobre un total de 100 puntos, estas son las distribuciones, independiente de
    la escala' tiene dos comas y parece un encabezado de tres columnas. Lo que la
    delata es que las lineas de abajo NO estan delimitadas: traen un solo campo.
    En una planilla de verdad, casi todas las filas tienen varios campos.
    """
    if len(hoja["columnas"]) < 2 or len(hoja["filas"]) < 2:
        return False
    delimitadas = sum(1 for f in hoja["filas"]
                      if sum(1 for v in f if _tipo(v) != VACIO) >= 2)
    return delimitadas >= len(hoja["filas"]) * 0.7


def cargar_config(ruta_config):
    return json.loads(Path(ruta_config).read_text(encoding="utf-8"))


VERSION_MINIMA = (3, 8)


def comprobar_entorno():
    print("CHEQUEO PREVIO")
    print(f"  Python           : {sys.version.split()[0]}")
    print(f"  Sistema          : {sys.platform}")
    if sys.version_info < VERSION_MINIMA:
        actual = ".".join(str(n) for n in sys.version_info[:3])
        minima = ".".join(str(n) for n in VERSION_MINIMA)
        print(f"\nEste programa necesita Python {minima} o superior; "
              f"esta computadora tiene {actual}.")
        print("Instala una version mas nueva desde https://www.python.org/downloads/")
        sys.exit(1)
    try:
        import openpyxl
        print(f"  openpyxl         : {openpyxl.__version__}")
    except ImportError:
        print("  openpyxl         : NO INSTALADO")
        print("\nFalta una dependencia obligatoria. Instalala con:")
        print("    pip install openpyxl")
        sys.exit(1)


def ejecutar(nombre_carpeta, raiz, ruta_config, ruta_aprobados=None):
    config = cargar_config(ruta_config)
    raiz = Path(raiz).resolve()
    origen = raiz / nombre_carpeta
    if not origen.is_dir():
        print(f"ERROR: no existe la carpeta '{origen}'.")
        sys.exit(1)
    destino = raiz / f"{nombre_carpeta}-REV"

    print(f"\nORGANIZANDO: {origen.name}")
    print(f"Carpeta de trabajo: {destino.name}\n")

    # --- 1. Ordenar -----------------------------------------------------------
    inventario, rutas = clasificar(origen, destino, config)
    aprobados = None
    if ruta_aprobados:
        aprobados = set(json.loads(Path(ruta_aprobados).read_text(encoding="utf-8")))
    for entrada in inventario:
        entrada["aprobado"] = aprobados is None or entrada["archivo"] in aprobados

    # Dos archivos con la misma huella son el mismo archivo con otro nombre. Se
    # copian ambos a -REV (no se pierde nada), pero analizar los dos duplicaria
    # cada columna sin aportar un solo dato nuevo.
    vistos_por_huella = {}
    for entrada in inventario:
        gemelo = vistos_por_huella.get(entrada["huella_origen"])
        if gemelo is None:
            vistos_por_huella[entrada["huella_origen"]] = entrada["archivo"]
            entrada["duplicado_de"] = None
        else:
            entrada["duplicado_de"] = gemelo

    analizables = [e for e in inventario
                   if e["aprobado"] and e["duplicado_de"] is None]
    print(f"1. Clasificados {len(inventario)} archivo(s); "
          f"{len(analizables)} aprobado(s) para el analisis.")

    incidencias = []
    for entrada in inventario:
        if not entrada["extension_conocida"]:
            incidencias.append({
                "tipo": "extension_desconocida",
                "archivo": entrada["archivo"],
                "detalle": f"se guardo en '{entrada['subcarpeta']}' sin analizarse",
            })
        elif (entrada["aprobado"]
              and entrada["extension"] not in EXTENSIONES_ANALIZABLES):
            incidencias.append({
                "tipo": "formato_aprobado_que_no_se_puede_abrir",
                "archivo": entrada["archivo"],
                "detalle": (f"el formato '{entrada['extension']}' se organizo en "
                            f"'{entrada['subcarpeta']}' pero este programa no lo sabe "
                            f"leer, asi que sus datos NO entraron a la base. "
                            f"Conviertelo a .xlsx o .csv y vuelve a ejecutar."),
            })
        if entrada["duplicado_de"] and entrada["aprobado"]:
            incidencias.append({
                "tipo": "archivo_duplicado_identico",
                "archivo": entrada["archivo"],
                "detalle": (f"tiene exactamente el mismo contenido que "
                            f"'{entrada['duplicado_de']}' (misma huella SHA-256). Se "
                            f"copio a la carpeta de trabajo, pero NO se integro: sus "
                            f"columnas ya estan en la base a traves del otro archivo."),
            })
        if not entrada["aprobado"]:
            incidencias.append({
                "tipo": "archivo_no_aprobado",
                "archivo": entrada["archivo"],
                "detalle": f"organizado en '{entrada['subcarpeta']}', fuera del analisis",
            })

    # --- 2. Rescatar datos de imagenes ---------------------------------------
    # Imagenes y PDF comparten camino: el programa no los abre, los transcribe el
    # agente y aqui solo se recoge el resultado.
    para_transcribir = [e["ruta_copia"] for e in analizables
                        if e["ruta_copia"].suffix.lower()
                        in (EXTENSIONES_IMAGEN | EXTENSIONES_PDF)]
    documentos = [e["ruta_copia"] for e in analizables
                  if e["ruta_copia"].suffix.lower() in EXTENSIONES_TEXTO]

    extraidas, textos_transcritos, inc_transcripcion = procesar_para_transcripcion(
        para_transcribir, rutas["bases_de_datos"])
    # La normativa transcrita de un PDF se revisa igual que cualquier documento.
    documentos += textos_transcritos

    de_documentos, inc_documentos = procesar_documentos(documentos,
                                                        rutas["bases_de_datos"])
    extraidas += de_documentos
    incidencias.extend(inc_transcripcion)
    incidencias.extend(inc_documentos)
    print(f"2. Archivos a transcribir: {len(para_transcribir)}; documentos "
          f"aprobados: {len(documentos)}; hojas de datos rescatadas: "
          f"{len(extraidas)}.")

    # --- 3. Leer planillas ----------------------------------------------------
    rutas_tabulares = [e["ruta_copia"] for e in analizables
                       if e["ruta_copia"].suffix.lower() in EXTENSIONES_TABULARES]
    rutas_tabulares += [r for r in extraidas if r not in rutas_tabulares]

    # Un .txt puede ser una planilla separada por comas o punto y coma. Si el
    # documento ya entrego una lista de notas, no se toca; si no, se intenta leer
    # como tabla. Sin esto, una planilla guardada como texto se pierde entera.
    con_extraccion = {i["archivo"] for i in inc_documentos
                      if i["tipo"] == "datos_rescatados_de_documento"}
    for documento in documentos:
        if (documento.suffix.lower() not in (".txt", ".md")
                or documento.name in con_extraccion):
            continue
        hojas = leer_csv(documento, config["max_filas_encabezado"])
        if hojas and _es_tabla_de_verdad(hojas[0]):
            rutas_tabulares.append(documento)
            incidencias.append({
                "tipo": "texto_leido_como_planilla",
                "archivo": documento.name,
                "detalle": f"el archivo es texto delimitado: se leyo como planilla "
                           f"con {len(hojas[0]['columnas'])} columna(s) y "
                           f"{len(hojas[0]['filas'])} fila(s)",
            })

    fuentes, huellas_lectura = [], {}
    for ruta in sorted(set(rutas_tabulares), key=lambda p: p.name):
        hojas = leer_fuente(ruta, config["max_filas_encabezado"])
        if not hojas:
            incidencias.append({"tipo": "planilla_vacia", "archivo": ruta.name,
                                "detalle": "no se encontraron filas de datos"})
            continue
        for hoja in hojas:
            for letra, cuantas in sorted(hoja.get("calculadas_sin_valor", {}).items()):
                incidencias.append({
                    "tipo": "columna_calculada_sin_valor",
                    "archivo": ruta.name,
                    "valor_original": f"columna {letra} · hoja '{hoja['hoja']}'",
                    "detalle": (f"{cuantas} celda(s) tienen una formula pero el "
                                f"archivo no guardo el resultado, asi que entraron "
                                f"VACIAS a la base. Abre '{ruta.name}' en Excel, "
                                f"guardalo y vuelve a ejecutar; o reemplaza las "
                                f"formulas por sus valores."),
                })
        fuentes.append({"archivo": ruta.name, "etiqueta": ruta.stem,
                        "ruta": ruta, "hojas": hojas})
        huellas_lectura[ruta.name] = sum(len(h["filas"]) for h in hojas)
    print(f"3. Planillas leidas: {len(fuentes)} "
          f"({sum(len(f['hojas']) for f in fuentes)} hoja(s) en total).")

    # --- 4. Lista oficial -----------------------------------------------------
    fuente_oficial, motivo = elegir_lista_oficial(fuentes, config)
    if fuente_oficial is None:
        print("ERROR: no se pudo identificar la lista oficial de estudiantes.")
        sys.exit(1)
    estudiantes, columnas_oficial = construir_estudiantes(fuente_oficial["hojas"][0])
    print(f"4. Lista oficial: '{fuente_oficial['archivo']}' ({motivo}); "
          f"{len(estudiantes)} estudiante(s).")

    vistos = {}
    for est in estudiantes:
        vistos.setdefault(est["id"], []).append(est["nombre"])
    for codigo, nombres in vistos.items():
        if len(nombres) > 1:
            incidencias.append({
                "tipo": "codigo_repetido_en_lista_oficial",
                "archivo": fuente_oficial["archivo"],
                "valor_original": codigo,
                "detalle": f"comparten codigo: {' | '.join(nombres)}; se conservan todos",
            })

    # --- 5. Reconocer e integrar ---------------------------------------------
    reconocedor = Reconocedor(estudiantes, config)
    (columnas_base, filas_base, cobertura, emparejamientos,
     inc_integrar, diccionario) = integrar(fuentes, estudiantes, reconocedor,
                                           columnas_oficial, fuente_oficial)
    incidencias.extend(inc_integrar)
    print(f"5. Integracion: {len(filas_base)} fila(s) y "
          f"{len(columnas_base)} columna(s).")

    # --- 6. Reglas de evaluacion ---------------------------------------------
    reglas, notas_reglas = descubrir(documentos, config)
    reglas = anclar_a_columnas(reglas, diccionario)
    print(f"6. Reglas de evaluacion encontradas: {len(reglas)}.")

    # --- 7. Escribir ----------------------------------------------------------
    salida = rutas["bases_de_datos"] / "BASE_INTEGRADA.xlsx"
    escribir_base(salida, columnas_base, filas_base, diccionario, cobertura,
                  emparejamientos, incidencias, reglas,
                  f"{fuente_oficial['archivo']} ({motivo})")

    indice_id = 0
    for indice, columna in enumerate(columnas_base):
        if columnas_oficial["codigo"] is not None and indice == columnas_oficial["codigo"]:
            indice_id = indice
            break
    huella = huella_contenido(columnas_base, filas_base, indice_id)

    intactos = all(huella_archivo(origen / e["archivo"]) == e["huella_origen"]
                   for e in inventario)

    resumen = _resumen(origen, salida, inventario, analizables, fuentes, estudiantes,
                       columnas_base, filas_base, cobertura, emparejamientos,
                       incidencias, reglas, notas_reglas, huella, intactos,
                       fuente_oficial, motivo, diccionario)
    escribir_informe(destino / "INFORME_PREPARACION.md", resumen)

    (destino / "manifiesto.json").write_text(json.dumps({
        "carpeta_origen": origen.name,
        "archivos_de_entrada": [{"archivo": e["archivo"], "huella": e["huella_origen"],
                                 "aprobado": e["aprobado"]} for e in inventario],
        "salidas_generadas": ["bases_de_datos/BASE_INTEGRADA.xlsx",
                              "INFORME_PREPARACION.md"],
        "huella_contenido_base": huella,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    _imprimir_resumen(resumen)
    return {"salida": salida, "huella": huella}


def _resumen(origen, salida, inventario, analizables, fuentes, estudiantes,
             columnas_base, filas_base, cobertura, emparejamientos, incidencias,
             reglas, notas_reglas, huella, intactos, fuente_oficial, motivo,
             diccionario):
    conteo_situacion = {}
    for registro in cobertura:
        conteo_situacion[registro["situacion"]] = conteo_situacion.get(
            registro["situacion"], 0) + 1

    conteo_metodo = {}
    for registro in emparejamientos:
        conteo_metodo[registro["metodo"]] = conteo_metodo.get(registro["metodo"], 0) + 1

    conteo_incidencia = {}
    for registro in incidencias:
        conteo_incidencia[registro["tipo"]] = conteo_incidencia.get(
            registro["tipo"], 0) + 1

    columnas_por_archivo = []
    for fuente in fuentes:
        for hoja in fuente["hojas"]:
            columnas_por_archivo.append(
                f"{fuente['archivo']} · hoja '{hoja['hoja']}': "
                f"{len(hoja['columnas'])} columna(s) de origen, "
                f"{len(hoja['filas'])} fila(s), "
                f"encabezado de {hoja['filas_encabezado']} fila(s)")

    return [
        ("Archivos", [f"{e['archivo']} -> {e['subcarpeta']}"
                      f"{'' if e['aprobado'] else '  (no aprobado, fuera del analisis)'}"
                      for e in inventario]),
        ("Lista oficial", f"{fuente_oficial['archivo']} ({motivo}) — "
                          f"{len(estudiantes)} estudiante(s)"),
        ("Filas", f"lista oficial: {len(estudiantes)} · "
                  f"BASE_INTEGRADA: {len(filas_base)}"),
        ("Columnas por archivo de origen", columnas_por_archivo),
        ("Columnas conservadas en la base", str(len(columnas_base))),
        ("Columnas de identidad repetidas",
         f"{contar_columnas_plegables(diccionario)} columna(s) de nombre o correo "
         f"de los archivos de origen quedan PLEGADAS en la hoja BASE (se ven con el "
         f"signo + de Excel). Se conservan enteras; la hoja DICCIONARIO las marca "
         f"con 'identifica al estudiante'."),
        ("Metodos de reconocimiento",
         [f"{k}: {v}" for k, v in sorted(conteo_metodo.items())] or ["ninguno"]),
        ("Cobertura",
         [f"{k}: {v}" for k, v in sorted(conteo_situacion.items())] or ["sin registros"]),
        ("Incidencias",
         [f"{k}: {v}" for k, v in sorted(conteo_incidencia.items())] or ["ninguna"]),
        ("Reglas de evaluacion",
         [f"{r['instrumento']}: {r['valor_declarado']} {r['unidad']} "
          f"({r['archivo']}, linea {r['linea']})"
          + (f" — {r['observacion']}" if r["observacion"] else "")
          for r in reglas] or ["no se encontro normativa declarada"]),
        ("Documentos revisados en busca de normativa",
         [f"{n['archivo']}: {n['detalle']}" for n in notas_reglas] or ["ninguno"]),
        ("Registros del aula virtual",
         "no se encontro ningun archivo de registros; no se agrego ninguna columna "
         "de telemetria"
         if not any(i["tipo"] == "archivo_tratado_como_registro_de_actividad"
                    for i in incidencias)
         else "se detecto y se resumio por estudiante; el archivo completo queda "
              "intacto en bases_de_datos"),
        ("Archivos originales sin modificar", "SI" if intactos else "NO — REVISAR"),
        ("Huella de contenido de la hoja BASE", huella),
        ("Archivo generado", str(salida)),
    ]


def _imprimir_resumen(resumen):
    print("\n" + "=" * 70)
    print(" RESUMEN DE CONTROL")
    print("=" * 70)
    for titulo, contenido in resumen:
        print(f"\n{titulo}:")
        if isinstance(contenido, list):
            for linea in contenido:
                print(f"  - {linea}")
        else:
            print(f"  {contenido}")
    print("=" * 70 + "\n")


def main():
    analizador = argparse.ArgumentParser(
        description="Etapa 1 — PREPARAR: organiza e integra una carpeta de materia.")
    analizador.add_argument("carpeta", nargs="?",
                            help="nombre de la carpeta de la materia")
    analizador.add_argument("--raiz", default=".",
                            help="carpeta que contiene a la de la materia")
    analizador.add_argument("--config",
                            default=str(Path(__file__).resolve().parent / "config.json"))
    analizador.add_argument("--aprobados",
                            help="JSON con la lista de archivos aprobados")
    argumentos = analizador.parse_args()

    comprobar_entorno()
    carpeta = argumentos.carpeta or input(
        "Nombre exacto de la carpeta a organizar: ").strip()
    ejecutar(carpeta, argumentos.raiz, argumentos.config, argumentos.aprobados)


if __name__ == "__main__":
    main()
