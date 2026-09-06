"""Skill: descubrir_reglas

Busca en los documentos aprobados la informacion normativa de la materia:
ponderaciones, puntajes y escalas. La transcribe tal como esta.

No aplica nada. No convierte escalas ni calcula notas: eso pertenece a la etapa
siguiente. Si encuentra una contradiccion, la reporta sin resolverla.
"""

import re

from skill_identidad import normalizar
from skill_leer_documentos import es_legible, texto_de_documento

PATRON_ESCALA = re.compile(
    r"(?<![0-9/])(?:s/|sobre\s+|/)\s*(\d+(?:[.,]\d+)?)(?![/0-9])", re.IGNORECASE)


PATRON_ITEM_DE_LISTA = re.compile(r"^\s*\d+\s*[.)]")


def _es_regla_plausible(instrumento):
    """Descarta lineas que parecen una regla pero son otra cosa.

    Una lista de notas ("3. <apellido>, <nombre> - 82") o un encabezado
    ("Escala: sobre 100") terminan en numero igual que una ponderacion, pero no lo
    son. Se distinguen por la coma, los dos puntos y la numeracion de lista.
    """
    if not instrumento or not any(c.isalpha() for c in instrumento):
        return False
    if len(instrumento.split()) > 6:
        return False
    if "," in instrumento or ":" in instrumento:
        return False
    if PATRON_ITEM_DE_LISTA.match(instrumento):
        return False
    return True


def _valor_plausible(valor, unidad):
    """Un numero sin unidad y mayor a 100 no es un puntaje: suele ser un año."""
    try:
        numero = float(valor)
    except ValueError:
        return False
    if unidad in ("puntos", "punto", "pts", "pt", "%"):
        return True
    return numero <= 100


def descubrir(documentos_aprobados, config):
    """Devuelve (reglas, notas_del_hallazgo)."""
    patron = re.compile(config["patron_regla_evaluacion"])
    reglas, notas = [], []

    for documento in sorted(documentos_aprobados, key=lambda p: p.name):
        if not es_legible(documento):
            notas.append({
                "archivo": documento.name,
                "detalle": "formato no legible como texto; no se busco normativa",
            })
            continue

        lineas = texto_de_documento(documento)
        encontradas = 0
        for numero, linea in enumerate(lineas, start=1):
            if not linea.strip():
                continue
            coincidencia = patron.match(linea)
            if not coincidencia:
                continue
            instrumento = coincidencia.group("instrumento").strip()
            unidad = (coincidencia.group("unidad") or "").lower()
            if not _es_regla_plausible(instrumento):
                continue
            if not _valor_plausible(coincidencia.group("valor").replace(",", "."), unidad):
                continue
            reglas.append({
                "instrumento": instrumento,
                "valor_declarado": coincidencia.group("valor").replace(",", "."),
                "unidad": (coincidencia.group("unidad") or "puntos").lower(),
                "archivo": documento.name,
                "linea": numero,
                "texto_original": linea.strip(),
            })
            encontradas += 1

        notas.append({
            "archivo": documento.name,
            "detalle": f"{encontradas} regla(s) de evaluacion encontrada(s)",
        })

    return reglas, notas


def escala_de_columna(nombre_columna):
    """Extrae la escala escrita en el titulo de una columna: 's/15', 'sobre 100'."""
    coincidencia = PATRON_ESCALA.search(str(nombre_columna))
    return coincidencia.group(1).replace(",", ".") if coincidencia else None


PATRON_ORDINAL = re.compile(r"(\d+)\s*(?:er|do|da|ro|ra|to|ta|vo|va|mo|ma)?\s*(?=[a-z])")


ORDINALES = {"primer": "1", "primero": "1", "primera": "1",
             "segundo": "2", "segunda": "2",
             "tercer": "3", "tercero": "3", "tercera": "3",
             "cuarto": "4", "cuarta": "4", "quinto": "5", "quinta": "5"}

VACIAS = {"de", "del", "la", "el", "los", "las", "en", "por", "para", "con",
          "que", "una", "uno", "sus", "sobre"}


def _raiz(palabra):
    """Reduce singular y plural a una misma raiz.

    En castellano el plural agrega 's' despues de vocal ('avance/avances') y 'es'
    despues de consonante ('examen/examenes'). Quitando primero la 's' final y
    despues la 'e' final, las dos formas caen en la misma raiz sin necesidad de
    saber cual era el singular.
    """
    if len(palabra) > 4 and palabra.endswith("s"):
        palabra = palabra[:-1]
    if len(palabra) > 4 and palabra.endswith("e"):
        palabra = palabra[:-1]
    return palabra


def _palabras(texto):
    """Palabras significativas, con los ordinales reducidos a su numero y sin plural.

    '1er Parcial' y '2doParcial' quedan como {1, parcial} y {2, parcial}, para que
    se puedan comparar con el titulo de la columna sin importar como se escribieron.
    """
    normalizado = re.sub(r"[.@_]", " ",
                         PATRON_ORDINAL.sub(r"\1 ", normalizar(texto)))
    palabras = set()
    for palabra in normalizado.split():
        palabra = ORDINALES.get(palabra, palabra)
        if palabra in VACIAS:
            continue
        if len(palabra) > 2 or palabra.isdigit():
            palabras.add(_raiz(palabra))
    return palabras


def anclar_a_columnas(reglas, diccionario):
    """Relaciona cada regla con las columnas de la base que parecen medirla.

    Solo describe la relacion y senala diferencias de escala. No convierte nada.
    Se compara contra el nombre de la hoja y el titulo original de la columna, no
    contra el nombre del archivo: si no, cualquier columna de un archivo llamado
    'asistencia' pareceria medir la asistencia.
    """
    anclajes = []
    for regla in reglas:
        palabras = _palabras(regla["instrumento"])
        candidatas, por_hoja, por_archivo, parciales = [], [], [], []
        for entrada in diccionario:
            if not palabras:
                continue
            en_columna = _palabras(entrada["columna_original"])
            con_hoja = _palabras(f"{entrada['hoja']} {entrada['columna_original']}")
            con_archivo = _palabras(f"{entrada['archivo']} {entrada['hoja']} "
                                    f"{entrada['columna_original']}")
            if palabras <= en_columna:
                candidatas.append(entrada["columna_en_base"])
            elif palabras <= con_hoja:
                por_hoja.append(entrada["hoja"])
            elif palabras <= con_archivo:
                por_archivo.append(entrada["archivo"])
            elif len(palabras) >= 3 and len(palabras & con_hoja) >= len(palabras) - 1:
                parciales.append(entrada["hoja"])

        nivel = "el titulo de la columna"
        if not candidatas and por_hoja:
            # El instrumento no da nombre a ninguna columna, pero si a una hoja entera
            # (por ejemplo, una planilla de asistencia con una columna por fecha).
            candidatas = [f"(toda la hoja '{h}')" for h in sorted(set(por_hoja))]
            nivel = "el nombre de la hoja"
        elif not candidatas and por_archivo:
            candidatas = [f"(todo el archivo '{a}')" for a in sorted(set(por_archivo))]
            nivel = "el nombre del archivo"
        elif not candidatas and parciales:
            candidatas = [f"(hoja '{h}', coincidencia parcial)"
                          for h in sorted(set(parciales))]
            nivel = "parecido parcial del nombre"

        escalas = {escala_de_columna(c) for c in candidatas}
        escalas.discard(None)
        observacion = ""
        if not candidatas:
            observacion = "no se encontro una columna que corresponda a este instrumento"
        elif nivel != "el titulo de la columna":
            observacion = f"vinculado por {nivel}: confirmar que corresponde"
        elif escalas and regla["valor_declarado"] not in escalas:
            observacion = (f"el documento declara {regla['valor_declarado']} "
                           f"{regla['unidad']} y la planilla usa escala "
                           f"{'/'.join(sorted(escalas))}: revisar antes de convertir")

        anclajes.append({
            **regla,
            "columnas_relacionadas": " | ".join(candidatas) if candidatas else "",
            "escala_en_planilla": "/".join(sorted(escalas)) if escalas else "",
            "observacion": observacion,
        })
    return anclajes
