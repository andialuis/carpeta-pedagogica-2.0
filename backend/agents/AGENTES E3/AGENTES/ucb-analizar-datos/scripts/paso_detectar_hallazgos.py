"""Paso: detectar_hallazgos

Reune todo lo que encontraron los pasos anteriores y decide que merece llamarse
hallazgo.

La regla es estricta y no se negocia: un hallazgo necesita las tres cosas o no
entra. La cifra que lo respalda, a cuantos estudiantes afecta, y que pasa si el
docente no hace nada. Sin la tercera, un hallazgo es una curiosidad; sin la
segunda, es una anecdota; sin la primera, es una opinion.

Si con estos datos no salen cinco que se sostengan, se entregan los que si y se
dice cuantos faltaron y que informacion haria falta para conseguirlos. Cuatro
hallazgos solidos valen mas que cinco con uno inventado.
"""

def _limitar_relaciones(hallazgos, config):
    """Cuantas relaciones entre columnas caben en un informe de ocho.

    Las relaciones son la unica familia que el programa puede producir sin
    limite: con veinte columnas hay ciento noventa pares posibles, y las mas
    fuertes suelen compartir una punta (tres relaciones distintas que en el
    fondo dicen «quien entra al aula rinde mejor»). Los demas hallazgos son
    unicos por construccion: hay un solo grupo que abandona, un solo aviso
    anticipado, un solo instrumento que no se parece a los demas.

    Sin este tope, la familia numerosa desplaza a las unicas y el informe pierde
    justo lo que nadie mas iba a contarle al docente. Las relaciones que quedan
    fuera no se pierden: se cuentan entre las sobrantes y siguen en la hoja de
    correlaciones completa.
    """
    tope = config.get("relaciones_maximo_en_informe", 2)
    quedan, vistas = [], 0
    for h in hallazgos:
        if h.get("grafico") == "relacion":
            if vistas >= tope:
                continue
            vistas += 1
        quedan.append(h)
    return quedan


SEPARADOR = " se diferencian del resto del curso en "


def _juntar_por_grupo(sostenidas):
    """Un mismo grupo que destaca en varios instrumentos es UN hallazgo.

    Cuando el programa compara un grupo contra el resto, lo hace instrumento por
    instrumento. Si el grupo B rinde distinto en tres practicas, salian tres
    hallazgos con la misma frase y distinto numero al final. Para el docente eso
    no son tres noticias: es una sola, y ademas ocupaba tres de los ocho lugares
    del informe y dejaba fuera hallazgos de otro tipo. Aqui se juntan en uno solo
    que nombra los instrumentos donde aparece la diferencia, ordenados del caso
    mas claro al menos claro.
    """
    grupos, orden = {}, []
    for h in sostenidas:
        titulo = str(h.get("hipotesis", ""))
        if SEPARADOR not in titulo:
            orden.append(h)
            continue
        base, medida = titulo.split(SEPARADOR, 1)
        grupos.setdefault(base, []).append((h, medida))
        if base not in orden:
            orden.append(base)

    juntadas = []
    for elemento in orden:
        if not isinstance(elemento, str):
            juntadas.append(elemento)
            continue
        casos = sorted(grupos[elemento], key=lambda par: _a_p(par[0]))
        principal = dict(casos[0][0])
        medidas = []
        for _, medida in casos:
            if medida not in medidas:
                medidas.append(medida)
        if len(medidas) == 1:
            principal["hipotesis"] = elemento + SEPARADOR + medidas[0]
        else:
            visibles = ", ".join(medidas[:3])
            resto = ("" if len(medidas) <= 3
                     else f" y {len(medidas) - 3} instrumento"
                          f"{'s' if len(medidas) - 3 > 1 else ''} mas")
            principal["hipotesis"] = (
                f"{elemento} se diferencian del resto del curso en "
                f"{len(medidas)} instrumentos: {visibles}{resto}")
            principal["detalle"] = (
                f"{principal.get('detalle', '')} La diferencia no aparece en un "
                f"solo instrumento sino en {len(medidas)}, lo que hace mas "
                f"dificil que sea casualidad de una evaluacion suelta.").strip()
        juntadas.append(principal)
    return juntadas


def _a_p(h):
    try:
        return float(h.get("p", 1))
    except (TypeError, ValueError):
        return 1.0


def _prioridad_por_alcance(afectados, total, la_pidio_el_docente):
    """Que tan urgente es un hallazgo confirmado.

    Antes dependia de QUIEN habia planteado la sospecha: si la traia el docente
    era «alta» y si la encontraba el programa era «media». Eso ordenaba mal el
    informe: un hallazgo que alcanza a media clase quedaba por debajo de una
    curiosidad que alcanza a dos personas, solo porque nadie lo habia sospechado
    antes. Lo que decide la urgencia es a cuantos alcanza.
    """
    if la_pidio_el_docente:
        return "alta"
    if not total:
        return "media"
    fraccion = afectados / total
    if fraccion >= 0.5:
        return "urgente"
    if fraccion >= 0.2:
        return "alta"
    return "media"


def _hallazgo(titulo, cifra, afectados, consecuencia, apoyo, prioridad="media",
              grafico=""):
    """Un hallazgo. `grafico` dice cual de las imagenes lo respalda.

    Se guarda aqui, donde se sabe de que habla el hallazgo, y no se decide al
    imprimir: emparejar imagenes por su posicion en la lista pondria al lado de
    un hallazgo un grafico que habla de otra cosa, con un pie de foto que no
    corresponde. Un grafico equivocado confunde mas que ninguno.
    """
    return {
        "hallazgo": titulo,
        "cifra": cifra,
        "estudiantes_afectados": afectados,
        "si_no_hago_nada": consecuencia,
        "en_que_se_apoya": apoyo,
        "prioridad": prioridad,
        "grafico": grafico,
    }


def aviso_anticipado(abandonos, config):
    """¿El aula virtual aviso antes que la asistencia?

    Cuando alguien deja de entrar a la plataforma semanas antes de dejar de venir
    a clase, la plataforma fue la señal temprana y la asistencia llego tarde. Es
    el hallazgo mas accionable de todos: dice exactamente donde mirar el semestre
    que viene para alcanzar a intervenir mientras todavia se puede.
    """
    import datetime as _dt

    def fecha(valor):
        if isinstance(valor, _dt.datetime):
            return valor.date()
        if isinstance(valor, _dt.date):
            return valor
        try:
            return _dt.date.fromisoformat(str(valor).strip()[:10])
        except (ValueError, TypeError):
            return None

    casos = []
    for fila in abandonos:
        ultima_clase = fecha(fila.get("desde"))
        ultimo_acceso = fecha(fila.get("ultimo_acceso"))
        if not ultima_clase or not ultimo_acceso:
            continue
        dias = (ultima_clase - ultimo_acceso).days
        if dias >= config["dias_de_aviso_anticipado"]:
            casos.append({"codigo": str(fila.get("codigo", "")), "dias": dias})
    return casos


def reunir(resumen_curso, perfiles, relaciones, hipotesis_docente,
           hipotesis_programa, instrumentos, actividad, senales, config,
           filas_de_abandonos=()):
    """Devuelve (hallazgos, faltantes, que_haria_falta)."""
    hallazgos = []

    # 1. Abandono: es el hallazgo que mas veces esta y que mas veces se pasa por alto.
    abandonos = resumen_curso["abandonos"]
    total = resumen_curso["total"]
    if abandonos:
        hallazgos.append(_hallazgo(
            "El curso perdio estudiantes por el camino",
            f"{abandonos} de {total} estudiantes ({abandonos / total:.1%}) "
            "dejaron de participar",
            abandonos,
            "el promedio del curso seguira calculandose sobre los que se "
            "quedaron, y la perdida no aparecera en ningun indicador",
            "hoja ABANDONOS de la etapa anterior",
            "urgente"))

    # 1b. La plataforma que aviso antes que la asistencia.
    anticipados = aviso_anticipado(filas_de_abandonos, config)
    if anticipados:
        dias = max(c["dias"] for c in anticipados)
        codigos = ", ".join(c["codigo"] for c in anticipados)
        hallazgos.append(_hallazgo(
            "El aula virtual aviso antes que la asistencia",
            f"dejaron de entrar a la plataforma hasta {dias} dias antes de dejar "
            f"de venir a clase",
            len(anticipados),
            "se seguira esperando a que falten a clase para reaccionar, cuando "
            "el aviso ya estaba disponible semanas antes",
            f"codigos: {codigos}. Comparacion entre la ultima clase a la que "
            "asistieron y su ultimo acceso registrado.",
            "urgente"))

    # 2. Perfiles de riesgo.
    for perfil in perfiles:
        if perfil["estudiantes"] <= 0:
            continue
        if perfil["perfil"] == "Poca presencia y bajo resultado":
            hallazgos.append(_hallazgo(
                "Hay un grupo que ni aparece ni aprueba",
                f"{perfil['estudiantes']} estudiantes con participacion y "
                f"resultado en el tercio bajo "
                f"(rendimiento medio {perfil['rendimiento_medio']})",
                perfil["estudiantes"],
                "es el grupo con mayor probabilidad de abandonar; sin contacto "
                "directo la mayoria no vuelve",
                f"perfil «{perfil['perfil']}» ({perfil['codigos']})",
                "urgente", "perfiles"))
        elif perfil["perfil"] == "Se esfuerza y aun asi no le sale":
            hallazgos.append(_hallazgo(
                "Hay estudiantes que se esfuerzan y no les alcanza",
                f"{perfil['estudiantes']} estudiantes con participacion alta y "
                f"resultado bajo (rendimiento medio {perfil['rendimiento_medio']})",
                perfil["estudiantes"],
                "se desmotivan y terminan abandonando aunque estaban dispuestos; "
                "es la perdida mas evitable de todas",
                f"perfil «{perfil['perfil']}» ({perfil['codigos']})",
                "alta", "perfiles"))
        elif perfil["perfil"] == "Rinde bien casi sin aparecer":
            hallazgos.append(_hallazgo(
                "Hay estudiantes que rinden sin apenas registrarse",
                f"{perfil['estudiantes']} estudiantes con resultado alto y muy "
                "poca presencia registrada",
                perfil["estudiantes"],
                "si es un problema de registro, sus datos seguiran incompletos; "
                "si dominan la materia, se los esta atendiendo como si no",
                f"perfil «{perfil['perfil']}» ({perfil['codigos']})",
                "media", "perfiles"))

    # 3. Las relaciones que se sostienen. Solo las que cruzan variables de
    #    naturaleza distinta —asistencia contra nota, plataforma contra nota— y
    #    solo las que sobreviven al ajuste. Que dos parciales vayan juntos es
    #    cierto, esperable, y no le dice al docente que hacer el lunes.
    utiles = [r for r in relaciones.get("relaciones", [])
              if r.get("tipo") == "entre variables distintas"
              and r.get("sobrevive_al_ajuste") == "si"]
    for relacion in utiles[:3]:
        hallazgos.append(_hallazgo(
            f"«{relacion['columna_a']}» y «{relacion['columna_b']}» se mueven juntas",
            f"relacion {relacion['fuerza']} ({relacion['relacion']:+.2f}); "
            f"{relacion['sentido']}",
            relacion["estudiantes"],
            "se seguira decidiendo sobre una de las dos sin mirar la otra, "
            "aunque el dato para anticiparse ya este disponible",
            f"cruce sobre {relacion['estudiantes']} estudiantes; {relacion['lectura']}",
            "alta", "relacion"))

    # 4. Relaciones que unos pocos casos estaban tapando.
    for tapada in relaciones.get("tapadas_por_casos_extremos", [])[:1]:
        hallazgos.append(_hallazgo(
            "Una relacion invisible en el promedio aparece al apartar unos pocos casos",
            f"{tapada['relacion_con_todos']:+.2f} con todo el curso, "
            f"{tapada['relacion_sin_los_extremos']:+.2f} sin "
            f"{tapada['estudiantes_apartados']}",
            tapada["estudiantes"],
            "el curso seguira tratandose como un grupo homogeneo cuando en "
            "realidad hay dos comportamientos distintos mezclados",
            tapada["lectura"],
            "alta", "relacion"))

    # 4b. El instrumento que no se parece a ningun otro del curso.
    for aislado in relaciones.get("instrumentos_aislados", [])[:2]:
        hallazgos.append(_hallazgo(
            f"«{aislado['instrumento']}» no se parece a ninguna otra evaluacion "
            "del curso",
            f"parecido medio de {aislado['fuerza_media']} con las demas "
            f"evaluaciones, cuando en este curso lo habitual es "
            f"{aislado['fuerza_tipica_del_curso']}",
            aislado["estudiantes"],
            "se seguira usando para calificar un aprendizaje que, segun los "
            "propios datos del curso, no esta midiendo",
            aislado["lectura"],
            "alta"))

    # 5. Hipotesis del docente y del programa que se sostuvieron.
    sostenidas = [h for h in ([hipotesis_docente] if hipotesis_docente else [])
                  + hipotesis_programa
                  if h and str(h.get("veredicto", "")).startswith("se sostiene")
                  and h.get("sobrevive_al_ajuste") != "no"]
    for h in _juntar_por_grupo(sostenidas):
        es_relacion = " frente a " in str(h.get("grupo", ""))
        hallazgos.append(_hallazgo(
            f"Se confirmo: {h['hipotesis']}",
            h.get("cifra", ""),
            h.get("estudiantes", 0),
            "seguira sin usarse para anticiparse: el dato que lo muestra ya "
            "existe y nadie lo esta mirando" if es_relacion
            else "la diferencia entre esos grupos seguira sin atenderse",
            h.get("detalle", ""),
            _prioridad_por_alcance(h.get("estudiantes", 0),
                                   resumen_curso["total"],
                                   h.get("origen") == "docente"),
            "relacion" if es_relacion else ""))

    # 6. Instrumentos vigilados contra no vigilados.
    for observacion in instrumentos.get("observaciones", []):
        hallazgos.append(_hallazgo(
            f"Se observa {observacion['que_se_observa']}",
            observacion["cifra"],
            observacion["estudiantes"],
            "la evidencia queda sin revisar y la evaluacion pierde validez "
            "para todo el curso",
            f"codigos: {observacion['codigos']}. Revisa: "
            f"{observacion['quien_revisa']}",
            "alta", "instrumentos"))

    # 7. Linea de tiempo del aula.
    if actividad.get("disponible"):
        for observacion in actividad.get("observaciones", [])[:2]:
            if observacion["observacion"] == "hora de mayor actividad":
                continue
            hallazgos.append(_hallazgo(
                f"El aula virtual muestra {observacion['observacion']}",
                observacion["cifra"],
                resumen_curso["total"],
                "se seguiran programando entregas sin saber cuando trabaja "
                "realmente el curso",
                f"archivo {actividad.get('archivo', '')}, "
                f"{actividad.get('eventos', 0)} eventos",
                "media", "actividad"))

    # Un hallazgo que no afecta a nadie no es un hallazgo.
    hallazgos = [h for h in hallazgos if (h["estudiantes_afectados"] or 0) > 0]

    # Y uno que repite lo que ya dijo otro tampoco: se queda el primero.
    vistos, unicos = set(), []
    for h in hallazgos:
        firma = (h["hallazgo"][:60], h["cifra"][:40])
        if firma in vistos:
            continue
        vistos.add(firma)
        unicos.append(h)
    hallazgos = unicos

    orden = {"urgente": 0, "alta": 1, "media": 2, "baja": 3}
    hallazgos.sort(key=lambda h: (orden.get(h["prioridad"], 9),
                                  -(h["estudiantes_afectados"] or 0)))

    # Un informe con veinte hallazgos no tiene ninguno: el docente no sabe por
    # donde empezar. Se entregan los mas importantes y el resto queda en el Excel.
    hallazgos = _limitar_relaciones(hallazgos, config)
    sobrantes = max(0, len(hallazgos) - config["hallazgos_maximo"])
    hallazgos = hallazgos[:config["hallazgos_maximo"]]

    objetivo = config["hallazgos_objetivo"]
    faltantes = max(0, objetivo - len(hallazgos))
    que_haria_falta = []
    if faltantes:
        if not any(s.get("plataforma") is not None for s in senales):
            que_haria_falta.append(
                "el registro de actividad del aula virtual: sin el no se puede "
                "distinguir a quien trabaja fuera de clase de quien no aparece")
        if not actividad.get("disponible"):
            que_haria_falta.append(
                "el detalle de eventos del aula virtual con fecha y hora, para "
                "ver cuando trabaja el curso y como reacciona a las entregas")
        if instrumentos["resumen"]["instrumentos_no_vigilados"] == 0 or \
                instrumentos["resumen"]["instrumentos_vigilados"] == 0:
            que_haria_falta.append(
                "distinguir en el titulo de cada evaluacion si fue rendida en "
                "aula o por cuenta propia, para poder compararlas")
        if not que_haria_falta:
            que_haria_falta.append(
                "mas variables de contexto (turno, modalidad, grupo de trabajo, "
                "sede): son las que permiten comparar grupos entre si")

    return hallazgos, faltantes, que_haria_falta, sobrantes


def marcar_datos_sucios(anomalias_heredadas):
    """R1: si la base todavia arrastra valores sospechosos, se avisa y no se toca.

    Arreglarlos aqui rompe la trazabilidad: la etapa de procesamiento dejo
    constancia de cada cambio, y una correccion hecha en el analisis no aparece
    en ningun registro.
    """
    if not anomalias_heredadas:
        return []
    return [{
        "aviso": f"la base trae {len(anomalias_heredadas)} valor(es) marcados "
                 "como sospechosos por la etapa anterior y NO se corrigieron aqui",
        "que_hacer": "si alguno es un error de captura, corrijalo en el archivo "
                     "original y vuelva a ejecutar la Etapa 2. Corregirlo en el "
                     "analisis dejaria dos versiones distintas de la misma nota.",
    }]
