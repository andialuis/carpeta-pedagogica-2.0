"""Paso: correlacionar_variables

Cruza asistencia, actividad en la plataforma y calificaciones, y reporta cada
relacion con tres datos: que tan fuerte es, en que sentido va y sobre cuantos
estudiantes se calculo. El tercero es el que evita el error tipico: en un curso
de veinte, una relacion muy fuerte puede ser pura casualidad.

Dos cuidados que cambian por completo lo que sale en el informe:

  - LAS RELACIONES TRIVIALES SE APARTAN. Dos fechas de la misma planilla de
    asistencia, o una columna y la medida global que se construyo con ella, se
    mueven juntas por construccion y no dicen nada. Se reportan aparte, como
    columnas redundantes, para que no ocupen el lugar de un hallazgo real.
  - UNA RELACION DEBIL PUEDE ESTAR TAPADA. Si al quitar uno o dos casos extremos
    la relacion se vuelve fuerte, no es que no exista: es que hay un perfil
    distinto mezclado con el resto. Ese es un hallazgo, y de los buenos.
"""

from estadistica import (benjamini_hochberg, correlacion,
                         cuantas_saldrian_por_azar, fuerza, p_correlacion,
                         sentido, veredicto_p, z)
from paso_leer_depurada import (ASISTENCIA, CONSTANTE, IDENTIDAD, NOTA,
                                PAPELEO, SIN_EMPAREJAR,
                                PLATAFORMA, limpiar_titulo, serie)


def _candidatas(columnas, filas, fichas, senales, config):
    """Las columnas que vale la pena cruzar, mas las medidas globales."""
    minimo = config["minimo_datos_para_estadistica"]
    lista = []
    for ficha in fichas:
        if ficha["papel"] not in (NOTA, ASISTENCIA, PLATAFORMA):
            continue
        valores = serie(filas, ficha["indice"])
        if sum(1 for v in valores if v is not None) < minimo:
            continue
        if len(set(v for v in valores if v is not None)) <= 1:
            continue
        lista.append({"nombre": ficha["columna"], "papel": ficha["papel"],
                      "origen": ficha["origen"], "valores": valores,
                      "compone": ficha["papel"]})

    # Las tres medidas globales entran como una columna mas, para poder decir
    # "la asistencia del semestre se relaciona con el rendimiento" en una sola linea.
    globales = [("rendimiento general del estudiante", "rendimiento", NOTA),
                ("asistencia del semestre", "asistencia", ASISTENCIA),
                ("actividad total en la plataforma", "plataforma", PLATAFORMA)]
    for nombre, llave, papel in globales:
        # Si la medida global se construyo con UNA sola columna, esa columna ya
        # esta en la lista y la global es su copia. Agregarla hace que la misma
        # relacion aparezca dos veces en el informe con dos nombres distintos, y
        # el docente cree que son dos hallazgos.
        if sum(1 for c in lista if c["papel"] == papel) == 1:
            continue
        valores = [s.get(llave) for s in senales]
        if sum(1 for v in valores if v is not None) >= minimo and \
                len(set(v for v in valores if v is not None)) > 1:
            lista.append({"nombre": nombre, "papel": papel, "origen": "",
                          "valores": valores, "compone": papel, "global": True})
    return lista


def _es_redundante(a, b, r, config):
    """¿Esta pareja se mueve junta por construccion y no por un hallazgo?"""
    if a.get("global") and b.get("global") is None and a["compone"] == b["papel"]:
        return ("la medida global se construyo con esta misma columna, asi que "
                "no puede sino moverse con ella")
    if b.get("global") and a.get("global") is None and b["compone"] == a["papel"]:
        return ("la medida global se construyo con esta misma columna, asi que "
                "no puede sino moverse con ella")
    if (a["papel"] == b["papel"] == ASISTENCIA):
        return ("son dos fechas de la misma asistencia: van juntas porque miden "
                "lo mismo en dias distintos")
    if a["origen"] and a["origen"] == b["origen"] and r is not None and \
            abs(r) >= config["umbral_correlacion_redundante"]:
        return ("salen del mismo archivo y practicamente coinciden: son la misma "
                "columna escrita dos veces")
    if r is not None and abs(r) >= 0.999:
        return "las dos columnas tienen exactamente los mismos valores"
    return ""


def _sin_atipicos(x, y, config):
    """Vuelve a medir la relacion despues de apartar hasta dos casos extremos."""
    zx, zy = z(x), z(y)
    umbral = config["umbral_z_atipico"]
    sospechosos = []
    for i, (a, b) in enumerate(zip(zx, zy)):
        peor = max(abs(a) if a is not None else 0, abs(b) if b is not None else 0)
        if peor >= umbral:
            sospechosos.append((peor, i))
    if not sospechosos:
        return None, []
    sospechosos.sort(reverse=True)
    fuera = {i for _, i in sospechosos[:2]}
    x2 = [v for i, v in enumerate(x) if i not in fuera]
    y2 = [v for i, v in enumerate(y) if i not in fuera]
    r2, _ = correlacion(x2, y2)
    return r2, sorted(fuera)


def cruzar(columnas, filas, fichas, senales, clave, config):
    """Devuelve (relaciones, redundantes, sin_variacion, tapadas)."""
    candidatas = _candidatas(columnas, filas, fichas, senales, config)
    umbral = config["umbral_correlacion_relevante"]

    relaciones, redundantes, tapadas = [], [], []
    for i in range(len(candidatas)):
        for j in range(i + 1, len(candidatas)):
            a, b = candidatas[i], candidatas[j]
            r, n = correlacion(a["valores"], b["valores"])
            motivo = _es_redundante(a, b, r, config)
            if motivo:
                redundantes.append({
                    "columna_a": a["nombre"], "columna_b": b["nombre"],
                    "relacion": round(r, 4) if r is not None else "",
                    "por_que_se_aparta": motivo, "estudiantes": n})
                continue
            if r is None:
                continue

            if abs(r) >= umbral:
                p = p_correlacion(a["valores"], b["valores"],
                                  config["permutaciones_relaciones"],
                                  config["semilla"])
                # Dos calificaciones del mismo curso casi siempre van juntas: el
                # que rinde bien rinde bien en todo. Es cierto y es esperable, y
                # si se mezcla con lo demas tapa las relaciones que si ensenan
                # algo, como asistencia contra nota.
                misma_familia = a["papel"] == b["papel"]
                # Una fecha de clase suelta no puede competir como hallazgo con
                # la asistencia del semestre: es un trozo de la misma señal, y
                # con veinte estudiantes cualquier clase individual da alguna
                # correlacion por azar. Se reporta, pero no encabeza el informe.
                una_sola_clase = any(
                    c["papel"] == ASISTENCIA and not c.get("global")
                    for c in (a, b))
                relaciones.append({
                    "columna_a": a["nombre"], "columna_b": b["nombre"],
                    "relacion": round(r, 4), "fuerza": fuerza(r),
                    "sentido": sentido(r), "estudiantes": n,
                    "p": round(p, 4) if p is not None else None,
                    "tipo": ("esperable (dos medidas del mismo tipo)"
                             if misma_familia else
                             "una sola clase, no el semestre"
                             if una_sola_clase else "entre variables distintas"),
                    "lectura": veredicto_p(p, config["umbral_p"]),
                })
                continue

            # Relacion debil: comprobar si unos pocos casos la estan tapando.
            r2, fuera = _sin_atipicos(a["valores"], b["valores"], config)
            if r2 is None or not fuera:
                continue
            if abs(r2) >= umbral and \
                    abs(r2) - abs(r) >= config["mejora_para_avisar_atipico"]:
                codigos = [str(filas[i2][clave]).strip() for i2 in fuera
                           if i2 < len(filas)]
                tapadas.append({
                    "columna_a": a["nombre"], "columna_b": b["nombre"],
                    "relacion_con_todos": round(r, 4),
                    "relacion_sin_los_extremos": round(r2, 4),
                    "estudiantes_apartados": ", ".join(codigos),
                    "estudiantes": n,
                    "lectura": (f"con todo el curso la relacion parece {fuerza(r)}, "
                                f"pero al apartar a {len(codigos)} estudiante(s) "
                                f"pasa a ser {fuerza(r2)}: no es que no exista, es "
                                "que hay un perfil distinto mezclado"),
                })

    aislados = _instrumentos_aislados(candidatas, config)

    sin_variacion = [{"columna": f["columna"], "por_que": f["por_que"]}
                     for f in fichas
                     if f["papel"] in (CONSTANTE, SIN_EMPAREJAR, PAPELEO)]
    protegidas = [{"columna": f["columna"], "por_que": f["por_que"]}
                  for f in fichas if f["papel"] == IDENTIDAD]

    relaciones = _quitar_gemelas(relaciones, candidatas, config)

    sobreviven = benjamini_hochberg([r.get("p") for r in relaciones],
                                    config["umbral_p"])
    for relacion, sobrevive in zip(relaciones, sobreviven):
        relacion["sobrevive_al_ajuste"] = "si" if sobrevive else "no"
        if not sobrevive:
            relacion["lectura"] = (
                "no sobrevive al ajuste por haber probado muchas parejas a la "
                "vez: tomela como una pista, no como un hallazgo. "
                + relacion["lectura"])

    # Primero lo que ensena algo, despues lo esperable; dentro de cada grupo,
    # por fuerza. Y se corta la lista: cincuenta relaciones no se leen.
    relaciones.sort(key=lambda x: (x["tipo"] != "entre variables distintas",
                                   -abs(x["relacion"])))
    aviso_multiple = (cuantas_saldrian_por_azar(len(relaciones),
                                                config["umbral_p"])
                      if relaciones else "")
    interesantes = [r for r in relaciones
                    if r["tipo"] == "entre variables distintas"]
    esperables = [r for r in relaciones if r["tipo"] != "entre variables distintas"]
    tope = config["relaciones_a_reportar"]
    relaciones = interesantes[:tope] + esperables[:max(3, tope // 3)]
    return {
        "relaciones": relaciones,
        "relaciones_probadas": len(sobreviven),
        "aviso_comparaciones_multiples": aviso_multiple,
        "redundantes": redundantes,
        "sin_variacion": sin_variacion,
        "protegidas_por_privacidad": protegidas,
        "tapadas_por_casos_extremos": tapadas,
        "instrumentos_aislados": aislados,
        "columnas_cruzadas": len(candidatas),
    }


def _quitar_gemelas(relaciones, candidatas, config):
    """Aparta las relaciones que son la misma dicha con otros nombres.

    Dos columnas casi identicas —«total de accesos» y «dias con actividad», o una
    medida global y la unica columna con la que se construyo— generan pares
    distintos que cuentan el mismo hecho. En el informe se leen como dos
    hallazgos y son uno. Se conserva el mas fuerte de cada grupo.
    """
    por_nombre = {c["nombre"]: c["valores"] for c in candidatas}
    tope = config["umbral_correlacion_redundante"]

    def gemelas(a, b):
        if a == b:
            return True
        va, vb = por_nombre.get(a), por_nombre.get(b)
        if va is None or vb is None:
            return False
        r, _ = correlacion(va, vb)
        return r is not None and abs(r) >= tope

    conservadas = []
    for relacion in sorted(relaciones, key=lambda x: -abs(x["relacion"])):
        repetida = False
        for guardada in conservadas:
            if ((gemelas(relacion["columna_a"], guardada["columna_a"])
                 and gemelas(relacion["columna_b"], guardada["columna_b"]))
                or (gemelas(relacion["columna_a"], guardada["columna_b"])
                    and gemelas(relacion["columna_b"], guardada["columna_a"]))):
                repetida = True
                break
        if not repetida:
            conservadas.append(relacion)
    return conservadas


def _instrumentos_aislados(candidatas, config):
    """Calificaciones que no se parecen a ninguna otra del mismo curso.

    Este detector busca lo contrario que el resto del paso: en vez de relaciones
    fuertes, busca su AUSENCIA. Es de los hallazgos mas valiosos que existen,
    porque no habla de los estudiantes: habla del instrumento. Si en un curso
    todas las evaluaciones se parecen entre si —quien rinde bien en una rinde
    bien en las demas— y hay una que no se parece a ninguna, esa evaluacion no
    esta midiendo lo mismo que el resto.

    Se compara la fuerza MEDIA de cada instrumento con la del curso, y no cuantas
    relaciones fuertes tiene. Con veinte estudiantes, una pareja cualquiera puede
    dar una correlacion alta por puro azar, y contarla como «relacion» bastaba
    para que el instrumento aislado dejara de parecerlo.
    """
    notas = [c for c in candidatas
             if c["papel"] == NOTA and not c.get("global")]
    if len(notas) < 4:
        return []

    fuerzas, n_por_columna = {}, {}
    for i in range(len(notas)):
        propias = []
        for j in range(len(notas)):
            if i == j:
                continue
            r, n = correlacion(notas[i]["valores"], notas[j]["valores"])
            if r is not None:
                propias.append(abs(r))
                n_por_columna[i] = n
        if propias:
            fuerzas[i] = sum(propias) / len(propias)

    if len(fuerzas) < 4:
        return []
    ordenadas = sorted(fuerzas.values())
    tipica = ordenadas[len(ordenadas) // 2]
    if tipica < config["umbral_correlacion_relevante"]:
        # El curso entero esta desconectado: no hay un instrumento raro, es que
        # ninguna evaluacion se parece a otra, y eso ya se ve sin este detector.
        return []

    salida = []
    for indice, media_propia in sorted(fuerzas.items(), key=lambda x: x[1]):
        if media_propia >= config["umbral_correlacion_relevante"]:
            continue
        if media_propia > tipica * config["proporcion_para_instrumento_aislado"]:
            continue
        salida.append({
            "instrumento": limpiar_titulo(notas[indice]["nombre"]),
            "fuerza_media": round(media_propia, 2),
            "fuerza_tipica_del_curso": round(tipica, 2),
            "estudiantes": n_por_columna.get(indice, 0),
            "lectura": (f"su parecido medio con las demas evaluaciones es de "
                        f"{media_propia:.2f} sobre 1, cuando en este curso lo "
                        f"habitual es {tipica:.2f}. Quien rinde bien en el resto "
                        "del curso no rinde necesariamente bien aqui, ni al reves."),
        })
    return salida


def aviso_de_tamano(relaciones, filas, config):
    """Un aviso unico sobre el tamano del curso, en vez de repetirlo en cada fila."""
    n = len(filas)
    if n >= 40:
        return ""
    return (f"El curso tiene {n} estudiantes. Con un grupo de este tamano, una "
            "relacion fuerte puede aparecer por azar: mire siempre la columna de "
            "cuantos estudiantes la sostienen antes de tomar una decision.")
