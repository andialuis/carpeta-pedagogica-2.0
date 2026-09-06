"""Paso: clasificar_estudiantes

Mira al curso COMPLETO — activos y abandonos juntos — y responde dos cosas antes
de cualquier analisis: cuanto rindio cada estudiante y en que grupo cae.

La medida de rendimiento que se construye aqui NO es la nota oficial. Es una
variable de analisis, armada para poder cruzar instrumentos que estan en escalas
distintas. La nota oficial la pone el docente; el programa nunca la calcula ni la
sustituye.
"""

from estadistica import media, normalizar_0_1
from paso_leer_depurada import (ASISTENCIA, NOTA, PLATAFORMA, a_numero,
                                de_papel, normalizar, serie)


def _repartir_pesos(columnas_nota, reglas):
    """Reparte el puntaje que declara el silabo entre las columnas de la base.

    Dos correcciones que cambian por completo la medida de rendimiento:

      - Un instrumento que vale 30 puntos y se evaluo en tres practicas vale 30
        EN TOTAL, no 30 por practica. Antes cada practica se llevaba los 30
        enteros y el laboratorio terminaba pesando el 80% del rendimiento en vez
        del 30% que le daba el silabo.
      - El puntaje declarado que no encontro columna se reparte entre las
        columnas que no encontraron regla. Si el silabo dice «Primer parcial 30»
        y la planilla titula esa columna «1er Parcial», el nombre no coincide
        pero los 30 puntos existen igual, y dejarlos fuera deja al parcial
        pesando lo mismo que un decimal.

    Devuelve (pesos, cuantas_columnas_emparejaron, explicacion).
    """
    emparejadas = {}
    for regla in reglas:
        instrumento = normalizar(regla.get("instrumento", ""))
        if not instrumento:
            continue
        puntaje = _puntaje_de(regla)
        if not puntaje:
            continue
        suyas = [c for c in columnas_nota if instrumento in normalizar(c)]
        if suyas:
            emparejadas[regla.get("instrumento", "")] = (puntaje, suyas)

    pesos = {}
    for puntaje, suyas in emparejadas.values():
        for c in suyas:
            pesos[c] = pesos.get(c, 0.0) + puntaje / len(suyas)

    huerfanas = [c for c in columnas_nota if c not in pesos]
    declarado_total = sum(_puntaje_de(r) or 0 for r in reglas
                          if _es_regla_de_instrumento(r))
    declarado_usado = sum(p for p, _ in emparejadas.values())
    sobrante = max(0.0, declarado_total - declarado_usado)

    if huerfanas and sobrante > 0:
        for c in huerfanas:
            pesos[c] = sobrante / len(huerfanas)
        nota = (f"{len(huerfanas)} columna(s) no coincidieron por nombre con "
                f"ninguna regla; se repartieron entre ellas los {sobrante:.0f} "
                f"puntos declarados que quedaban sin usar")
    elif huerfanas:
        medio = (sum(pesos.values()) / len(pesos)) if pesos else 1.0
        for c in huerfanas:
            pesos[c] = medio
        nota = (f"{len(huerfanas)} columna(s) sin regla: se les dio el peso medio "
                "de las demas para que no quedaran aplastadas")
    else:
        nota = ""
    return pesos, len(columnas_nota) - len(huerfanas), nota


def _puntaje_de(regla):
    for llave, valor in regla.items():
        if normalizar(llave).startswith(("puntaje", "puntos", "valor",
                                         "ponderacion", "peso")):
            numero = a_numero(valor)
            if numero and numero > 0:
                return numero
    return None


def _es_regla_de_instrumento(regla):
    """Descarta las lineas del silabo que son condiciones, no instrumentos.

    «Nota minima de aprobacion 51 puntos» tiene la misma forma que una
    ponderacion y no lo es: sumarla al total declarado desplazaria todos los
    pesos.
    """
    plano = normalizar(regla.get("instrumento", ""))
    for palabra in ("minima", "minimo", "maxima", "maximo", "aprobacion",
                    "asistencia minima", "guia", "condicion"):
        if palabra in plano:
            return False
    return True


def construir_rendimiento(columnas, filas, fichas, reglas, config):
    """Una sola medida de rendimiento por estudiante, en escala 0 a 1.

    Devuelve (valores, explicacion). La explicacion se muestra al docente: como
    se armo la medida, con que instrumentos y que se hizo con las casillas vacias.
    """
    indices = de_papel(fichas, NOTA)
    if not indices:
        return [None] * len(filas), {
            "metodo": "no se pudo construir",
            "instrumentos": 0,
            "vacios": "no aplica",
            "detalle": "la base no tiene ninguna columna que se comporte como "
                       "calificacion",
        }

    nombres = [columnas[i] for i in indices]
    pesos_por_columna, con_regla, nota_reparto = _repartir_pesos(nombres, reglas)

    ponderadas, pesos, usados = [], [], []
    for indice in indices:
        nombre = columnas[indice]
        pesos.append(pesos_por_columna.get(nombre, 1.0))
        ponderadas.append(normalizar_0_1(serie(filas, indice)))
        usados.append(nombre)

    # Vacio no es cero: un cero diria que el estudiante rindio y saco cero. Cada
    # estudiante se promedia sobre los instrumentos que SI tiene, y se anota
    # cuantos le faltaban, porque un promedio sobre dos de diez no vale lo mismo.
    valores, faltantes = [], []
    for numero_fila in range(len(filas)):
        suma, total_peso, ausentes = 0.0, 0.0, 0
        for columna, peso in zip(ponderadas, pesos):
            valor = columna[numero_fila]
            if valor is None:
                ausentes += 1
                continue
            suma += valor * peso
            total_peso += peso
        valores.append(round(suma / total_peso, 4) if total_peso else None)
        faltantes.append(ausentes)

    if con_regla:
        metodo = (f"promedio ponderado de {len(usados)} instrumento(s); "
                  f"{con_regla} con el puntaje que declara REGLAS_EVALUACION, "
                  "repartido entre las columnas de cada instrumento")
    else:
        metodo = (f"promedio simple de {len(usados)} instrumento(s): la base no "
                  "traia ponderaciones utilizables, asi que todos pesan igual")
    if nota_reparto:
        metodo += f". {nota_reparto}"

    return valores, {
        "metodo": metodo,
        "instrumentos": len(usados),
        "vacios": "las casillas vacias NO se cuentan como cero: cada estudiante "
                  "se promedia sobre los instrumentos que tiene",
        "detalle": "medida de analisis en escala 0 a 1, no es la nota oficial",
        "columnas_usadas": usados,
        "pesos": {c: round(p, 2) for c, p in zip(usados, pesos)},
        "instrumentos_faltantes": faltantes,
    }


def _a_fraccion(valores):
    """Lleva una columna a la escala 0-1 dividiendo por su maximo.

    No se usa min-max: si nadie falto nunca, min-max convertiria al que menos
    asistio en un cero absoluto y el docente veria una alarma que no existe.
    Dividir por el maximo conserva la distancia real al tope.
    """
    llenos = [v for v in valores if v is not None]
    if not llenos:
        return valores
    tope = max(llenos)
    if tope <= 1:
        return valores
    return [None if v is None else v / tope for v in valores]


def _proporcion_asistencia(filas, fichas):
    """Que fraccion de las clases registradas asistio cada estudiante.

    Una materia marca P/A/T, otra pone un puntaje de asistencia sobre 5 y otra
    un porcentaje. Cada columna se lleva a su propia escala 0-1 antes de
    promediarlas: sin eso, el umbral de alerta comparia una escala con otra.
    """
    indices = de_papel(fichas, ASISTENCIA)
    if not indices:
        return [None] * len(filas), 0
    columnas = [_a_fraccion([a_numero(f[i]) for f in filas]) for i in indices]
    resultado = []
    for numero in range(len(filas)):
        marcas = [c[numero] for c in columnas if c[numero] is not None]
        resultado.append(round(sum(marcas) / len(marcas), 4) if marcas else None)
    return resultado, len(indices)


def _actividad_plataforma(filas, fichas):
    indices = de_papel(fichas, PLATAFORMA)
    if not indices:
        return [None] * len(filas), 0
    columnas = [normalizar_0_1([a_numero(f[i]) for f in filas]) for i in indices]
    resultado = []
    for numero_fila in range(len(filas)):
        valores = [c[numero_fila] for c in columnas if c[numero_fila] is not None]
        resultado.append(round(sum(valores) / len(valores), 4) if valores else None)
    return resultado, len(indices)


def clasificar(columnas, filas, fichas, reglas, clave, config):
    """Arma las senales por estudiante y reparte al curso en grupos de rendimiento."""
    rendimiento, explicacion = construir_rendimiento(columnas, filas, fichas,
                                                     reglas, config)
    asistencia, columnas_asistencia = _proporcion_asistencia(filas, fichas)
    plataforma, columnas_plataforma = _actividad_plataforma(filas, fichas)

    indice_situacion = columnas.index("situacion_en_el_curso")

    senales = []
    for numero_fila, fila in enumerate(filas):
        senales.append({
            "codigo": str(fila[clave]).strip(),
            "situacion": fila[indice_situacion],
            "rendimiento": rendimiento[numero_fila],
            "asistencia": asistencia[numero_fila],
            "plataforma": plataforma[numero_fila],
            "instrumentos_sin_registro":
                explicacion.get("instrumentos_faltantes", [0] * len(filas))[numero_fila],
        })

    # Los grupos se cortan por tercios del propio curso, no por una nota fija: una
    # materia puede calificar sobre 100 y otra sobre 6, y un umbral escrito en el
    # programa serviria para una sola de las dos.
    con_valor = sorted((s["rendimiento"] for s in senales
                        if s["rendimiento"] is not None))
    if len(con_valor) >= 3:
        bajo = con_valor[len(con_valor) // 3]
        alto = con_valor[2 * len(con_valor) // 3]
    else:
        bajo = alto = None

    for s in senales:
        valor = s["rendimiento"]
        if valor is None:
            s["grupo"] = "sin datos suficientes"
        elif bajo is None:
            s["grupo"] = "curso demasiado pequeno para agrupar"
        elif valor <= bajo:
            s["grupo"] = "tercio de menor rendimiento"
        elif valor >= alto:
            s["grupo"] = "tercio de mayor rendimiento"
        else:
            s["grupo"] = "tercio intermedio"

    conteo = {}
    for s in senales:
        conteo[s["grupo"]] = conteo.get(s["grupo"], 0) + 1

    explicacion.update({
        "columnas_de_asistencia": columnas_asistencia,
        "columnas_de_plataforma": columnas_plataforma,
        "corte_bajo": round(bajo, 4) if bajo is not None else None,
        "corte_alto": round(alto, 4) if alto is not None else None,
    })

    resumen = {
        "total": len(senales),
        "activos": sum(1 for s in senales if s["situacion"] == "activo"),
        "abandonos": sum(1 for s in senales if s["situacion"] == "abandono"),
        "grupos": [{"grupo": g, "estudiantes": n} for g, n in
                   sorted(conteo.items(), key=lambda x: -x[1])],
        "rendimiento_medio": (round(media([s["rendimiento"] for s in senales]), 4)
                              if con_valor else None),
    }
    return senales, explicacion, resumen
