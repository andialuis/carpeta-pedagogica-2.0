"""Paso: detectar_perfiles

Encuentra los grupos que el promedio esconde: el que participa mucho y aun asi
reprueba, el que casi no entra a la plataforma y le va bien.

Para agrupar no se usa una sola senal. Un estudiante puede faltar a clase y estar
todos los dias en el aula virtual, o entregarlo todo y no rendir en los examenes:
mirando una sola columna, los tres casos parecen el mismo. Aqui se combinan
asistencia, actividad en la plataforma, entregas y resultado.

Los perfiles se arman con reglas y no con un algoritmo de agrupamiento
automatico, por dos razones: el resultado es el mismo en cualquier computadora, y
cada perfil se puede explicar al docente en una frase. Un grupo que no se puede
explicar no sirve para decidir nada en el aula.
"""

from estadistica import media


def _nivel(valor, corte_bajo, corte_alto):
    if valor is None:
        return None
    if valor <= corte_bajo:
        return "bajo"
    if valor >= corte_alto:
        return "alto"
    return "medio"


def _cortes(valores):
    llenos = sorted(v for v in valores if v is not None)
    if len(llenos) < 3:
        return None, None
    return llenos[len(llenos) // 3], llenos[2 * len(llenos) // 3]


PERFILES = {
    ("alto", "bajo"): (
        "Se esfuerza y aun asi no le sale",
        "asiste y participa por encima del curso, pero su resultado esta en la "
        "parte baja. Suele ser un problema de comprension, no de compromiso."),
    ("bajo", "alto"): (
        "Rinde bien casi sin aparecer",
        "resultado alto con muy poca presencia y poca actividad registrada. "
        "Conviene mirar si tiene la materia dominada o si algo no esta quedando "
        "registrado."),
    ("alto", "alto"): (
        "Constante y con buen resultado",
        "presencia alta y resultado alto: el grupo que sostiene el curso."),
    ("bajo", "bajo"): (
        "Poca presencia y bajo resultado",
        "el perfil de mayor riesgo: ni aparece ni aprueba. Es donde una "
        "intervencion temprana cambia mas."),
}


def detectar(senales, config):
    """Devuelve (perfiles, asignacion_por_estudiante, avisos)."""
    avisos = []

    # El esfuerzo combina lo que este disponible: si la materia no registra
    # plataforma, se arma con asistencia y entregas, y se dice cual falto.
    disponibles = []
    for llave, etiqueta in (("asistencia", "asistencia"),
                            ("plataforma", "actividad en la plataforma")):
        if any(s.get(llave) is not None for s in senales):
            disponibles.append(llave)
        else:
            avisos.append(f"no se pudo usar {etiqueta} para armar los perfiles: "
                          "la base no trae esa senal")

    if not disponibles:
        return [], [], avisos + [
            "no se pudieron armar perfiles: hace falta al menos una senal de "
            "participacion (asistencia o actividad en la plataforma)"]

    esfuerzo = []
    for s in senales:
        valores = [s.get(l) for l in disponibles if s.get(l) is not None]
        esfuerzo.append(round(sum(valores) / len(valores), 4) if valores else None)

    corte_e_bajo, corte_e_alto = _cortes(esfuerzo)
    corte_r_bajo, corte_r_alto = _cortes([s.get("rendimiento") for s in senales])
    if corte_e_bajo is None or corte_r_bajo is None:
        return [], [], avisos + [
            "el curso es demasiado pequeno para separar perfiles con sentido"]

    asignacion = []
    for s, e in zip(senales, esfuerzo):
        nivel_e = _nivel(e, corte_e_bajo, corte_e_alto)
        nivel_r = _nivel(s.get("rendimiento"), corte_r_bajo, corte_r_alto)
        nombre, descripcion = PERFILES.get(
            (nivel_e, nivel_r),
            ("En la media del curso",
             "no se aparta de forma clara ni en participacion ni en resultado"))
        if nivel_e is None or nivel_r is None:
            nombre, descripcion = (
                "Sin datos suficientes",
                "le faltan registros para ubicarlo: revise si es un problema de "
                "captura o si dejo de participar")
        asignacion.append({
            "codigo": s["codigo"],
            "perfil": nombre,
            "situacion": s["situacion"],
            "esfuerzo": e,
            "rendimiento": s.get("rendimiento"),
        })

    agrupados = {}
    for a in asignacion:
        agrupados.setdefault(a["perfil"], []).append(a)

    significado = {n: d for n, d in PERFILES.values()}
    significado["En la media del curso"] = (
        "no se aparta de forma clara ni en participacion ni en resultado")
    significado["Sin datos suficientes"] = (
        "le faltan registros para ubicarlo: revise si es un problema de captura "
        "o si dejo de participar")

    perfiles = []
    for nombre, miembros in agrupados.items():
        perfiles.append({
            "perfil": nombre,
            "estudiantes": len(miembros),
            "codigos": ", ".join(m["codigo"] for m in miembros),
            "rendimiento_medio": (
                round(media([m["rendimiento"] for m in miembros]), 4)
                if any(m["rendimiento"] is not None for m in miembros) else None),
            "esfuerzo_medio": (round(media([m["esfuerzo"] for m in miembros]), 4)
                               if any(m["esfuerzo"] is not None for m in miembros)
                               else None),
            "abandonos_en_el_perfil": sum(1 for m in miembros
                                          if m["situacion"] == "abandono"),
            "que_significa": significado.get(nombre, ""),
        })

    perfiles.sort(key=lambda p: -p["estudiantes"])
    if len(disponibles) == 1:
        avisos.append(
            f"los perfiles se armaron con una sola senal de participacion "
            f"({disponibles[0]}): son mas gruesos de lo que serian con las dos")
    return perfiles, asignacion, avisos
