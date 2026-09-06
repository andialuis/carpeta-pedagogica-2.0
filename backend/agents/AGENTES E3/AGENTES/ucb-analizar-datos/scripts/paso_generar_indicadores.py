"""Paso: generar_indicadores

Traduce las conclusiones a dos cosas distintas que suelen confundirse:

  - SENALES DE ALERTA: que medir, con que valor se enciende la alarma y que hacer
    cuando se enciende. Sirven para el proximo semestre, no para este.
  - ACCIONES: una por cada grupo identificado, con para quien y cuantos son, que
    hacer en concreto, en que hallazgo se apoya y como sabra el docente despues si
    funciono.

Las acciones se escriben AQUI. La etapa de visualizacion solo las muestra y tiene
prohibido inventarlas: un tablero que propone tareas que nadie decidio es un
tablero que nadie deberia seguir.

Si un grupo no necesita intervencion, se dice con todas las letras. Inventarle
una tarea a un grupo que va bien gasta el tiempo del docente en el lugar
equivocado.
"""

from estadistica import media


def _umbral_legible(valor):
    return "no se pudo calcular" if valor is None else f"{valor:.2f}"


def indicadores(senales, perfiles, relaciones, config):
    """Las senales de alerta, calibradas con los datos de ESTE curso."""
    lista = []

    rendimientos = [s.get("rendimiento") for s in senales]
    con_valor = sorted(v for v in rendimientos if v is not None)
    if con_valor:
        corte = con_valor[len(con_valor) // 4]
        lista.append({
            "que_medir": "rendimiento acumulado (escala 0 a 1)",
            "se_enciende_cuando": f"cae por debajo de {_umbral_legible(corte)}",
            "por_que_ese_valor": "es el cuarto inferior de este curso; con otro "
                                 "grupo el valor cambia y hay que recalcularlo",
            "que_hacer": "contacto directo antes de la siguiente evaluacion",
            "estudiantes_hoy": sum(1 for v in rendimientos
                                   if v is not None and v <= corte),
        })

    asistencias = [s.get("asistencia") for s in senales]
    if any(v is not None for v in asistencias):
        lista.append({
            "que_medir": "proporcion de clases a las que asiste",
            "se_enciende_cuando": "baja de 0.70, o acumula 3 ausencias seguidas",
            "por_que_ese_valor": "por debajo de ese punto la asistencia deja de "
                                 "ser irregular y pasa a ser retiro",
            "que_hacer": "preguntar directamente antes de que pase una semana mas",
            "estudiantes_hoy": sum(1 for v in asistencias
                                   if v is not None and v < 0.70),
        })

    plataformas = [s.get("plataforma") for s in senales]
    if any(v is not None for v in plataformas):
        lista.append({
            "que_medir": "actividad en el aula virtual (escala 0 a 1)",
            "se_enciende_cuando": "dos semanas sin ninguna entrada",
            "por_que_ese_valor": "es el aviso mas temprano de todos: aparece "
                                 "antes que la nota y antes que la falta",
            "que_hacer": "un mensaje breve; en esta etapa suele bastar",
            "estudiantes_hoy": sum(1 for v in plataformas
                                   if v is not None and v <= 0.10),
        })

    faltas = [s for s in senales if s.get("instrumentos_sin_registro", 0) >= 2]
    if faltas:
        lista.append({
            "que_medir": "evaluaciones sin registrar por estudiante",
            "se_enciende_cuando": "acumula 2 evaluaciones sin nota",
            "por_que_ese_valor": "dos ausencias seguidas rara vez son un olvido "
                                 "administrativo",
            "que_hacer": "confirmar si falto o si la nota no se cargo",
            "estudiantes_hoy": len(faltas),
        })

    return lista


def acciones(perfiles, hallazgos, resumen_curso, config):
    """Una accion por grupo, con los cuatro campos y su prioridad."""
    guion = {
        "Poca presencia y bajo resultado": (
            "urgente",
            "contacto individual esta semana: preguntar que esta pasando y "
            "acordar una sola tarea concreta de reingreso",
            "que la mitad del grupo entregue la siguiente evaluacion"),
        "Se esfuerza y aun asi no le sale": (
            "alta",
            "sesion de repaso enfocada en los temas donde perdieron mas puntos, "
            "no en la materia entera",
            "que su rendimiento suba en la siguiente evaluacion del mismo tipo"),
        "Rinde bien casi sin aparecer": (
            "media",
            "confirmar si el registro esta incompleto; si dominan la materia, "
            "ofrecerles algo mas exigente en lugar de mas de lo mismo",
            "que sus registros de participacion dejen de estar vacios"),
        "Constante y con buen resultado": (
            "baja",
            "NO necesita intervencion. Sostener lo que ya funciona.",
            "que el grupo siga del mismo tamano al cierre del semestre"),
        "En la media del curso": (
            "baja",
            "NO necesita intervencion especifica: se atiende con la clase regular.",
            "que ninguno pase al tercio bajo en la proxima evaluacion"),
        "Sin datos suficientes": (
            "alta",
            "revisar si les faltan registros por un problema de carga o porque "
            "dejaron de participar: hoy no se sabe cual de las dos cosas es",
            "que en la proxima corrida tengan datos completos"),
    }

    lista = []
    for perfil in perfiles:
        prioridad, que_hacer, como_se_sabe = guion.get(
            perfil["perfil"],
            ("media", "definir con el docente", "definir con el docente"))
        apoyo = next((h["hallazgo"] for h in hallazgos
                      if perfil["perfil"] in h.get("en_que_se_apoya", "")),
                     "clasificacion por perfiles de este mismo informe")
        lista.append({
            "prioridad": prioridad,
            "para_quien": perfil["perfil"],
            "cuantos": perfil["estudiantes"],
            "codigos": perfil["codigos"],
            "que_hacer": que_hacer,
            "en_que_hallazgo_se_apoya": apoyo,
            "como_sabre_si_funciono": como_se_sabe,
        })

    if resumen_curso["abandonos"]:
        lista.insert(0, {
            "prioridad": "urgente",
            "para_quien": "estudiantes que ya dejaron de participar",
            "cuantos": resumen_curso["abandonos"],
            "codigos": "",
            "que_hacer": "verificar uno por uno si el retiro es formal; los que "
                         "no lo formalizaron siguen contando como matriculados",
            "en_que_hallazgo_se_apoya": "El curso perdio estudiantes por el camino",
            "como_sabre_si_funciono": "que cada caso tenga una situacion "
                                      "administrativa definida antes del cierre",
        })

    orden = {"urgente": 0, "alta": 1, "media": 2, "baja": 3}
    lista.sort(key=lambda a: (orden.get(a["prioridad"], 9), -a["cuantos"]))
    return lista


def _por_que_ahi(s):
    """Cuando ninguna senal llega al umbral de alerta, igual hay que decir que
    lo puso en ese lugar: una lista ordenada sin motivo no se puede discutir."""
    partes = []
    for llave, etiqueta in (("rendimiento", "rendimiento"),
                            ("asistencia", "asistencia"),
                            ("plataforma", "actividad en el aula")):
        valor = s.get(llave)
        if valor is None:
            partes.append(f"sin dato de {etiqueta}")
        elif valor < 0.5:
            partes.append(f"{etiqueta} por debajo de la mitad ({valor:.2f})")
    if not partes:
        return "ninguna senal por debajo del umbral: aparece por el orden general"
    return "; ".join(partes) + " (sin llegar al umbral de alerta)"


def prioridades(senales, asignacion, config):
    """Todos los estudiantes ordenados por urgencia de atencion, con el motivo.

    El orden se construye con las senales disponibles: cada una que falta se
    descuenta del peso total, para que un estudiante sin datos no aparezca
    tranquilo solo porque no hay con que medirlo.
    """
    perfil_de = {a["codigo"]: a["perfil"] for a in asignacion}
    filas = []
    for s in senales:
        motivos, puntos, medidas = [], 0.0, 0

        if s["situacion"] == "abandono":
            puntos += 1.0
            medidas += 1
            motivos.append("figura como abandono")

        for llave, etiqueta, peso in (("rendimiento", "rendimiento bajo", 1.0),
                                      ("asistencia", "asistencia baja", 0.8),
                                      ("plataforma", "poca actividad en el aula", 0.6)):
            valor = s.get(llave)
            if valor is None:
                continue
            medidas += 1
            puntos += (1 - valor) * peso
            if valor <= 0.34:
                motivos.append(etiqueta)

        sin_registro = s.get("instrumentos_sin_registro", 0)
        if sin_registro >= 2:
            puntos += 0.5
            motivos.append(f"{sin_registro} evaluaciones sin registrar")

        filas.append({
            "codigo": s["codigo"],
            "urgencia": round(puntos, 4),
            "situacion": s["situacion"],
            "perfil": perfil_de.get(s["codigo"], ""),
            "senales_disponibles": medidas,
            "motivo": "; ".join(motivos) if motivos else _por_que_ahi(s),
        })

    filas.sort(key=lambda f: -f["urgencia"])
    for posicion, fila in enumerate(filas, start=1):
        fila["puesto"] = posicion
    return filas


def resumen_de_medidas(senales):
    return {
        "rendimiento_medio": media([s.get("rendimiento") for s in senales]),
        "asistencia_media": media([s.get("asistencia") for s in senales]),
        "plataforma_media": media([s.get("plataforma") for s in senales]),
    }
