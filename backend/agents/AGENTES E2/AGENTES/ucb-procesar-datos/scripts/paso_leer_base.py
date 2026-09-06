"""Paso: leer_base

Abre el BASE_INTEGRADA.xlsx que dejo la Etapa 1 y lo convierte en algo con lo que
se pueda trabajar, sin suponer nada sobre la materia.

El programa no sabe que curso esta procesando: no tiene escritos nombres de
columnas, instrumentos ni escalas. Todo lo descubre aqui, leyendo la base y sus
hojas de auditoria.

Si a la base le falta alguna hoja, se sigue adelante sin ella y queda anotado. Lo
que nunca se hace es inventar una columna para tapar el hueco.
"""

import datetime as _dt
import unicodedata

import openpyxl

VACIO, NUMERO, TEXTO, FECHA = "vacio", "numero", "texto", "fecha"


def tipo_de(valor):
    """Que clase de dato es una celda, sin convertirla."""
    if valor is None:
        return VACIO
    if isinstance(valor, bool):
        return TEXTO
    if isinstance(valor, (_dt.datetime, _dt.date, _dt.time)):
        return FECHA
    if isinstance(valor, (int, float)):
        return NUMERO
    texto = str(valor).strip()
    if not texto:
        return VACIO
    try:
        float(texto.replace(",", "."))
        return NUMERO
    except ValueError:
        return TEXTO


def a_numero(valor):
    """Devuelve el valor como numero, o None si no lo es."""
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    if valor is None:
        return None
    try:
        return float(str(valor).strip().replace(",", "."))
    except ValueError:
        return None


def limpiar_texto(valor):
    """Quita caracteres invisibles y espacios sobrantes.

    Los archivos que vienen de una exportacion suelen traer espacios de ancho cero
    o saltos de linea dentro de la celda. No se ven, pero hacen que dos valores
    iguales dejen de serlo.
    """
    if not isinstance(valor, str):
        return valor
    limpio = "".join(c for c in valor
                     if unicodedata.category(c)[0] != "C" or c in "\t")
    return " ".join(limpio.split())


def _hoja_a_tabla(hoja):
    """Convierte una hoja en (columnas, filas), sin tocar los valores."""
    filas = [list(f) for f in hoja.iter_rows(values_only=True)]
    if not filas:
        return [], []
    columnas = [limpiar_texto(c) if isinstance(c, str) else c for c in filas[0]]
    cuerpo = [f for f in filas[1:] if any(tipo_de(v) != VACIO for v in f)]
    ancho = len(columnas)
    cuerpo = [list(f) + [None] * (ancho - len(f)) for f in cuerpo]
    return columnas, [f[:ancho] for f in cuerpo]


def _tabla_a_diccionarios(columnas, filas):
    """La misma tabla, pero como lista de diccionarios."""
    return [{c: f[i] for i, c in enumerate(columnas)} for f in filas]


def leer(ruta, config):
    """Devuelve todo lo que la Etapa 1 dejo, listo para trabajar.

    Estructura devuelta:
      base_columnas / base_filas : la hoja BASE tal cual
      diccionario, cobertura, emparejamientos, incidencias, reglas : listas de dicts
      faltantes : hojas de auditoria que no venian en el archivo
    """
    libro = openpyxl.load_workbook(ruta, data_only=True, read_only=False)
    disponibles = set(libro.sheetnames)

    if "BASE" not in disponibles:
        libro.close()
        raise ValueError("el archivo no tiene una hoja BASE: no parece salido "
                         "de la Etapa 1")

    base_columnas, base_filas = _hoja_a_tabla(libro["BASE"])

    resultado = {
        "base_columnas": base_columnas,
        "base_filas": base_filas,
        "faltantes": [],
    }

    for nombre in ("DICCIONARIO", "COBERTURA", "EMPAREJAMIENTOS",
                   "INCIDENCIAS", "REGLAS_EVALUACION"):
        clave = nombre.lower()
        if nombre not in disponibles:
            resultado[clave] = []
            resultado["faltantes"].append(nombre)
            continue
        columnas, filas = _hoja_a_tabla(libro[nombre])
        resultado[clave] = _tabla_a_diccionarios(columnas, filas)

    # Las columnas que la Etapa 1 dejo plegadas por repetir la identidad. Es la
    # pista mas fiable que existe para el paso de anonimizacion: viene marcada
    # por el programa anterior, no adivinada aqui.
    papeles = set(config["papel_identidad"])
    resultado["columnas_marcadas_identidad"] = {
        d.get("columna_en_base") for d in resultado["diccionario"]
        if d.get("papel") in papeles and d.get("columna_en_base")
    }

    # De donde salio cada columna, para poder explicarlo en el informe.
    resultado["origen_de_columna"] = {
        d.get("columna_en_base"): (d.get("archivo"), d.get("hoja"))
        for d in resultado["diccionario"] if d.get("columna_en_base")
    }

    libro.close()
    return resultado


def columna_clave(base_columnas, base_filas):
    """La columna que identifica a cada fila de forma unica.

    Se prefiere una con valores todos distintos y sin vacios. La Etapa 1 pone el
    codigo de la lista oficial en las primeras columnas, asi que se recorre de
    izquierda a derecha y se toma la primera que cumpla.
    """
    for indice in range(len(base_columnas)):
        valores = [f[indice] for f in base_filas]
        if any(tipo_de(v) == VACIO for v in valores):
            continue
        textos = [str(v).strip() for v in valores]
        if len(set(textos)) == len(textos):
            return indice
    return 0
