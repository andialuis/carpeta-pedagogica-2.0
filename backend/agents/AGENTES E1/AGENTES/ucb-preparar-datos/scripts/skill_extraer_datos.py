"""Skill: extraer_datos

Rescata los datos atrapados en archivos que este programa no sabe abrir —una foto
con notas escritas a mano, un acta en PDF— y los convierte en una hoja de datos
dentro de bases_de_datos.

ESTE PROGRAMA NO LEE IMAGENES NI PDF, y es deliberado: si dependiera de una
libreria de OCR o de lectura de PDF, la base saldria distinta segun lo que cada
computadora tenga instalado, y eso rompe R5 (mismo resultado en cualquier maquina).

Quien lee es el AGENTE, que si puede ver. El reparto es el mismo para los dos
formatos:

  1. Si existe '<archivo>_transcripcion_asistida.xlsx', se usa como fuente de datos
     y queda registrado con su origen.
  2. Si el archivo trae normativa en vez de calificaciones, el agente la vuelca a
     '<archivo>_transcripcion_asistida.txt' y de ahi se leen las reglas.
  3. Si no existe ninguna de las dos, se genera una plantilla
     PENDIENTE_TRANSCRIPCION y el programa CONTINUA. No se detiene por esto.
  4. El agente lee el archivo, llena la plantilla con su nivel de confianza, se la
     hace confirmar al docente y se vuelve a ejecutar el programa.

En ningun caso el resultado de una lectura queda escrito dentro de este programa.
"""

import re
from pathlib import Path

import openpyxl

from skill_leer_documentos import es_legible, texto_de_documento

SUFIJO_ASISTIDA = "_transcripcion_asistida.xlsx"
SUFIJO_ASISTIDA_TEXTO = "_transcripcion_asistida.txt"
SUFIJO_PENDIENTE = "_PENDIENTE_TRANSCRIPCION.xlsx"
SUFIJO_DOCUMENTO = "_extraido_de_documento.xlsx"

# "3. <apellido> <apellido>, <nombre> - 88"  o  "7) <apellido> <nombre>: 64"
PATRON_LISTA_DE_NOTAS = re.compile(
    r"^\s*\d+\s*[.)]\s*(?P<identidad>[^\d]{4,70}?)\s*[-–—:]\s*"
    r"(?P<valor>\d+(?:[.,]\d+)?)\s*$")
PATRON_ESCALA = re.compile(r"sobre\s+(\d+)|s/\s*(\d+)", re.IGNORECASE)
MINIMO_FILAS = 5


def _crear_plantilla(ruta_origen, carpeta_destino, etiqueta="identidad_en_imagen"):
    salida = carpeta_destino / (ruta_origen.stem + SUFIJO_PENDIENTE)
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.title = "PENDIENTE"
    hoja.append([etiqueta, "valor", "archivo_origen", "confianza", "origen"])
    hoja.append(["", "", ruta_origen.name, "", "transcripcion_pendiente"])
    libro.save(salida)
    return salida


def procesar_documentos(documentos_aprobados, carpeta_bases):
    """Rescata listas de notas escritas dentro de un documento de texto o Word.

    Muchos docentes anotan las calificaciones de una defensa o un laboratorio en un
    documento, no en una planilla. Si esos datos se quedan ahi, no entran a la base.
    """
    fuentes, incidencias = [], []

    for documento in sorted(documentos_aprobados, key=lambda p: p.name):
        if not es_legible(documento):
            continue

        lineas = texto_de_documento(documento)
        registros = []
        for linea in lineas:
            coincidencia = PATRON_LISTA_DE_NOTAS.match(linea)
            if coincidencia:
                registros.append((coincidencia.group("identidad").strip(),
                                  coincidencia.group("valor").replace(",", ".")))
        if len(registros) < MINIMO_FILAS:
            continue

        escala = None
        for linea in lineas:
            hallada = PATRON_ESCALA.search(linea)
            if hallada:
                escala = hallada.group(1) or hallada.group(2)
                break
        titulo_valor = f"Nota (sobre {escala})" if escala else "Valor registrado"

        salida = carpeta_bases / (documento.stem + SUFIJO_DOCUMENTO)
        libro = openpyxl.Workbook()
        hoja = libro.active
        hoja.title = documento.stem[:31]
        hoja.append(["identidad_en_documento", titulo_valor, "archivo_origen", "origen"])
        for identidad, valor in registros:
            numero = float(valor)
            hoja.append([identidad, int(numero) if numero.is_integer() else numero,
                         documento.name, "extraido_de_documento"])
        libro.save(salida)

        fuentes.append(salida)
        incidencias.append({
            "tipo": "datos_rescatados_de_documento",
            "archivo": documento.name,
            "detalle": f"se encontraron {len(registros)} registros con valor numerico; "
                       f"se guardaron en '{salida.name}'"
                       + (f" (escala detectada: sobre {escala})" if escala else ""),
        })

    return fuentes, incidencias


def procesar_para_transcripcion(rutas_aprobadas, carpeta_bases):
    """Imagenes y PDF: los archivos que solo puede leer el agente.

    Devuelve (fuentes_nuevas, textos_nuevos, incidencias):
      fuentes_nuevas: hojas de datos listas para integrarse a la base;
      textos_nuevos : transcripciones en texto, para buscarles normativa.
    """
    fuentes, textos, incidencias = [], [], []

    for origen in sorted(rutas_aprobadas, key=lambda p: p.name):
        es_pdf = origen.suffix.lower() == ".pdf"
        tipo_legible = "PDF" if es_pdf else "imagenes"
        etiqueta = "identidad_en_pdf" if es_pdf else "identidad_en_imagen"

        asistida = carpeta_bases / (origen.stem + SUFIJO_ASISTIDA)
        asistida_texto = carpeta_bases / (origen.stem + SUFIJO_ASISTIDA_TEXTO)
        pendiente = carpeta_bases / (origen.stem + SUFIJO_PENDIENTE)

        transcrito = False
        if asistida.exists():
            fuentes.append(asistida)
            incidencias.append({
                "tipo": "pdf_transcrito" if es_pdf else "imagen_transcrita",
                "archivo": origen.name,
                "detalle": f"se usa la transcripcion asistida '{asistida.name}'; "
                           f"revisar la columna de confianza",
            })
            transcrito = True

        if asistida_texto.exists():
            textos.append(asistida_texto)
            incidencias.append({
                "tipo": "normativa_transcrita",
                "archivo": origen.name,
                "detalle": f"se leyeron las reglas de evaluacion desde "
                           f"'{asistida_texto.name}'",
            })
            transcrito = True

        if transcrito:
            if pendiente.exists():
                pendiente.unlink()        # ya fue transcrito: la plantilla sobra
            continue

        plantilla = _crear_plantilla(origen, carpeta_bases, etiqueta)
        incidencias.append({
            "tipo": ("pdf_pendiente_de_transcripcion" if es_pdf
                     else "imagen_pendiente_de_transcripcion"),
            "archivo": origen.name,
            "detalle": (f"este programa no lee {tipo_legible}; le toca al agente. Se "
                        f"genero la plantilla '{plantilla.name}'. Si el archivo trae "
                        f"CALIFICACIONES, llenala, marca la confianza por fila, hazla "
                        f"confirmar al docente y guardala como "
                        f"'{origen.stem}{SUFIJO_ASISTIDA}'. Si trae NORMATIVA "
                        f"(ponderaciones, escalas), copia su texto a "
                        f"'{origen.stem}{SUFIJO_ASISTIDA_TEXTO}'. Despues vuelve a "
                        f"ejecutar el programa"),
        })

    return fuentes, textos, incidencias
