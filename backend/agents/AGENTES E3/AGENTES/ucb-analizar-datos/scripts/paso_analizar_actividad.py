"""Paso: analizar_actividad

Mira el aula virtual como una linea de tiempo y no como un total: a que horas y
que dias se conectan los estudiantes, y como cambia la actividad cerca de las
fechas de entrega.

Si el archivo de registros no existe, este paso lo dice con todas las letras y el
analisis continua sin el. Lo que nunca hace es deducir la actividad de otras
columnas: un total de accesos no dice a que hora se conecto nadie, y fabricar esa
linea de tiempo seria inventar datos.
"""

import csv
from pathlib import Path

from paso_leer_depurada import a_momento, a_numero, normalizar

EXTENSIONES = (".xlsx", ".xlsm", ".csv")


def buscar_registros(carpeta_rev, config, carpeta_original=None):
    """Busca el archivo de registros del aula virtual.

    Mira en la carpeta -REV y TAMBIEN en la carpeta original de la materia. Antes
    solo miraba en -REV, donde nunca esta: la Etapa 1 deja ahi sus resultados,
    pero el registro descargado del aula sigue donde el docente lo puso. El
    efecto era que la linea de tiempo no se armaba nunca, en ninguna materia, y
    el informe decia «no se encontro» aunque el archivo estuviera al lado.
    """
    palabras = config["palabras"]["plataforma"]
    candidatos = []
    lugares = [Path(carpeta_rev)]
    if carpeta_original and Path(carpeta_original).is_dir():
        lugares.append(Path(carpeta_original))
    for ruta in sorted(r for lugar in lugares for r in lugar.rglob("*")):
        if not ruta.is_file() or ruta.suffix.lower() not in EXTENSIONES:
            continue
        if ruta.name.startswith("~$"):
            continue
        plano = normalizar(ruta.stem).replace("_", " ").replace("-", " ")
        plano = " ".join(plano.split())
        if any(p in plano for p in palabras):
            candidatos.append(ruta)
    # Se prefiere el archivo mas grande: el detalle de eventos pesa mucho mas que
    # una tabla de totales.
    candidatos.sort(key=lambda r: r.stat().st_size, reverse=True)
    return candidatos[0] if candidatos else None


def _leer_tabla(ruta):
    if ruta.suffix.lower() == ".csv":
        with open(ruta, "r", encoding="utf-8", errors="ignore", newline="") as f:
            muestra = f.read(4096)
            f.seek(0)
            try:
                dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t|")
            except csv.Error:
                dialecto = csv.excel
            lector = csv.reader(f, dialecto)
            filas = [fila for fila in lector]
        if not filas:
            return [], []
        return filas[0], filas[1:]

    import openpyxl
    libro = openpyxl.load_workbook(ruta, data_only=True, read_only=True)
    hoja = libro[libro.sheetnames[0]]
    filas = [list(f) for f in hoja.iter_rows(values_only=True)]
    libro.close()
    if not filas:
        return [], []
    return [str(c) if c is not None else "" for c in filas[0]], filas[1:]


def _columna_de_momento(columnas, filas):
    """La columna que contiene la fecha y hora de cada evento."""
    mejor, mejor_aciertos = None, 0
    for indice in range(len(columnas)):
        aciertos = 0
        for fila in filas[:200]:
            if indice < len(fila) and a_momento(fila[indice]) is not None:
                aciertos += 1
        if aciertos > mejor_aciertos:
            mejor, mejor_aciertos = indice, aciertos
    if mejor is None or mejor_aciertos < 5:
        return None
    return mejor


def analizar(carpeta_rev, config, carpeta_original=None):
    """Devuelve la linea de tiempo del aula, o la explicacion de por que no hay."""
    ruta = buscar_registros(carpeta_rev, config, carpeta_original)
    if ruta is None:
        return {
            "disponible": False,
            "por_que": "no se encontro ningun archivo de registros del aula "
                       "virtual, ni en la carpeta -REV ni en la de la materia. "
                       "El analisis "
                       "continua sin la linea de tiempo; no se dedujo de otras "
                       "columnas porque un total de accesos no dice a que hora "
                       "se conecto nadie.",
            "por_hora": [], "por_dia": [], "eventos": 0,
        }

    columnas, filas = _leer_tabla(ruta)
    indice = _columna_de_momento(columnas, filas) if columnas else None
    if indice is None:
        return {
            "disponible": False,
            "archivo": ruta.name,
            "por_que": f"se encontro «{ruta.name}», pero ninguna de sus columnas "
                       "contiene fecha y hora, asi que no se puede armar una "
                       "linea de tiempo. Exporte el registro con la columna de "
                       "fecha completa.",
            "por_hora": [], "por_dia": [], "eventos": 0,
        }

    dias_semana = ["lunes", "martes", "miercoles", "jueves", "viernes",
                   "sabado", "domingo"]
    por_hora = {h: 0 for h in range(24)}
    por_dia = {d: 0 for d in dias_semana}
    por_fecha = {}
    for fila in filas:
        if indice >= len(fila):
            continue
        momento = a_momento(fila[indice])
        if momento is None:
            continue
        por_hora[momento.hour] += 1
        por_dia[dias_semana[momento.weekday()]] += 1
        clave = momento.date()
        por_fecha[clave] = por_fecha.get(clave, 0) + 1

    eventos = sum(por_hora.values())
    if not eventos:
        return {"disponible": False, "archivo": ruta.name,
                "por_que": "el archivo no tiene ningun evento con fecha valida",
                "por_hora": [], "por_dia": [], "eventos": 0}

    madrugada = sum(por_hora[h] for h in range(0, 6))
    fin_de_semana = por_dia["sabado"] + por_dia["domingo"]
    pico = max(por_hora.items(), key=lambda x: x[1])

    observaciones = []
    if madrugada:
        observaciones.append({
            "observacion": "actividad de madrugada (00:00 a 06:00)",
            "cifra": f"{madrugada} de {eventos} eventos ({madrugada / eventos:.1%})",
        })
    if fin_de_semana:
        observaciones.append({
            "observacion": "actividad en fin de semana",
            "cifra": f"{fin_de_semana} de {eventos} eventos "
                     f"({fin_de_semana / eventos:.1%})",
        })
    observaciones.append({
        "observacion": "hora de mayor actividad",
        "cifra": f"{pico[0]:02d}:00 h, con {pico[1]} eventos",
    })

    return {
        "disponible": True,
        "archivo": ruta.name,
        "eventos": eventos,
        "estudiantes_o_filas": len(filas),
        "por_hora": [{"hora": f"{h:02d}:00", "eventos": por_hora[h]}
                     for h in range(24)],
        "por_dia": [{"dia": d, "eventos": por_dia[d]} for d in dias_semana],
        "por_fecha": [{"fecha": str(f), "eventos": n}
                      for f, n in sorted(por_fecha.items())],
        "observaciones": observaciones,
    }
