"""Paso: anonimizar

Reemplaza por un codigo toda columna que contenga nombres o correos, y guarda la
equivalencia en un archivo aparte para que el docente pueda volver atras.

Dos cosas hay que hacer bien aqui, y las dos son faciles de arruinar:

1. NO ALCANZA CON LA COLUMNA DE LA LISTA OFICIAL. La base trae la identidad
   repetida una vez por cada archivo de origen —la Etapa 1 las conserva a
   proposito para poder auditar los cruces—, y basta con que una se escape para
   que la proteccion no sirva de nada.

2. SOLO NOMBRES Y CORREOS. Una fecha con hora ("2026-03-02 08:00:00") es distinta
   en cada fila y tiene dos partes separadas por un espacio, asi que es facil
   confundirla con un nombre. Si se borra, se destruye la evidencia temporal que
   hace falta despues para ver desde cuando alguien dejo de participar. Lo mismo
   con codigos y contadores.

La prueba que separa una cosa de la otra: un nombre de persona es texto casi todo
alfabetico. Una fecha, un codigo o un contador, no.
"""

import re

from paso_leer_base import FECHA, VACIO, limpiar_texto, tipo_de

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.IGNORECASE)
# Una fecha escrita como texto: 2026-03-02, 02/03/2026, 2026-03-02 08:00:00
PATRON_FECHA_TEXTO = re.compile(
    r"^\s*\d{1,4}[-/]\d{1,2}[-/]\d{1,4}([ T]\d{1,2}:\d{2}(:\d{2})?)?\s*$")


def _proporcion_alfabetica(texto):
    """Que parte del texto son letras, ignorando espacios y puntuacion."""
    utiles = [c for c in texto if not c.isspace()]
    if not utiles:
        return 0.0
    return sum(1 for c in utiles if c.isalpha()) / len(utiles)


def parece_nombre_de_persona(valores):
    """True si la columna contiene nombres de personas.

    Se exige que la mayoria de los valores sean texto predominantemente
    alfabetico. Un codigo como 'EST-01' o '2024-1147' no pasa: tiene demasiados
    digitos. Una fecha tampoco.
    """
    muestra = [limpiar_texto(v) for v in valores
               if tipo_de(v) not in (VACIO, FECHA) and isinstance(v, str)]
    muestra = [m for m in muestra if m]
    if len(muestra) < 3:
        return False
    if any(PATRON_FECHA_TEXTO.match(m) for m in muestra):
        return False

    alfabeticos = sum(1 for m in muestra if _proporcion_alfabetica(m) >= 0.85)
    if alfabeticos < len(muestra) * 0.8:
        return False
    # Un nombre tiene al menos dos palabras en la mayoria de los casos, y no se
    # repite igual en todas las filas (eso seria una carrera o un turno).
    distintos = len({m.lower() for m in muestra})
    return distintos >= len(muestra) * 0.8


def parece_correo(valores):
    muestra = [str(v).strip() for v in valores if tipo_de(v) != VACIO]
    if not muestra:
        return False
    return sum(1 for m in muestra if PATRON_CORREO.match(m)) >= len(muestra) * 0.7


def proponer(columnas, filas, marcadas_por_etapa1, indice_clave):
    """Que columnas se van a reemplazar y por que. No modifica nada.

    Devuelve (propuestas, indices), donde cada propuesta explica el motivo para
    que el docente pueda vetarla en la segunda pausa.
    """
    propuestas, indices = [], []

    for indice, nombre in enumerate(columnas):
        valores = [f[indice] for f in filas]
        es_correo = parece_correo(valores)
        es_nombre = parece_nombre_de_persona(valores)
        marcada = nombre in marcadas_por_etapa1

        if not (es_correo or es_nombre):
            continue
        if indice == indice_clave and not (es_correo or es_nombre):
            continue

        if es_correo:
            motivo = "contiene correos electronicos"
        elif marcada:
            motivo = ("la Etapa 1 la marco como columna que identifica al "
                      "estudiante, y su contenido es alfabetico")
        else:
            motivo = "el contenido es texto alfabetico con un valor distinto por fila"

        propuestas.append({
            "columna": nombre,
            "tipo": "correo" if es_correo else "nombre",
            "motivo": motivo,
            "ejemplo": _primer_ejemplo(valores),
        })
        indices.append(indice)

    return propuestas, indices


def _primer_ejemplo(valores):
    """Un valor real de la columna, para que el docente reconozca de cual se habla."""
    for v in valores:
        if tipo_de(v) != VACIO:
            texto = str(v).strip()
            return texto[:34] + ("…" if len(texto) > 34 else "")
    return ""


def aplicar(columnas, filas, indices, indice_clave):
    """Sustituye el contenido de esas columnas por el codigo de cada estudiante.

    El codigo es el de la columna clave de la propia base —el que la Etapa 1 tomo
    de la lista oficial de matricula—, asi que no se inventa ninguna numeracion
    nueva y el docente sigue reconociendo a quien mira.

    Devuelve (filas_nuevas, equivalencia, cambios).
    """
    a_reemplazar = set(indices)
    equivalencia, cambios = [], []
    nuevas = []

    for fila in filas:
        copia = list(fila)
        codigo = str(fila[indice_clave]).strip()
        registro = {"codigo": codigo}
        for indice in a_reemplazar:
            original = fila[indice]
            if tipo_de(original) != VACIO:
                # Se guarda el valor original una sola vez por columna: es lo que
                # permite deshacer la anonimizacion cuando el docente lo necesite.
                registro[columnas[indice]] = limpiar_texto(str(original).strip())
            copia[indice] = codigo
        equivalencia.append(registro)
        nuevas.append(copia)

    for indice in sorted(a_reemplazar):
        cambios.append({
            "columna": columnas[indice],
            "paso": "anonimizar",
            "que_se_hizo": "el contenido se reemplazo por el codigo del estudiante",
            "factor": "",
            "por_que": "protege la identidad sin romper el cruce entre columnas",
        })

    return nuevas, equivalencia, cambios


def columnas_de_equivalencia(equivalencia):
    """Encabezado de la tabla de equivalencia, con el codigo siempre primero."""
    vistas = ["codigo"]
    for registro in equivalencia:
        for clave in registro:
            if clave not in vistas:
                vistas.append(clave)
    return vistas
