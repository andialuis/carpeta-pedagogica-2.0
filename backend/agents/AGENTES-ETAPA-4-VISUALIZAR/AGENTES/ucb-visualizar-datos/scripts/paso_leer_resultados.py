"""Paso: leer_resultados

Abre el RESULTADOS_ANALISIS.xlsx que dejo la Etapa 3 y toma sus cifras tal como
estan.

Este paso tiene una sola regla y es la que define a toda la etapa: NO SE RECALCULA
NADA. Ni un promedio, ni un redondeo distinto, ni un reordenamiento propio. Si el
tablero y el informe dijeran cifras distintas delante de una reunion, el problema no
seria el informe: seria que nadie volveria a creerle a ninguno de los dos.

Si falta el archivo o alguna de sus hojas, el paso se detiene y lo dice. Un tablero
armado a medias con datos improvisados es peor que no tener tablero.
"""

import re
import unicodedata
from pathlib import Path

import openpyxl


def normalizar(texto):
    if texto is None:
        return ""
    plano = unicodedata.normalize("NFKD", str(texto))
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return " ".join(plano.lower().split())


def limpiar_titulo(columna, config):
    """Convierte «[3_evaluaciones] Nota s/15 [sobre 100]» en «Nota sobre 15».

    Quien mira el tablero no tiene por que conocer los archivos del docente. Los
    prefijos entre corchetes son el rastro de que archivo vino la columna: sirven
    para auditar, no para proyectar.
    """
    texto = str(columna or "").strip()
    reglas = config["limpieza_de_titulos"]
    if reglas.get("quitar_prefijo_entre_corchetes") and texto.startswith("["):
        cierre = texto.find("]")
        if cierre != -1:
            texto = texto[cierre + 1:].strip()
    if reglas.get("quitar_sufijo_entre_corchetes"):
        texto = re.sub(r"\s*\[[^\[\]]*\]\s*$", "", texto).strip()
    for viejo, nuevo in reglas.get("reemplazos", {}).items():
        texto = texto.replace(viejo, nuevo)
    return " ".join(texto.split()) or str(columna or "")


def localizar(carpeta, raiz, nombre_archivo):
    rev = Path(raiz) / f"{carpeta}-REV"
    if not rev.is_dir():
        rev = Path(raiz) / carpeta
    bases = rev / "bases_de_datos"
    if not bases.is_dir():
        return None, rev
    candidatos = [c for c in sorted(bases.glob(f"{nombre_archivo}*.xlsx"))
                  if not c.name.startswith("~$")]
    return (candidatos[0] if candidatos else None), rev


def _hoja(libro, nombre):
    if nombre not in libro.sheetnames:
        return []
    filas = list(libro[nombre].iter_rows(values_only=True))
    if not filas:
        return []
    campos = [str(c).strip() if c is not None else f"col_{i}"
              for i, c in enumerate(filas[0])]
    registros = []
    for fila in filas[1:]:
        if all(v is None or str(v).strip() == "" for v in fila):
            continue
        if len(fila) == 1 and str(fila[0]).strip() == "(sin registros)":
            continue
        registros.append({c: v for c, v in zip(campos, fila)})
    return registros


def leer(ruta, config):
    """Devuelve un diccionario con cada hoja del analisis, sin tocar sus valores."""
    libro = openpyxl.load_workbook(ruta, data_only=True)
    datos = {"hojas_presentes": list(libro.sheetnames), "faltantes": []}
    for nombre in config["hojas_esperadas"]:
        datos[nombre] = _hoja(libro, nombre)
        if nombre not in libro.sheetnames:
            datos["faltantes"].append(nombre)
    # Estas dos no son obligatorias, pero si vienen se muestran: son las que dicen
    # que NO se pudo analizar, y ese es el dato mas honesto del tablero.
    for extra in ("NO_SE_PUDO", "COLUMNAS"):
        datos[extra] = _hoja(libro, extra)
    libro.close()
    return datos


def numero(valor, por_defecto=0.0):
    if valor is None:
        return por_defecto
    if isinstance(valor, bool):
        return por_defecto
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        return float(str(valor).strip().replace(",", "."))
    except ValueError:
        return por_defecto


def entero(valor, por_defecto=0):
    return int(numero(valor, por_defecto))


def plural(cantidad, singular, plural_=None):
    """«1 estudiante» y no «1 estudiantes». Un tablero que se equivoca en esto
    parece hecho a las apuradas, y eso contagia desconfianza al resto."""
    cantidad = entero(cantidad)
    if plural_ is None:
        plural_ = singular + "s"
    return f"{cantidad} {singular if cantidad == 1 else plural_}"


def arreglar_plurales(texto):
    """Corrige «1 estudiantes» a «1 estudiante» en los textos que llegan del
    analisis.

    Es un arreglo de escritura, no de datos: no cambia ninguna cifra. Se hace porque
    un tablero que se proyecta y dice «1 estudiantes» parece hecho a las apuradas, y
    esa impresion se contagia a todo lo demas que muestra.
    """
    import re

    def uno(m):
        palabra = m.group(2)
        if palabra.endswith("es"):
            return f"1 {palabra[:-2]}"
        if palabra.endswith("s"):
            return f"1 {palabra[:-1]}"
        return m.group(0)

    return re.sub(r"\b(1) ([a-záéíóúñ]+(?:s|es))\b", uno, str(texto))


def clasificar_veredicto(texto, config):
    """Traduce el veredicto de la hoja HIPOTESIS a confirmada, descartada o sin
    comprobar."""
    plano = normalizar(texto)
    for clase in ("sin_comprobar", "descartada", "confirmada"):
        for marca in config["veredictos"][clase]:
            if normalizar(marca) in plano:
                return clase
    return "sin_comprobar"


def comprobar(datos, config):
    """Devuelve los motivos por los que NO se puede construir el tablero."""
    problemas = []
    obligatorias = ["HALLAZGOS", "ACCIONES", "PRIORIDADES"]
    for nombre in obligatorias:
        if nombre in datos["faltantes"]:
            problemas.append(f"falta la hoja {nombre} en el archivo de resultados")
    if not any(datos.get(n) for n in config["hojas_esperadas"]):
        problemas.append("el archivo de resultados esta vacio")
    return problemas
