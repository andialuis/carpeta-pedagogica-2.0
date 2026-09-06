"""Paso: comparar_instrumentos

Compara como le fue a cada estudiante en las evaluaciones que rindio vigilado
—parciales, laboratorios, examenes presenciales— y en las que hizo por su cuenta
—tareas, trabajos, cuestionarios en linea—.

Y no mira solo la nota. Si la base trae cuanto tardo cada uno o a que hora
empezo, tambien lo mira: una nota altisima obtenida en una fraccion del tiempo
que tardaron los demas, o varios estudiantes que empiezan con segundos de
diferencia entre ellos, dicen algo que el promedio no dice.

R5 manda aqui mas que en ningun otro paso: esto DESCRIBE, no acusa. Se presenta
la evidencia y se dice quien deberia revisarla. La conclusion sobre una persona
la toma el docente.
"""

from estadistica import media, normalizar_0_1, z
from paso_leer_depurada import (DURACION, MOMENTO, NOTA, a_momento, a_numero,
                                de_papel, normalizar, serie)


def _clasificar_instrumentos(fichas, config):
    """Reparte las columnas de calificacion en vigiladas y no vigiladas."""
    palabras = config["palabras"]
    vigilados, libres, sin_clasificar = [], [], []
    for ficha in fichas:
        if ficha["papel"] != NOTA:
            continue
        plano = normalizar(ficha["columna"])
        es_vigilado = any(p in plano for p in palabras["vigilado"])
        es_libre = any(p in plano for p in palabras["no_vigilado"])
        if es_vigilado and not es_libre:
            vigilados.append(ficha)
        elif es_libre and not es_vigilado:
            libres.append(ficha)
        else:
            sin_clasificar.append(ficha)
    return vigilados, libres, sin_clasificar


def _promedio_normalizado(filas, fichas_grupo):
    """Promedio 0-1 por estudiante sobre un conjunto de instrumentos."""
    if not fichas_grupo:
        return [None] * len(filas)
    columnas = [normalizar_0_1(serie(filas, f["indice"])) for f in fichas_grupo]
    salida = []
    for numero in range(len(filas)):
        valores = [c[numero] for c in columnas if c[numero] is not None]
        salida.append(round(sum(valores) / len(valores), 4) if valores else None)
    return salida


def _revisar_tiempos(columnas, filas, fichas, clave, config):
    """Casos donde el tiempo empleado no cuadra con la nota obtenida."""
    indices = de_papel(fichas, DURACION)
    casos = []
    for indice in indices:
        tiempos = serie(filas, indice)
        con_dato = [t for t in tiempos if t is not None]
        if len(con_dato) < config["minimo_datos_para_estadistica"]:
            continue
        tipico = sorted(con_dato)[len(con_dato) // 2]
        if tipico <= 0:
            continue
        limite = tipico * config["proporcion_tiempo_sospechoso"]
        for fila, tiempo in zip(filas, tiempos):
            if tiempo is None or tiempo > limite:
                continue
            casos.append({
                "codigo": str(fila[clave]).strip(),
                "columna": columnas[indice],
                "cifra": f"{tiempo:g} frente a {tipico:g} del resto del curso",
                "que_se_observa": "resolvio en menos de la mitad del tiempo "
                                  "habitual del curso",
            })
    return casos


def _revisar_horas(columnas, filas, fichas, clave, config):
    """Estudiantes que empezaron una misma evaluacion casi al mismo segundo.

    Solo se miran las columnas que dicen ser hora de INICIO de una prueba. Antes
    se miraba cualquier columna con fechas, y eso incluia el «primer registro»
    del aula virtual: tres personas que entraron a la plataforma con segundos de
    diferencia no significan nada, y el informe lo reportaba como si fuera un
    hallazgo. Un falso positivo aqui es especialmente caro, porque señala a
    personas concretas.
    """
    palabras = config["palabras"]["hora_inicio"]
    indices = [f["indice"] for f in fichas
               if f["papel"] == MOMENTO
               and any(p in normalizar(f["columna"]) for p in palabras)]
    casos = []
    for indice in indices:
        momentos = []
        for fila in filas:
            valor = a_momento(fila[indice])
            if valor is not None:
                momentos.append((valor, str(fila[clave]).strip()))
        if len(momentos) < 3:
            continue
        momentos.sort()
        margen = config["umbral_hora_sospechosa_segundos"]
        bloque = [momentos[0]]
        for actual in momentos[1:]:
            if (actual[0] - bloque[-1][0]).total_seconds() <= margen:
                bloque.append(actual)
                continue
            if len(bloque) >= 3:
                casos.append(_caso_de_bloque(columnas[indice], bloque, margen))
            bloque = [actual]
        if len(bloque) >= 3:
            casos.append(_caso_de_bloque(columnas[indice], bloque, margen))
    return casos


def _caso_de_bloque(columna, bloque, margen):
    codigos = ", ".join(c for _, c in bloque)
    inicio = bloque[0][0].strftime("%Y-%m-%d %H:%M:%S")
    return {
        "codigo": codigos,
        "cuantos": len(bloque),
        "columna": columna,
        "cifra": f"{len(bloque)} estudiantes empezaron dentro de {margen} "
                 f"segundos, a partir de las {inicio}",
        "que_se_observa": "coincidencia de horario de inicio",
    }


def comparar(columnas, filas, fichas, senales, clave, config):
    """Devuelve la comparacion, los casos observados y lo que no se pudo mirar."""
    vigilados, libres, sin_clasificar = _clasificar_instrumentos(fichas, config)
    no_se_pudo = []

    if not vigilados or not libres:
        falta = ("rendida bajo vigilancia" if not vigilados
                 else "hecha por cuenta propia")
        lista = "vigilado" if not vigilados else "no_vigilado"
        no_se_pudo.append({
            "analisis": "vigilado contra no vigilado",
            "por_que": f"no se reconocio ninguna evaluacion {falta} en los "
                       "titulos de las columnas. Si su materia las llama de otro "
                       f"modo, agregue esa palabra a la lista '{lista}' de "
                       "config.json y vuelva a ejecutar.",
        })

    nota_vigilada = _promedio_normalizado(filas, vigilados)
    nota_libre = _promedio_normalizado(filas, libres)

    comparacion, brechas = [], []
    umbral = config["umbral_brecha_instrumentos"]
    for fila, a, b in zip(filas, nota_vigilada, nota_libre):
        if a is None or b is None:
            continue
        brecha = round(b - a, 4)
        registro = {
            "codigo": str(fila[clave]).strip(),
            "vigilado": a, "no_vigilado": b, "brecha": brecha,
        }
        comparacion.append(registro)
        if abs(brecha) >= umbral:
            brechas.append(registro)

    resumen = {
        "instrumentos_vigilados": len(vigilados),
        "instrumentos_no_vigilados": len(libres),
        "sin_clasificar": len(sin_clasificar),
        "estudiantes_comparados": len(comparacion),
        "media_vigilado": round(media([c["vigilado"] for c in comparacion]), 4)
                          if comparacion else None,
        "media_no_vigilado": round(media([c["no_vigilado"] for c in comparacion]), 4)
                             if comparacion else None,
    }

    tiempos = _revisar_tiempos(columnas, filas, fichas, clave, config)
    horas = _revisar_horas(columnas, filas, fichas, clave, config)
    if not de_papel(fichas, DURACION):
        no_se_pudo.append({
            "analisis": "tiempo empleado en cada evaluacion",
            "por_que": "la base no trae ninguna columna con cuanto tardo cada "
                       "estudiante. Se consigue exportando el detalle de intentos "
                       "del aula virtual.",
        })
    if not de_papel(fichas, MOMENTO):
        no_se_pudo.append({
            "analisis": "hora de inicio de cada evaluacion",
            "por_que": "la base no trae ninguna columna con fecha y hora de "
                       "inicio. Sin ella no se puede ver si varios empezaron a la vez.",
        })

    # Los casos se juntan en un solo hallazgo por tipo, con todos los codigos:
    # repetir el mismo hallazgo una vez por estudiante infla el informe y no
    # agrega nada.
    observaciones = []
    if brechas:
        peores = sorted(brechas, key=lambda b: -abs(b["brecha"]))[:10]
        observaciones.append({
            "que_se_observa": "diferencia entre lo vigilado y lo no vigilado",
            "codigos": ", ".join(b["codigo"] for b in peores),
            "estudiantes": len(brechas),
            "cifra": f"brecha de {min(abs(b['brecha']) for b in peores):.2f} a "
                     f"{max(abs(b['brecha']) for b in peores):.2f} puntos en "
                     "escala 0-1",
            "quien_revisa": "el docente, mirando las evidencias de esos trabajos",
        })
    for grupo, titulo in ((tiempos, "tiempo empleado muy por debajo del curso"),
                          (horas, "coincidencia de hora de inicio")):
        if grupo:
            observaciones.append({
                "que_se_observa": titulo,
                "codigos": ", ".join(sorted({c["codigo"] for c in grupo}))[:400],
                "estudiantes": sum(c.get("cuantos", 1) for c in grupo),
                "cifra": grupo[0]["cifra"],
                "quien_revisa": "el docente; el programa solo describe lo que "
                                "muestran los registros",
            })

    return {
        "resumen": resumen,
        "por_estudiante": comparacion,
        "observaciones": observaciones,
        "no_se_pudo": no_se_pudo,
    }
