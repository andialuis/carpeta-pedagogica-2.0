"""Paso: evaluar_hipotesis

Traduce la sospecha del docente a una comparacion que se pueda medir, y la
comprueba. Tambien plantea las hipotesis que el propio programa encuentra, pero
solo sobre variables de contexto (turno, modalidad, grupo, sede): una hipotesis
que enfrente asistencia contra notas se confirma sola y solo sirve para llenar el
informe de obviedades.

Dos cosas que este paso hace y que son mas importantes que el veredicto:

  - Si ninguna columna mide lo que la hipotesis afirma, no busca un sustituto
    parecido: responde "no se puede comprobar con estos datos" y dice que habria
    que registrar. Una hipotesis contestada con la columna equivocada es peor que
    una sin contestar.
  - Nunca da por confirmada una hipotesis porque encontro una relacion fuerte en
    otra parte de los datos. La evidencia tiene que hablar de LO MISMO.

La hipotesis entra por la linea de ordenes en cada ejecucion. No queda escrita
dentro del programa (R6).
"""

from estadistica import (benjamini_hochberg, correlacion,
                         cuantas_saldrian_por_azar, fuerza, media,
                         p_correlacion, p_diferencia_de_medias, sentido,
                         tamano_del_efecto, veredicto_p)
from paso_leer_depurada import (CONTEXTO, NOTA, a_numero, limpiar_titulo,
                                normalizar)

# Como se nombra en el aula cada una de las medidas que el programa sabe calcular.
MEDIDAS = {
    "rendimiento": ["nota", "notas", "calificacion", "calificaciones", "rinde",
                    "rinden", "rendimiento", "promedio", "puntaje", "resultado",
                    "aprueba", "reprueba", "reprueban", "desempeno"],
    "asistencia": ["asiste", "asisten", "asistencia", "falta", "faltas",
                   "ausencia", "ausencias", "viene", "vienen", "puntualidad"],
    "plataforma": ["plataforma", "moodle", "aula virtual", "campus", "entra",
                   "entran", "conecta", "conectan", "accede", "acceden",
                   "acceso", "accesos", "actividad en linea", "clics"],
}

DIRECCION_MENOS = ["menos", "menor", "peor", "peores", "baja", "bajas", "bajo",
                   "bajos", "abandona", "abandonan", "cae", "caen", "inferior"]
DIRECCION_MAS = ["mas", "mayor", "mejor", "mejores", "alta", "altas", "alto",
                 "altos", "sube", "suben", "superior"]

# Palabras que no aportan nada al buscar de que habla la hipotesis.
VACIAS = set("""el la los las un una unos unas de del al a en y o u que se su sus
mi mis con por para como es son fue fueron tiene tienen hay este esta estos estas
mas menos muy poco mucho porque cuando donde cual cuales quien quienes lo le les
sobre entre desde hasta durante segun tambien pero sino ni no si""".split())


def _palabras(texto):
    plano = normalizar(texto)
    limpio = "".join(c if c.isalnum() or c.isspace() else " " for c in plano)
    return [p for p in limpio.split() if len(p) > 2 and p not in VACIAS]


def _medidas_mencionadas(texto):
    """Todas las medidas que nombra la hipotesis, en el orden en que aparecen."""
    plano = f" {normalizar(texto)} "
    encontradas = []
    for medida, palabras in MEDIDAS.items():
        posiciones = [plano.find(f" {p} ") for p in palabras
                      if f" {p} " in plano]
        if posiciones:
            encontradas.append((min(posiciones), medida))
    encontradas.sort()
    return [m for _, m in encontradas]


def _medida_mencionada(texto):
    medidas = _medidas_mencionadas(texto)
    return medidas[0] if medidas else None


def _relacionar(senales, medida_a, medida_b, config, etiqueta):
    """Cuando la hipotesis enfrenta dos medidas —"los que menos entran a la
    plataforma sacan peores notas"— no hay dos grupos que comparar: hay dos
    columnas que se mueven juntas o no. Es la forma en que la mayoria de los
    docentes formula su sospecha, y rechazarla por no nombrar un grupo seria
    dejar sin responder justo la pregunta que trajo."""
    a = [s.get(medida_a) for s in senales]
    b = [s.get(medida_b) for s in senales]
    r, n = correlacion(a, b)
    if r is None:
        return {
            "hipotesis": etiqueta, "veredicto": "no se puede comprobar",
            "cifra": "", "estudiantes": n, "origen": "docente",
            "detalle": f"solo hay {n} estudiante(s) con las dos medidas a la vez",
        }
    p = p_correlacion(a, b, config["permutaciones"], config["semilla"])
    sostiene = (p is not None and p <= config["umbral_p"]
                and abs(r) >= config["umbral_correlacion_relevante"])
    return {
        "hipotesis": etiqueta,
        "grupo": f"{medida_a} frente a {medida_b}",
        "medida": f"{medida_a} y {medida_b}",
        "veredicto": "se sostiene" if sostiene else "no se sostiene",
        "cifra": f"relacion {fuerza(r)} ({r:+.2f}); {sentido(r)}",
        "estudiantes": n,
        "p": round(p, 4) if p is not None else None,
        "efecto": round(r, 3),
        "detalle": veredicto_p(p, config["umbral_p"]),
        "origen": "docente",
    }


def _formas_de(llave):
    """Como puede haber escrito el docente el nombre de ese grupo.

    Los valores de una columna suelen traer una aclaracion que nadie repite al
    hablar: «madrugada (00-05)», «turno noche - vespertino», «Grupo B / Lab».
    El docente escribe «madrugada» a secas. Si solo se busca la forma completa,
    su hipotesis queda como «compara un grupo que no existe» aunque el grupo
    este ahi, y encima el programa la encuentra despues por su cuenta: el
    docente ve su pregunta rechazada y el mismo hallazgo confirmado dos lineas
    mas abajo. Se prueban tambien las formas cortas.
    """
    formas = [llave]
    for corte in ("(", "/", " - ", ",", ":"):
        if corte in llave:
            formas.append(llave.split(corte)[0].strip())
    primera = llave.split()[0] if llave.split() else ""
    if len(primera) >= 4:
        formas.append(primera)
    vistas, salida = set(), []
    for f in formas:
        f = f.strip()
        if f and f not in vistas:
            vistas.add(f)
            salida.append(f)
    return salida


def _grupo_mencionado(texto, columnas, filas, fichas):
    """Busca en la hipotesis el nombre de un grupo que exista en los datos.

    Se compara contra los VALORES de las columnas de contexto, no contra sus
    titulos: el docente escribe "los virtuales", no "modalidad".
    """
    plano = f" {normalizar(texto)} "
    candidatos = []
    for ficha in fichas:
        if ficha["papel"] != CONTEXTO:
            continue
        indice = ficha["indice"]
        valores = {}
        for fila in filas:
            bruto = fila[indice]
            if bruto is None or not str(bruto).strip():
                continue
            valores.setdefault(normalizar(bruto), str(bruto).strip())
        for llave, original in valores.items():
            for forma in _formas_de(llave):
                if forma and (f" {forma} " in plano or f" {forma}s " in plano
                              or forma.rstrip("s") + " " in plano):
                    candidatos.append({"columna": ficha["columna"],
                                       "indice": indice, "valor": original})
                    break
    # La situacion en el curso siempre esta disponible y el docente la nombra mucho.
    if " abandon" in plano or "desert" in plano:
        indice = columnas.index("situacion_en_el_curso")
        candidatos.append({"columna": "situacion_en_el_curso", "indice": indice,
                           "valor": "abandono"})
    return candidatos[0] if candidatos else None


def _valores_de_medida(senales, medida):
    return [s.get(medida) for s in senales]


def _comparar(senales, filas, grupo, medida, config, etiqueta, valores=None):
    """Compara el grupo senalado contra el resto del curso."""
    if valores is None:
        valores = _valores_de_medida(senales, medida)
    indice = grupo["indice"]
    objetivo = normalizar(grupo["valor"])

    dentro, fuera = [], []
    for fila, valor in zip(filas, valores):
        if valor is None:
            continue
        (dentro if normalizar(fila[indice]) == objetivo else fuera).append(valor)

    minimo = config["minimo_por_grupo"]
    if len(dentro) < minimo or len(fuera) < minimo:
        return {
            "hipotesis": etiqueta,
            "veredicto": "no se puede comprobar",
            "cifra": "",
            "estudiantes": len(dentro) + len(fuera),
            "detalle": f"uno de los dos grupos tiene menos de {minimo} "
                       f"estudiantes con dato ({len(dentro)} contra {len(fuera)}): "
                       "cualquier diferencia seria ruido",
            "origen": "docente",
        }

    ma, mb = media(dentro), media(fuera)
    p = p_diferencia_de_medias(dentro, fuera, config["permutaciones"],
                               config["semilla"])
    efecto = tamano_del_efecto(dentro, fuera)
    hay_diferencia = p is not None and p <= config["umbral_p"]

    return {
        "hipotesis": etiqueta,
        "grupo": f"{grupo['columna']} = {grupo['valor']}",
        "medida": medida,
        "veredicto": "se sostiene" if hay_diferencia else "no se sostiene",
        "cifra": f"{ma:.3f} contra {mb:.3f} (diferencia {ma - mb:+.3f})",
        "estudiantes": len(dentro) + len(fuera),
        "n_grupo": len(dentro),
        "n_resto": len(fuera),
        "p": round(p, 4) if p is not None else None,
        "efecto": round(efecto, 3) if efecto is not None else None,
        "detalle": veredicto_p(p, config["umbral_p"]),
        "origen": "docente",
    }


def evaluar(hipotesis, columnas, filas, fichas, senales, config):
    """Comprueba la hipotesis del docente. Devuelve el resultado y los avisos."""
    if not hipotesis or not hipotesis.strip():
        return None, ["no se entrego ninguna hipotesis: se analiza sin ella"]

    avisos = []
    medidas = _medidas_mencionadas(hipotesis)
    medida = medidas[0] if medidas else None
    grupo = _grupo_mencionado(hipotesis, columnas, filas, fichas)

    # Una hipotesis suele nombrar dos cosas: DE DONDE sale el grupo y QUE se le
    # mide. «Los que entran al aula virtual de madrugada sacan notas mas bajas»
    # nombra plataforma y rendimiento, pero lo que se compara son las notas; el
    # aula virtual solo dice quien es quien. Tomando siempre la primera medida
    # nombrada, el programa medía sobre una senal vacia y contestaba «cero
    # contra cero», que al docente le suena a que su pregunta estaba mal hecha.
    # Con un grupo ya identificado, se mide sobre la primera medida que de
    # verdad tenga datos.
    if grupo is not None and medidas:
        con_datos = [m for m in medidas
                     if any(s.get(m) is not None for s in senales)]
        if con_datos:
            medida = con_datos[0]

    # Dos medidas y ningun grupo: la hipotesis habla de una relacion, no de una
    # comparacion entre grupos.
    if len(medidas) >= 2 and grupo is None:
        disponibles = [m for m in medidas
                       if any(s.get(m) is not None for s in senales)]
        if len(disponibles) >= 2:
            return _relacionar(senales, disponibles[0], disponibles[1], config,
                               hipotesis.strip()), avisos
        faltan = [m for m in medidas if m not in disponibles]
        return {
            "hipotesis": hipotesis.strip(),
            "veredicto": "no se puede comprobar con estos datos",
            "cifra": "", "estudiantes": 0, "origen": "docente",
            "detalle": "la hipotesis habla de " + " y de ".join(faltan)
                       + ", y la base no trae ninguna columna que lo registre.",
        }, avisos

    if medida is None:
        return {
            "hipotesis": hipotesis.strip(),
            "veredicto": "no se puede comprobar con estos datos",
            "cifra": "",
            "estudiantes": 0,
            "detalle": "la hipotesis no nombra ninguna medida que exista en la "
                       "base (nota, asistencia o actividad en la plataforma). "
                       "Habria que registrar la variable de la que habla, o "
                       "reformularla sobre una que si este.",
            "origen": "docente",
        }, avisos

    if grupo is None:
        return {
            "hipotesis": hipotesis.strip(),
            "veredicto": "no se puede comprobar con estos datos",
            "cifra": "",
            "estudiantes": 0,
            "medida": medida,
            "detalle": "la hipotesis compara un grupo que no existe como columna "
                       "en la base. Para comprobarla habria que registrar a que "
                       "grupo pertenece cada estudiante (turno, modalidad, sede, "
                       "grupo de trabajo).",
            "origen": "docente",
        }, avisos

    # Palabras de la hipotesis que no encontraron eco en ninguna columna: se
    # avisan ahora, no al final, para que el docente pueda reformular.
    reconocidas = set(MEDIDAS[medida]) | {normalizar(grupo["valor"])}
    reconocidas |= set(DIRECCION_MAS) | set(DIRECCION_MENOS)
    titulos = " ".join(normalizar(c) for c in columnas)
    sueltas = [p for p in _palabras(hipotesis)
               if p not in reconocidas and p not in titulos]
    if sueltas:
        avisos.append("estas palabras de la hipotesis no corresponden a ninguna "
                      "columna de la base y no se usaron: " + ", ".join(sueltas[:8]))

    resultado = _comparar(senales, filas, grupo, medida, config,
                          hipotesis.strip())

    # La direccion importa: que haya diferencia no significa que sea la que el
    # docente supuso. Si va al reves, se dice.
    plano = f" {normalizar(hipotesis)} "
    espera_menos = any(f" {p} " in plano for p in DIRECCION_MENOS)
    if resultado.get("veredicto") == "se sostiene":
        signo = resultado["cifra"].split("diferencia ")[-1].rstrip(")")
        va_hacia_abajo = signo.startswith("-")
        if espera_menos != va_hacia_abajo:
            resultado["veredicto"] = "se sostiene, pero al reves"
            resultado["detalle"] = (
                "hay una diferencia real entre los dos grupos, pero va en el "
                "sentido contrario al que suponia la hipotesis. " +
                resultado["detalle"])
    return resultado, avisos


def _particion(filas, indice):
    """Como reparte esta columna a los estudiantes, sin importar como se llamen
    los grupos. Sirve para descubrir que dos columnas distintas separan al curso
    exactamente igual."""
    grupos = {}
    for numero, fila in enumerate(filas):
        grupos.setdefault(normalizar(fila[indice]), set()).add(numero)
    return frozenset(frozenset(v) for v in grupos.values())


def hipotesis_del_programa(columnas, filas, fichas, senales, config,
                          ya_probada=None):
    """Las que propone el programa: solo sobre variables de contexto.

    Tres cuidados que evitan un informe lleno de la misma hipotesis repetida:

      - Si una columna tiene dos categorias, se comprueba UNA. Decir que los
        virtuales rinden menos y que los presenciales rinden mas es la misma
        frase dos veces.
      - Si dos columnas separan al curso exactamente igual (pasa cuando el turno
        y la modalidad coinciden), se usa una y se avisa: los datos no permiten
        distinguir cual de las dos explica la diferencia.
      - Al final se ajusta por la cantidad de comprobaciones hechas. Probando
        muchas cosas a la vez, algunas salen bien por azar.
    """
    resultados, avisos = [], []
    # Lo que ya pregunto el docente no se vuelve a preguntar con otras palabras.
    cubierta = None
    if ya_probada and ya_probada.get("grupo"):
        cubierta = (ya_probada["grupo"].split(" = ")[0], ya_probada.get("medida"))
    candidatas = [f for f in fichas if f["papel"] == CONTEXTO]
    ya_estan = {f["columna"] for f in candidatas}
    if "situacion_en_el_curso" in columnas and \
            "situacion_en_el_curso" not in ya_estan:
        candidatas.append({"columna": "situacion_en_el_curso",
                           "indice": columnas.index("situacion_en_el_curso"),
                           "papel": CONTEXTO})

    # Ademas de las tres medidas globales, se prueba CADA INSTRUMENTO por
    # separado. Sin esto el analisis no puede ver que un grupo rinde igual que
    # el resto en todo menos en el laboratorio: la diferencia se diluye dentro
    # del promedio y el informe concluye que no pasa nada. Y esa —«a este grupo
    # le va mal solo en esta actividad»— es de las conclusiones mas accionables
    # que puede dar una analitica, porque señala una parte concreta del curso.
    medidas_a_probar = [(m, [s.get(m) for s in senales])
                        for m in ("rendimiento", "asistencia", "plataforma")]
    for ficha_nota in fichas:
        if ficha_nota["papel"] != NOTA:
            continue
        columna = ficha_nota["columna"]
        medidas_a_probar.append(
            (limpiar_titulo(columna),
             [a_numero(f[ficha_nota["indice"]]) for f in filas]))

    vistas = {}
    for ficha in candidatas:
        indice = ficha["indice"]
        categorias = {}
        for fila in filas:
            bruto = fila[indice]
            if bruto is None or not str(bruto).strip():
                continue
            categorias.setdefault(normalizar(bruto), str(bruto).strip())
        if not 2 <= len(categorias) <= config["maximo_categorias_contexto"]:
            continue

        reparto = _particion(filas, indice)
        if reparto in vistas:
            avisos.append(
                f"«{ficha['columna']}» separa al curso exactamente igual que "
                f"«{vistas[reparto]}»: se analizo una sola vez. Con estos datos "
                "no se puede saber cual de las dos explica la diferencia.")
            continue
        vistas[reparto] = ficha["columna"]

        # Con dos categorias basta una comparacion: la otra es su espejo.
        valores_a_probar = sorted(categorias.values())
        if len(categorias) == 2:
            valores_a_probar = valores_a_probar[:1]

        for medida, valores in medidas_a_probar:
            if all(v is None for v in valores):
                continue
            if cubierta and cubierta == (ficha["columna"], medida):
                continue
            for original in valores_a_probar:
                grupo = {"columna": ficha["columna"], "indice": indice,
                         "valor": original}
                etiqueta = (f"los estudiantes con {ficha['columna']} = "
                            f"{original} se diferencian del resto del curso en "
                            f"{medida}")
                salida = _comparar(senales, filas, grupo, medida, config,
                                   etiqueta, valores)
                salida["origen"] = "el programa"
                if salida["veredicto"] == "no se puede comprobar":
                    continue
                resultados.append(salida)

    # Solo se reportan las que dicen algo. Las que no se sostienen se conservan
    # igual: descartar una sospecha tambien es un resultado, y el docente pidio
    # saber cuales quedaron descartadas.
    # Ajuste por comparaciones multiples: sin el, probar veinte cosas garantiza
    # que una salga "confirmada" aunque no haya nada.
    sobreviven = benjamini_hochberg([r.get("p") for r in resultados],
                                    config["umbral_p"])
    for resultado, sobrevive in zip(resultados, sobreviven):
        resultado["sobrevive_al_ajuste"] = "si" if sobrevive else "no"
        if resultado["veredicto"] == "se sostiene" and not sobrevive:
            resultado["veredicto"] = "no se sostiene al ajustar"
            resultado["detalle"] = (
                "por si sola la diferencia parecia real, pero se probaron "
                f"{len(resultados)} comparaciones a la vez y esta no sobrevive "
                "al ajuste. " + resultado["detalle"])

    if resultados:
        avisos.append(cuantas_saldrian_por_azar(len(resultados),
                                                config["umbral_p"]))
    resultados.sort(key=lambda r: (not str(r["veredicto"]).startswith("se sostiene"),
                                   r.get("p") if r.get("p") is not None else 1))
    return resultados[:12], avisos
