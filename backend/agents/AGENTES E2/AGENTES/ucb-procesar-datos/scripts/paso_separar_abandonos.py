"""Paso: separar_abandonos

Un curso tiene dos grupos distintos y mezclarlos engaña: el promedio de la materia
baja por gente que dejo de venir en abril, y el docente cree que enseño peor de lo
que enseño.

Este paso los separa. NO borra a nadie: los mueve a una hoja aparte y explica, para
cada persona, por que quedo de ese lado.

Por que no basta una sola columna de estado:
    Puede decir 'Activo' para alguien que dejo de venir hace dos meses. Nadie
    actualiza esa columna a mitad de semestre. Por eso se cruzan varias señales
    independientes y se exige que coincidan.

Las señales que se miran:
    1. desde que fecha se corta su secuencia cronologica de asistencia;
    2. su fecha de ultimo acceso al aula virtual;
    3. desde cuando dejan de registrarse sus evaluaciones;
    4. en cuantos archivos del curso no figura, segun la hoja COBERTURA.

Un cuidado que decide el resultado: hace falta la secuencia de clases COMPLETA y
en orden, incluidas aquellas a las que fueron todos. Si se descartan esas columnas
por no tener variacion, se rompe la cronologia que sirve justamente para ver desde
cuando alguien falta.

Y una excepcion: si alguien no tiene registro en NINGUNA evaluacion, esa sola señal
alcanza. No es que haya dejado de participar; es que nunca aparecio.
"""

import datetime as _dt
import re

from paso_leer_base import FECHA, NUMERO, VACIO, a_numero, tipo_de

PATRON_FECHA = re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})")
PATRON_FECHA_INV = re.compile(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})")
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
         "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12}


def fecha_de_texto(texto):
    """Saca una fecha de un titulo de columna o de una celda, si la hay."""
    # datetime es subclase de date, asi que hay que preguntar por datetime
    # PRIMERO. Al reves, una celda con fecha y hora se devolvia sin convertir y
    # despues reventaba al compararla con una fecha sin hora.
    if isinstance(texto, _dt.datetime):
        return texto.date()
    if isinstance(texto, _dt.date):
        return texto
    bruto = str(texto or "")
    m = PATRON_FECHA.search(bruto)
    if m:
        try:
            return _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = PATRON_FECHA_INV.search(bruto)
    if m:
        try:
            return _dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    m = re.search(r"(\d{1,2})[-\s]([a-zA-Z]{3})[a-zA-Z]*[-\s](\d{2,4})", bruto)
    if m:
        mes = MESES.get(m.group(2)[:3].lower())
        if mes:
            anio = int(m.group(3))
            anio = anio + 2000 if anio < 100 else anio
            try:
                return _dt.date(anio, mes, int(m.group(1)))
            except ValueError:
                return None
    return None


def _columnas_con_fecha(columnas):
    """Columnas cuyo titulo lleva una fecha, ordenadas cronologicamente.

    Se conservan TODAS, incluidas aquellas donde nadie falto: son las que
    sostienen la cronologia.
    """
    por_fecha = {}
    for indice, nombre in enumerate(columnas):
        fecha = fecha_de_texto(nombre)
        if not fecha:
            continue
        # Una misma clase puede aparecer dos veces: la columna original y la copia
        # que otro paso genero al convertirla. Se queda UNA por fecha, porque si no
        # el conteo de clases perdidas sale al doble y el docente lee un numero que
        # no se corresponde con su curso.
        if fecha not in por_fecha:
            por_fecha[fecha] = (fecha, indice, nombre)
    return sorted(por_fecha.values())


def _ultima_presencia(fila, fechadas, marcas_presente):
    """La ultima fecha en la que hay señal de que el estudiante estuvo.

    Se reconoce la presencia por LISTA BLANCA, nunca por descarte. Si se contara
    como presente todo lo que no sea una falta conocida, cualquier texto que otro
    paso haya escrito en la celda —un 'Sin registro', por ejemplo— pasaria por
    asistencia y correria la ultima presencia hasta el final del curso. Con eso,
    quien dejo de venir en abril parece haber cursado hasta junio.
    """
    ultima = None
    for fecha, indice, _ in fechadas:
        valor = fila[indice]
        if tipo_de(valor) == VACIO:
            continue
        numero = a_numero(valor)
        if numero is not None:
            presente = numero > 0
        else:
            presente = str(valor).strip().lower() in marcas_presente
        if presente:
            ultima = fecha
    return ultima


def _ultimo_acceso(fila, columnas):
    """La fecha mas reciente que aparezca en columnas de tipo fecha."""
    ultima = None
    for indice, nombre in enumerate(columnas):
        valor = fila[indice]
        if tipo_de(valor) != FECHA and not isinstance(valor, str):
            continue
        fecha = fecha_de_texto(valor)
        if fecha and (ultima is None or fecha > ultima):
            ultima = fecha
    return ultima


def _columnas_de_evaluacion(columnas, filas, fechadas, config):
    """Columnas numericas que parecen calificaciones, no asistencia ni contadores."""
    de_asistencia = {i for _, i, _ in fechadas}
    minimo = config["minimo_datos_para_estadistica"]
    indices = []
    for indice, nombre in enumerate(columnas):
        if indice in de_asistencia:
            continue
        valores = [a_numero(f[indice]) for f in filas]
        llenos = [v for v in valores if v is not None]
        if len(llenos) < minimo:
            continue
        tipos = [tipo_de(f[indice]) for f in filas]
        con_dato = [t for t in tipos if t != VACIO]
        if not con_dato or sum(1 for t in con_dato if t == NUMERO) < len(con_dato) * 0.8:
            continue
        # Una columna de 0 y 1 es asistencia convertida, no una calificacion.
        if set(llenos) <= {0.0, 0.5, 1.0}:
            continue
        indices.append(indice)
    return indices


def diagnosticar(columnas, filas, cobertura, config):
    """Que señales se pueden evaluar en ESTA base, y cuales no.

    Existe porque el riesgo mas serio de este paso es callarse. Si la asistencia
    no lleva fechas en el titulo de sus columnas, o el curso no uso el aula
    virtual, la señal correspondiente no se puede medir y la separacion devuelve
    cero. Sin este aviso, el docente leeria 'ningun abandono' y creeria que su
    curso no tuvo ninguno, cuando en realidad nadie lo comprobo.
    """
    fechadas = _columnas_con_fecha(columnas)
    evaluaciones = _columnas_de_evaluacion(columnas, filas, fechadas, config)
    con_fecha_valor = 0
    for fila in filas[:5]:
        if _ultimo_acceso(fila, columnas):
            con_fecha_valor += 1
    archivos = len({str(r.get("archivo", "") or "").strip() for r in cobertura})

    señales = [
        ("secuencia de asistencia", len(fechadas) >= 3,
         f"{len(fechadas)} columna(s) con fecha en el titulo",
         "ninguna columna de asistencia tiene una fecha en su titulo, asi que no "
         "hay cronologia que seguir"),
        ("ultimo acceso al aula virtual", con_fecha_valor > 0,
         "hay columnas con fecha y hora",
         "no se encontro ninguna fecha de actividad: el curso no dejo registro "
         "en la plataforma, o no se descargo"),
        ("evaluaciones sin registrar", len(evaluaciones) >= 3,
         f"{len(evaluaciones)} columna(s) de calificacion",
         "no hay suficientes columnas de calificacion para ver desde cuando "
         "alguien deja de rendir"),
        ("ausencias en los archivos", archivos >= 2,
         f"cobertura de {archivos} archivo(s)",
         "la hoja COBERTURA no vino o cubre un solo archivo"),
    ]

    disponibles = [n for n, ok, _, _ in señales if ok]
    return {
        "señales": [{"señal": n, "disponible": "si" if ok else "NO",
                     "detalle": bien if ok else mal}
                    for n, ok, bien, mal in señales],
        "disponibles": len(disponibles),
        "minimo": config["senales_minimas_para_abandono"],
        "fiable": len(disponibles) >= config["senales_minimas_para_abandono"],
    }


def proponer(columnas, filas, indice_clave, cobertura, config):
    """Decide quien abandono y por que. Devuelve la lista de propuestas.

    No mueve nada: esta es la tabla D que el docente aprueba en la segunda pausa.
    """
    fechadas = _columnas_con_fecha(columnas)
    evaluaciones = _columnas_de_evaluacion(columnas, filas, fechadas, config)
    # Solo estas palabras cuentan como haber estado en clase.
    marcas_presente = {str(p).strip().lower()
                       for valor, palabras in config["marcas_asistencia"].items()
                       if float(valor) > 0 for p in palabras}
    minimo_senales = config["senales_minimas_para_abandono"]
    proporcion = config["proporcion_ausencias_para_abandono"]

    ausencias_por_codigo = {}
    for registro in cobertura:
        codigo = str(registro.get("id_estudiante", "") or "").strip()
        if str(registro.get("situacion", "") or "").strip() == "ausente":
            ausencias_por_codigo[codigo] = ausencias_por_codigo.get(codigo, 0) + 1
    archivos_distintos = len({str(r.get("archivo", "") or "").strip()
                              for r in cobertura}) or 1

    ultima_clase = fechadas[-1][0] if fechadas else None
    propuestas = []

    for fila in filas:
        codigo = str(fila[indice_clave]).strip()
        senales, motivos = 0, []

        # --- señal 0 (decisiva por si sola): nunca aparecio -----------------
        con_evaluacion = sum(1 for i in evaluaciones
                             if tipo_de(fila[i]) != VACIO)
        if evaluaciones and con_evaluacion == 0:
            propuestas.append({
                "codigo": codigo,
                "motivo": "no tiene registro en ninguna evaluacion",
                "desde": "",
                "senales": "1 (decisiva)",
                "detalle": "no es que haya dejado de participar: nunca aparecio "
                           "en el curso",
            })
            continue

        # --- señal 1: se corta su secuencia de asistencia -------------------
        ultima = _ultima_presencia(fila, fechadas, marcas_presente)
        if fechadas:
            if ultima is None:
                senales += 1
                motivos.append("no figura presente en ninguna clase")
            elif ultima_clase and ultima < ultima_clase:
                faltadas = sum(1 for f, _, _ in fechadas if f > ultima)
                if faltadas >= len(fechadas) * (1 - proporcion) and faltadas >= 2:
                    senales += 1
                    motivos.append(f"dejo de asistir despues del "
                                   f"{ultima.isoformat()} ({faltadas} clases sin venir)")

        # --- señal 2: su ultimo acceso al aula virtual ----------------------
        acceso = _ultimo_acceso(fila, columnas)
        if acceso and ultima_clase and acceso < ultima_clase:
            dias = (ultima_clase - acceso).days
            if dias >= 21:
                senales += 1
                motivos.append(f"ultimo acceso al aula virtual el "
                               f"{acceso.isoformat()}, {dias} dias antes de la "
                               f"ultima clase")

        # --- señal 3: dejan de registrarse sus evaluaciones -----------------
        if evaluaciones:
            faltan = len(evaluaciones) - con_evaluacion
            if faltan >= len(evaluaciones) * proporcion:
                senales += 1
                motivos.append(f"sin nota en {faltan} de {len(evaluaciones)} "
                               f"evaluaciones")

        # --- señal 4: no figura en varios archivos del curso ----------------
        ausente_en = ausencias_por_codigo.get(codigo, 0)
        if archivos_distintos and ausente_en >= archivos_distintos * proporcion:
            senales += 1
            motivos.append(f"no figura en {ausente_en} de {archivos_distintos} "
                           f"archivos del curso")

        if senales >= minimo_senales:
            propuestas.append({
                "codigo": codigo,
                "motivo": "; ".join(motivos),
            # Se guarda aparte, ademas de dentro del motivo: la etapa de
            # analisis necesita compararla con la fecha de la ultima clase, y
            # sacarla de una frase escrita seria adivinar.
            "ultimo_acceso": acceso.isoformat() if acceso else "",
                "desde": ultima.isoformat() if ultima else "",
                "senales": str(senales),
                "detalle": f"coinciden {senales} señales independientes",
            })

    return propuestas


def aplicar(filas, indice_clave, propuestas, excluidos, forzados):
    """Reparte las filas en activos y abandonos, respetando el veto del docente.

    Devuelve (activos, abandonos, decisiones) donde decisiones explica cada caso
    para la hoja ABANDONOS.
    """
    excluidos = {str(c).strip() for c in excluidos}
    forzados = {str(c).strip() for c in forzados}

    propuesto = {p["codigo"]: p for p in propuestas}
    activos, abandonos, decisiones = [], [], []

    for fila in filas:
        codigo = str(fila[indice_clave]).strip()
        p = propuesto.get(codigo)

        if codigo in forzados:
            abandonos.append(fila)
            decisiones.append({
                "codigo": codigo,
                "motivo": (p["motivo"] if p else
                           "el docente lo indico expresamente"),
                "desde": p["desde"] if p else "",
                "ultimo_acceso": p.get("ultimo_acceso", "") if p else "",
                "senales": p["senales"] if p else "decision del docente",
                "quien_decidio": "el docente",
            })
        elif p and codigo not in excluidos:
            abandonos.append(fila)
            decisiones.append({
                "codigo": codigo,
                "motivo": p["motivo"],
                "desde": p["desde"],
                "ultimo_acceso": p.get("ultimo_acceso", ""),
                "senales": p["senales"],
                "quien_decidio": "el programa, aprobado por el docente",
            })
        else:
            activos.append(fila)
            if p and codigo in excluidos:
                decisiones.append({
                    "codigo": codigo,
                    "motivo": p["motivo"],
                    "desde": p["desde"],
                    "senales": p["senales"],
                    "quien_decidio": "SE QUEDA EN ACTIVOS por decision del docente",
                })

    return activos, abandonos, decisiones
