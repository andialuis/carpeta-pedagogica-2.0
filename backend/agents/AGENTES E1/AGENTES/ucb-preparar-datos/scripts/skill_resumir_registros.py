"""Skill: resumir_registros

Un archivo de registros del aula virtual no es una planilla de notas: tiene miles de
filas y cada estudiante aparece muchas veces. Integrarlo fila por fila no tiene
sentido; hay que resumirlo por estudiante.

Este skill detecta ese tipo de archivo y produce, para cada persona: cuantas veces
aparece, cuando fue su primer y su ultimo registro, en cuantos dias distintos tuvo
actividad, en que franja horaria se conecta mas, y cuantas veces hizo cada tipo de
accion.

El archivo original NO se modifica ni se reduce: se queda entero en bases_de_datos.
"""

import datetime as _dt

from skill_leer_planillas import VACIO, _tipo

FORMATOS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y %H:%M:%S")

FRANJAS = ((0, 5, "madrugada (00-05)"), (6, 11, "manana (06-11)"),
           (12, 18, "tarde (12-18)"), (19, 23, "noche (19-23)"))


def a_fecha(valor):
    if isinstance(valor, _dt.datetime):
        return valor
    if isinstance(valor, _dt.date):
        return _dt.datetime(valor.year, valor.month, valor.day)
    if not isinstance(valor, str):
        return None
    texto = valor.strip()
    for formato in FORMATOS:
        try:
            return _dt.datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


def _columna_fecha(hoja):
    mejor, mejor_conteo = None, 0
    for indice in range(len(hoja["columnas"])):
        conteo = sum(1 for f in hoja["filas"][:200] if a_fecha(f[indice]) is not None)
        if conteo > mejor_conteo:
            mejor, mejor_conteo = indice, conteo
    return mejor if mejor_conteo >= min(20, len(hoja["filas"])) else None


def _columna_categoria(hoja, excluidas):
    """Una columna de texto con pocos valores distintos: el tipo de accion."""
    mejor, mejor_puntaje = None, 0
    for indice in range(len(hoja["columnas"])):
        if indice in excluidas:
            continue
        valores = [str(f[indice]).strip() for f in hoja["filas"]
                   if _tipo(f[indice]) == "texto"]
        if len(valores) < len(hoja["filas"]) * 0.8:
            continue
        distintos = len(set(valores))
        if 1 < distintos <= 10 and distintos > mejor_puntaje:
            mejor, mejor_puntaje = indice, distintos
    return mejor


def parece_registro_de_actividad(hoja, claves_unicas, total_estudiantes):
    """Muchas filas y pocas identidades distintas: es un registro, no una planilla."""
    filas = len(hoja["filas"])
    if filas < max(60, total_estudiantes * 3):
        return False
    if claves_unicas == 0:
        return False
    return filas / claves_unicas >= 3


def resumir(hoja, clave_identidad, reconocedor, etiqueta):
    """Devuelve (columnas, valores_por_estudiante, incidencias)."""
    incidencias = []
    col_fecha = _columna_fecha(hoja)
    col_categoria = _columna_categoria(hoja, set(clave_identidad) |
                                       ({col_fecha} if col_fecha is not None else set()))

    if col_fecha is None:
        incidencias.append({
            "tipo": "registro_sin_columna_de_fecha",
            "archivo": etiqueta,
            "detalle": "no se reconocio ninguna columna con fecha y hora; el resumen "
                       "solo contara eventos",
        })

    categorias = sorted({str(f[col_categoria]).strip() for f in hoja["filas"]
                         }) if col_categoria is not None else []

    columnas = [f"[{etiqueta}] Total de registros",
                f"[{etiqueta}] Primer registro",
                f"[{etiqueta}] Ultimo registro",
                f"[{etiqueta}] Dias distintos con actividad",
                f"[{etiqueta}] Franja horaria mas frecuente"]
    columnas += [f"[{etiqueta}] Veces: {c}" for c in categorias]

    acumulado, sin_reconocer = {}, {}
    for fila in hoja["filas"]:
        crudo = " ".join(str(fila[i]).strip() for i in clave_identidad
                         if fila[i] is not None and str(fila[i]).strip())
        est, _, _, _ = reconocedor.buscar(crudo)
        if est is None:
            sin_reconocer[crudo] = sin_reconocer.get(crudo, 0) + 1
            continue
        datos = acumulado.setdefault(est["id"], {
            "total": 0, "fechas": [], "dias": set(), "horas": [], "categorias": {}})
        datos["total"] += 1
        if col_fecha is not None:
            momento = a_fecha(fila[col_fecha])
            if momento:
                datos["fechas"].append(momento)
                datos["dias"].add(momento.date())
                datos["horas"].append(momento.hour)
        if col_categoria is not None and _tipo(fila[col_categoria]) != VACIO:
            clave = str(fila[col_categoria]).strip()
            datos["categorias"][clave] = datos["categorias"].get(clave, 0) + 1

    for crudo, veces in sorted(sin_reconocer.items(), key=lambda x: -x[1]):
        incidencias.append({
            "tipo": "identidad_del_registro_no_reconocida",
            "archivo": etiqueta,
            "valor_original": crudo,
            "detalle": f"aparece {veces} vez(veces) en el registro y no corresponde a "
                       f"ningun estudiante de la lista oficial",
        })

    valores = {}
    for id_estudiante, datos in acumulado.items():
        franja = ""
        if datos["horas"]:
            conteo = {}
            for hora in datos["horas"]:
                nombre = next(n for inicio, fin, n in FRANJAS if inicio <= hora <= fin)
                conteo[nombre] = conteo.get(nombre, 0) + 1
            franja = max(sorted(conteo.items()), key=lambda x: x[1])[0]
        fila = {
            columnas[0]: datos["total"],
            columnas[1]: min(datos["fechas"]).strftime("%Y-%m-%d %H:%M:%S") if datos["fechas"] else "",
            columnas[2]: max(datos["fechas"]).strftime("%Y-%m-%d %H:%M:%S") if datos["fechas"] else "",
            columnas[3]: len(datos["dias"]),
            columnas[4]: franja,
        }
        for categoria in categorias:
            fila[f"[{etiqueta}] Veces: {categoria}"] = datos["categorias"].get(categoria, 0)
        valores[id_estudiante] = fila

    return columnas, valores, incidencias
