"""Skill: leer_planillas

Lee cada hoja de un libro de Excel reconstruyendo el encabezado real, aunque este
repartido en varias filas y con celdas combinadas.

Dos decisiones importantes:

1. Las celdas combinadas se propagan a todas las celdas del rango, de modo que una
   fecha que encabeza dos columnas quede asociada a las dos.

2. Donde termina el encabezado se decide por CONSISTENCIA DE TIPOS: se prueba cada
   fila de inicio posible y se elige la que deja las columnas de datos mas
   homogeneas (todas numero, todas texto o todas fecha). Es un criterio que no
   depende del idioma ni del contenido, asi que sirve para cualquier materia.

Los valores se devuelven tal como vienen. No se convierten fechas ni numeros: eso
corresponde a la etapa siguiente.
"""

import datetime as _dt
from string import ascii_uppercase

import openpyxl

NUMERO, TEXTO, FECHA, VACIO = "numero", "texto", "fecha", "vacio"


def _tipo(valor):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return VACIO
    if isinstance(valor, bool):
        return TEXTO
    if isinstance(valor, (_dt.datetime, _dt.date, _dt.time)):
        return FECHA
    if isinstance(valor, (int, float)):
        return NUMERO
    if isinstance(valor, str):
        try:
            float(valor.strip().replace(",", "."))
            return NUMERO
        except ValueError:
            return TEXTO
    return TEXTO


def _letra_columna(indice):
    letra = ""
    indice += 1
    while indice:
        indice, resto = divmod(indice - 1, 26)
        letra = ascii_uppercase[resto] + letra
    return letra


def _texto_encabezado(valor):
    if isinstance(valor, _dt.datetime):
        if (valor.hour, valor.minute, valor.second) == (0, 0, 0):
            return valor.strftime("%Y-%m-%d")
        return valor.strftime("%Y-%m-%d %H:%M")
    if isinstance(valor, _dt.date):
        return valor.strftime("%Y-%m-%d")
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def _grilla_con_combinadas(hoja):
    """Matriz de valores con las celdas combinadas propagadas.

    Devuelve tambien el 'piso' del encabezado: si una fila tiene celdas combinadas
    en horizontal (un mes que abarca cuatro clases, una fecha que abarca asistencia
    y participacion), esa fila agrupa a otra que va debajo, asi que el encabezado
    tiene por fuerza mas de una fila. Es la unica pista fiable cuando la planilla
    es toda de texto y la consistencia de tipos no distingue nada.
    """
    grilla = [[celda.value for celda in fila] for fila in hoja.iter_rows()]
    piso = 1
    for rango in hoja.merged_cells.ranges:
        valor = hoja.cell(row=rango.min_row, column=rango.min_col).value
        if rango.max_col > rango.min_col and rango.max_row <= 3:
            piso = max(piso, rango.max_row + 1)
        for fila in range(rango.min_row, rango.max_row + 1):
            for col in range(rango.min_col, rango.max_col + 1):
                grilla[fila - 1][col - 1] = valor

    vacias_arriba = 0
    for fila in grilla:
        if any(_tipo(v) != VACIO for v in fila):
            break
        vacias_arriba += 1
    return _recortar(grilla), max(1, piso - vacias_arriba)


def _recortar(grilla):
    """Quita filas y columnas totalmente vacias en los bordes."""
    filas = [f for f in grilla if any(_tipo(v) != VACIO for v in f)]
    if not filas:
        return []
    ancho = max(len(f) for f in filas)
    filas = [list(f) + [None] * (ancho - len(f)) for f in filas]
    ultimas = [c for c in range(ancho)
               if any(_tipo(f[c]) != VACIO for f in filas)]
    if not ultimas:
        return []
    limite = max(ultimas) + 1
    return [f[:limite] for f in filas]


def _consistencia(grilla, inicio_datos):
    """Que tan homogeneas quedan las columnas si los datos empiezan en esa fila."""
    cuerpo = grilla[inicio_datos:]
    if not cuerpo:
        return 0.0
    puntajes = []
    for col in range(len(grilla[0])):
        tipos = [_tipo(fila[col]) for fila in cuerpo]
        tipos = [t for t in tipos if t != VACIO]
        if not tipos:
            puntajes.append(1.0)
            continue
        dominante = max(tipos.count(t) for t in set(tipos))
        puntajes.append(dominante / len(tipos))
    return sum(puntajes) / len(puntajes)


def _elegir_inicio_datos(grilla, maximo, piso=1):
    tope = min(maximo, len(grilla) - 1)
    piso = min(piso, max(tope, 1))
    mejor_inicio, mejor_puntaje = piso, -1.0
    for inicio in range(piso, max(tope, piso) + 1):
        puntaje = _consistencia(grilla, inicio)
        if puntaje > mejor_puntaje + 1e-9:      # empate -> gana el encabezado corto
            mejor_inicio, mejor_puntaje = inicio, puntaje
    return mejor_inicio


def _nombres_columnas(grilla, inicio_datos):
    nombres = []
    for col in range(len(grilla[0])):
        partes = []
        for fila in range(inicio_datos):
            valor = grilla[fila][col]
            if _tipo(valor) == VACIO:
                continue
            texto = _texto_encabezado(valor)
            if texto and (not partes or partes[-1] != texto):
                partes.append(texto)
        nombre = "_".join(partes).strip()
        if not nombre:
            nombre = f"columna_sin_titulo_{_letra_columna(col)}"
        nombres.append(nombre)

    # Ninguna columna puede quedar con el mismo nombre que otra.
    vistos = {}
    finales = []
    for nombre in nombres:
        if nombre in vistos:
            vistos[nombre] += 1
            finales.append(f"{nombre}_{vistos[nombre]}")
        else:
            vistos[nombre] = 1
            finales.append(nombre)
    return finales


def leer_hoja(hoja, max_filas_encabezado):
    grilla, piso = _grilla_con_combinadas(hoja)
    if not grilla:
        return None
    inicio = _elegir_inicio_datos(grilla, max_filas_encabezado, piso)
    columnas = _nombres_columnas(grilla, inicio)
    filas = [list(f) for f in grilla[inicio:]
             if any(_tipo(v) != VACIO for v in f)]
    return {
        "hoja": hoja.title,
        "columnas": columnas,
        "filas": filas,
        "filas_encabezado": inicio,
    }


def _formulas_sin_valor(hoja_valores, hoja_formulas):
    """Celdas con formula cuyo resultado NO quedo guardado dentro del archivo.

    Este programa no calcula formulas: lee el ultimo resultado que Excel dejo
    guardado en el archivo. Si la planilla se genero por programa, se exporto de
    un sistema o nunca se abrio en Excel, ese resultado no existe y la celda llega
    vacia. Sin este aviso, una columna 'Promedio' entera entraria en blanco a la
    base y nadie se enteraria: es la unica forma en que se podria perder un dato
    en silencio.

    Devuelve {letra_de_columna: cuantas celdas}.
    """
    afectadas = {}
    for fila in hoja_formulas.iter_rows():
        for celda in fila:
            valor = celda.value
            if not isinstance(valor, str) or not valor.startswith("="):
                continue
            guardado = hoja_valores.cell(row=celda.row, column=celda.column).value
            if guardado is None:
                afectadas[celda.column_letter] = afectadas.get(
                    celda.column_letter, 0) + 1
    return afectadas


def leer_libro(ruta, max_filas_encabezado):
    """Todas las hojas del libro, en orden alfabetico estable."""
    libro = openpyxl.load_workbook(ruta, data_only=True, read_only=False)
    try:
        formulas = openpyxl.load_workbook(ruta, data_only=False, read_only=False)
    except Exception:                      # noqa: BLE001 - si falla, se sigue igual
        formulas = None

    resultado = []
    for titulo in sorted(libro.sheetnames):
        leida = leer_hoja(libro[titulo], max_filas_encabezado)
        if leida and leida["filas"]:
            leida["calculadas_sin_valor"] = (
                _formulas_sin_valor(libro[titulo], formulas[titulo])
                if formulas is not None and titulo in formulas.sheetnames else {})
            resultado.append(leida)
    libro.close()
    if formulas is not None:
        formulas.close()
    return resultado


def leer_csv(ruta, max_filas_encabezado):
    """Un CSV o TSV se trata igual que una hoja: misma deteccion de encabezado."""
    import csv

    texto = None
    for codificacion in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            texto = ruta.read_text(encoding=codificacion)
            break
        except (UnicodeDecodeError, ValueError):
            continue
    if texto is None:
        return []

    muestra = "\n".join(texto.splitlines()[:20])
    try:
        dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t|")
        separador = dialecto.delimiter
    except csv.Error:
        separador = "\t" if ruta.suffix.lower() == ".tsv" else ","

    filas = [f for f in csv.reader(texto.splitlines(), delimiter=separador) if f]
    grilla = _recortar(filas)
    if not grilla:
        return []
    inicio = _elegir_inicio_datos(grilla, max_filas_encabezado)
    return [{
        "hoja": ruta.stem,
        "columnas": _nombres_columnas(grilla, inicio),
        "filas": [list(f) for f in grilla[inicio:]
                  if any(_tipo(v) != VACIO for v in f)],
        "filas_encabezado": inicio,
    }]


def leer_fuente(ruta, max_filas_encabezado):
    """Lee una planilla, sea Excel o texto separado por comas."""
    if ruta.suffix.lower() in (".csv", ".tsv", ".txt", ".md"):
        return leer_csv(ruta, max_filas_encabezado)
    return leer_libro(ruta, max_filas_encabezado)
