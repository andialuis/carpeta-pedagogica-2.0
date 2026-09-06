"""Paso: imputar_vacios

Cuenta los huecos y explica de que tipo es cada uno. Casi nunca los rellena, y
nunca con cero.

La regla que gobierna todo este paso:

    Un cero significa que el estudiante rindio y no obtuvo puntaje.
    Un vacio significa que no hay dato.

Son dos hechos distintos y confundirlos falsea el semestre entero: quien no rindio
pasa a parecer alguien que rindio pesimo, y el promedio de la materia baja por una
decision que nadie tomo. Por eso una casilla de nota vacia se queda vacia.

En las columnas de texto si se puede escribir 'Sin registro': ahi no hay ninguna
media que contaminar.

Para distinguir dos vacios que parecen iguales se usa la hoja COBERTURA, que
produjo la Etapa 1:

    'encontrado_vacio'  el estudiante figura en el archivo, con la celda en blanco
    'ausente'           el estudiante no figura en ese archivo

El primero suele ser un no rindio. El segundo suele ser un no estaba. La diferencia
importa y esta etapa la conserva en vez de aplanarla.
"""

from paso_leer_base import NUMERO, VACIO, tipo_de


def _situaciones_por_estudiante(cobertura):
    """{codigo: {archivo: situacion}} a partir de la hoja COBERTURA."""
    mapa = {}
    for registro in cobertura:
        codigo = str(registro.get("id_estudiante", "") or "").strip()
        archivo = str(registro.get("archivo", "") or "").strip()
        situacion = str(registro.get("situacion", "") or "").strip()
        if codigo and archivo:
            mapa.setdefault(codigo, {})[archivo] = situacion
    return mapa


def _archivo_de_columna(nombre, origen_de_columna, etiquetas_conocidas=()):
    """De que archivo vino esa columna, segun el DICCIONARIO de la Etapa 1.

    La Etapa 1 rotula la cobertura con la etiqueta de la fuente, que incluye la
    hoja **solo cuando el libro tenia varias**. Un CSV o un Excel de una sola
    hoja se rotula con el nombre del archivo a secas. Aqui se armaba siempre la
    forma compuesta, asi que «asistencia · asistencia» no encontraba a
    «asistencia» y todos sus vacios caian en «sin clasificar»: en una materia
    normal eso son la mayoria de los huecos, y el docente perdia justo la
    distincion que esta hoja existe para darle. Se prueban las dos formas y se
    devuelve la que la cobertura conoce.
    """
    dato = origen_de_columna.get(nombre)
    if not dato:
        return None
    archivo, hoja = dato
    if not archivo:
        return None
    base = str(archivo).rsplit(".", 1)[0]
    if not (hoja and str(hoja).strip()):
        return base
    compuesta = f"{base} · {hoja}"
    conocidas = set(etiquetas_conocidas)
    if not conocidas or compuesta in conocidas:
        return compuesta
    return base if base in conocidas else compuesta


def revisar(columnas, filas, indice_clave, cobertura, origen_de_columna, config,
            columnas_derivadas=()):
    """Cuenta los vacios por columna y los clasifica. Devuelve (resumen, cambios).

    Solo se rellena texto. Las columnas numericas se cuentan y se dejan como estan.

    Las columnas que esta etapa creo se omiten: sus huecos son exactamente los del
    original del que derivan, y ademas la hoja COBERTURA no las conoce, asi que
    saldrian todas como 'sin clasificar' ensuciando el recuento.
    """
    derivadas = set(columnas_derivadas)
    situaciones = _situaciones_por_estudiante(cobertura)
    etiquetas_de_cobertura = {etiqueta for porestudiante in situaciones.values()
                              for etiqueta in porestudiante}
    texto_vacio = config["texto_vacio"]
    resumen, cambios = [], []

    for indice, nombre in enumerate(columnas):
        if nombre in derivadas:
            continue
        crudos = [f[indice] for f in filas]
        tipos = [tipo_de(v) for v in crudos]
        vacios = [i for i, t in enumerate(tipos) if t == VACIO]
        if not vacios:
            continue

        con_dato = [t for t in tipos if t != VACIO]
        if not con_dato:
            # La columna esta entera vacia: no hay nada que clasificar y escribir
            # 'Sin registro' en ella solo inventaria contenido donde no hay dato.
            resumen.append({
                "columna": nombre, "tipo_de_columna": "sin datos",
                "vacios": len(vacios), "figura_pero_sin_dato": 0,
                "no_figura_en_el_archivo": 0, "sin_clasificar": len(vacios),
                "que_se_hizo": "se dejo vacia: la columna no trae ningun dato",
            })
            continue
        es_numerica = sum(1 for t in con_dato if t == NUMERO) >= len(con_dato) * 0.8

        etiqueta_archivo = _archivo_de_columna(nombre, origen_de_columna,
                                               etiquetas_de_cobertura)
        figura_sin_dato = no_figura = sin_clasificar = 0

        for i in vacios:
            codigo = str(filas[i][indice_clave]).strip()
            situacion = None
            if etiqueta_archivo:
                situacion = situaciones.get(codigo, {}).get(etiqueta_archivo)
            if situacion == "encontrado_vacio":
                figura_sin_dato += 1
            elif situacion == "ausente":
                no_figura += 1
            else:
                sin_clasificar += 1

        resumen.append({
            "columna": nombre,
            "tipo_de_columna": "numerica" if es_numerica else "texto",
            "vacios": len(vacios),
            "figura_pero_sin_dato": figura_sin_dato,
            "no_figura_en_el_archivo": no_figura,
            "sin_clasificar": sin_clasificar,
            "que_se_hizo": ("se dejaron vacios" if es_numerica
                            else f"se escribio '{texto_vacio}'"),
        })

        if not es_numerica:
            for i in vacios:
                filas[i][indice] = texto_vacio
            cambios.append({
                "columna": nombre,
                "paso": "vacios",
                "que_se_hizo": f"{len(vacios)} celda(s) de texto vacias pasaron a "
                               f"'{texto_vacio}'",
                "factor": "",
                "por_que": "en texto no hay promedio que contaminar",
            })

    return resumen, cambios
