"""Skill: leer_documentos

Saca el texto de un documento sin depender de librerias externas.

Un .docx y un .pptx son, por dentro, archivos comprimidos con XML. Se pueden leer
con la biblioteca estandar de Python, asi que el programa no necesita instalar nada
extra para revisar un Word o una presentacion en busca de informacion util.
"""

import re
import zipfile
from pathlib import Path

# El espacio antes de los atributos es obligatorio: sin el, "<w:t[^>]*>"
# tambien matchea <w:tcPr> y <w:tbl>, que son estructura de tabla y no
# texto. Cualquier documento con una tabla salia con XML crudo adentro.
ETIQUETA_TEXTO = re.compile(r"<(?:w|a):t(?: [^>]*)?>(.*?)</(?:w|a):t>",
                            re.DOTALL)
# Un salto de linea suave (Shift+Enter en Word, <w:br/> en el XML) corta la
# linea igual que el final de un parrafo. Word los guarda DENTRO del parrafo, no
# entre parrafos, y quien escribe una lista de ponderaciones casi siempre la
# escribe asi. Sin contarlos, «Examen Parcial 45 puntos» y «Examen Final 45
# puntos» salian pegados en una sola linea, la expresion que busca las reglas ya
# no reconocia ninguna, y el docente se quedaba sin sus ponderaciones sin que
# nada se lo avisara.
FIN_PARRAFO = re.compile(r"</(?:w:p|a:p)>|<(?:w|a):br(?: [^>]*)?/?>")


def _desescapar(texto):
    for entidad, caracter in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                              ("&quot;", '"'), ("&apos;", "'")):
        texto = texto.replace(entidad, caracter)
    return texto


def _texto_de_zip(ruta, partes):
    lineas = []
    with zipfile.ZipFile(ruta) as comprimido:
        nombres = sorted(n for n in comprimido.namelist() if partes(n))
        for nombre in nombres:
            xml = comprimido.read(nombre).decode("utf-8", errors="ignore")
            for parrafo in FIN_PARRAFO.split(xml):
                trozos = [_desescapar(t) for t in ETIQUETA_TEXTO.findall(parrafo)]
                linea = "".join(trozos).strip()
                if linea:
                    lineas.append(linea)
    return lineas


def texto_de_documento(ruta):
    """Devuelve la lista de lineas de texto de un documento, o [] si no se puede."""
    ruta = Path(ruta)
    extension = ruta.suffix.lower()
    try:
        if extension in (".txt", ".md"):
            for codificacion in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    return ruta.read_text(encoding=codificacion).splitlines()
                except (UnicodeDecodeError, ValueError):
                    continue
            return []
        if extension == ".docx":
            return _texto_de_zip(ruta, lambda n: n == "word/document.xml")
        if extension == ".pptx":
            return _texto_de_zip(ruta, lambda n: re.match(r"ppt/slides/slide\d+\.xml$", n))
    except (zipfile.BadZipFile, OSError):
        return []
    return []


def es_legible(ruta):
    return Path(ruta).suffix.lower() in (".txt", ".md", ".docx", ".pptx")
