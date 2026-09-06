"""Paso: verificar

Toma una fotografia de como se relacionan entre si las columnas numericas ANTES de
tocar nada, y vuelve a mirarlas al final.

Para que sirve: la limpieza puede alterar lo que los datos decian sin que nadie se
de cuenta. Si dos columnas iban juntas antes y van al reves despues, algo se rompio
en el camino y hay que avisarlo de forma destacada.

Una advertencia que decide el resultado: la comparacion final se hace sobre EL
MISMO CONJUNTO de estudiantes que la inicial, activos y abandonos juntos. Si se
comparara solo contra los que quedaron, las relaciones cambiarian por haber
separado a los que se fueron, y se daria una falsa alarma.

Usa solo la biblioteca estandar: ninguna correlacion depende de que este instalada
una libreria opcional.
"""

from paso_leer_base import NUMERO, VACIO, a_numero, tipo_de


def _columnas_numericas(columnas, filas, minimo):
    """Indices de las columnas que se comportan como numero."""
    indices = []
    for indice in range(len(columnas)):
        valores = [a_numero(f[indice]) for f in filas]
        llenos = [v for v in valores if v is not None]
        if len(llenos) < minimo:
            continue
        tipos = [tipo_de(f[indice]) for f in filas]
        con_dato = [t for t in tipos if t != VACIO]
        if con_dato and sum(1 for t in con_dato if t == NUMERO) >= len(con_dato) * 0.8:
            indices.append(indice)
    return indices


def _correlacion(x, y):
    """Correlacion de Pearson entre dos listas ya emparejadas."""
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def _resumen_columna(valores):
    llenos = [v for v in valores if v is not None]
    if not llenos:
        return None
    n = len(llenos)
    return {
        "n": n,
        "media": round(sum(llenos) / n, 4),
        "minimo": round(min(llenos), 4),
        "maximo": round(max(llenos), 4),
    }


def fotografiar(columnas, filas, clave, config):
    """Devuelve el estado de las relaciones numericas en este momento.

    Se indexa por el valor de la columna clave para poder comparar despues aunque
    las filas hayan cambiado de orden o se hayan repartido en dos hojas.
    """
    minimo = config["minimo_datos_para_estadistica"]
    indices = _columnas_numericas(columnas, filas, minimo)

    resumenes, series = {}, {}
    for indice in indices:
        nombre = columnas[indice]
        por_estudiante = {}
        for fila in filas:
            por_estudiante[str(fila[clave]).strip()] = a_numero(fila[indice])
        series[nombre] = por_estudiante
        resumen = _resumen_columna(list(por_estudiante.values()))
        if resumen:
            resumenes[nombre] = resumen

    relaciones = {}
    nombres = sorted(series)
    umbral = config["umbral_correlacion_relevante"]
    for i, uno in enumerate(nombres):
        for otro in nombres[i + 1:]:
            comunes = [(series[uno][k], series[otro][k]) for k in series[uno]
                       if series[uno].get(k) is not None
                       and series[otro].get(k) is not None]
            if len(comunes) < 3:
                continue
            r = _correlacion([a for a, _ in comunes], [b for _, b in comunes])
            if r is None or abs(r) < umbral:
                continue
            relaciones[(uno, otro)] = round(r, 4)

    return {"resumenes": resumenes, "relaciones": relaciones,
            "columnas": nombres}


def comparar(antes, despues, config):
    """Confronta las dos fotografias y devuelve las filas de la hoja VERIFICACION.

    Marca tres cosas distintas:
      - la relacion cambio de signo (lo mas grave: los datos dicen lo contrario);
      - la relacion se movio mas de lo tolerable sin cambiar de signo;
      - la relacion desaparecio porque la columna dejo de ser comparable.
    """
    tolerancia = config["diferencia_para_avisar_cambio_de_sentido"]
    filas, alertas = [], 0

    for par in sorted(antes["relaciones"], key=lambda p: (p[0], p[1])):
        uno, otro = par
        valor_antes = antes["relaciones"][par]
        valor_despues = despues["relaciones"].get(par)

        if valor_despues is None:
            filas.append({
                "columna_a": uno, "columna_b": otro,
                "relacion_antes": valor_antes, "relacion_despues": "",
                "veredicto": "ya no se puede comparar",
                "detalle": "una de las dos columnas dejo de tener suficientes "
                           "valores numericos despues de la depuracion",
            })
            alertas += 1
            continue

        cambio_de_signo = (valor_antes > 0) != (valor_despues > 0)
        diferencia = abs(valor_antes - valor_despues)

        if cambio_de_signo:
            veredicto = "CAMBIO DE SENTIDO"
            detalle = ("antes iban en un sentido y ahora en el contrario: la "
                       "depuracion altero lo que los datos decian. REVISAR.")
            alertas += 1
        elif diferencia > tolerancia:
            veredicto = "se movio"
            detalle = f"la relacion cambio {diferencia:.2f} sin invertirse"
            alertas += 1
        else:
            veredicto = "estable"
            detalle = ""

        filas.append({
            "columna_a": uno, "columna_b": otro,
            "relacion_antes": valor_antes, "relacion_despues": valor_despues,
            "veredicto": veredicto, "detalle": detalle,
        })

    return filas, alertas
