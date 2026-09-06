"""Paso: detectar_anomalias

Aisla los valores sospechosos ANTES de cualquier transformacion matematica, y no
corrige ninguno. Detectar y reportar es todo el trabajo de este paso.

No alcanza con buscar valores fuera de rango. Un dato puede estar perfectamente
dentro del rango y ser igual de sospechoso:

  - un decimal suelto en una columna donde todo el resto son enteros;
  - un valor diez veces menor que el resto de su columna (un 0,8 donde todos
    tienen entre 6 y 9: alguien tecleo la nota con la coma corrida);
  - un valor que se aleja de su columna mucho mas que cualquier otro.

Por eso cada valor se compara contra el comportamiento de su PROPIA columna, con
estadistica descriptiva, y no contra un limite fijo escrito en el programa.
"""

from paso_leer_base import NUMERO, VACIO, a_numero, tipo_de


def _mediana(valores):
    ordenados = sorted(valores)
    n = len(ordenados)
    medio = n // 2
    if n % 2:
        return ordenados[medio]
    return (ordenados[medio - 1] + ordenados[medio]) / 2


def _desviacion(valores, media):
    if len(valores) < 2:
        return 0.0
    return (sum((v - media) ** 2 for v in valores) / (len(valores) - 1)) ** 0.5


def revisar(columnas, filas, indice_clave, config, columnas_derivadas=()):
    """Devuelve la lista de valores sospechosos, sin tocar ninguno.

    Las columnas que esta etapa creo —una escala convertida, una asistencia pasada
    a numero— se omiten a proposito. Su contenido deriva del original, asi que
    revisarlas reportaria dos veces la misma anomalia y haria dudar del informe.
    """
    derivadas = set(columnas_derivadas)
    minimo = config["minimo_datos_para_estadistica"]
    umbral_z = config["umbral_atipico_z"]
    prop_decimales = config["proporcion_decimales_para_columna_entera"]

    hallazgos = []

    for indice, nombre in enumerate(columnas):
        if nombre in derivadas:
            continue
        crudos = [f[indice] for f in filas]
        tipos = [tipo_de(v) for v in crudos]
        con_dato = [t for t in tipos if t != VACIO]
        if not con_dato:
            continue
        if sum(1 for t in con_dato if t == NUMERO) < len(con_dato) * 0.8:
            continue

        numeros = [(i, a_numero(v)) for i, v in enumerate(crudos)]
        numeros = [(i, v) for i, v in numeros if v is not None]
        if len(numeros) < minimo:
            continue

        valores = [v for _, v in numeros]
        media = sum(valores) / len(valores)
        desviacion = _desviacion(valores, media)
        mediana = _mediana(valores)

        # --- 1. La columna es de enteros y aparece un decimal suelto ----------
        decimales = [(i, v) for i, v in numeros if not float(v).is_integer()]
        if decimales and len(decimales) <= max(1, len(numeros) * prop_decimales):
            for i, v in decimales:
                hallazgos.append(_hallazgo(
                    filas[i][indice_clave], nombre, v,
                    "decimal en una columna de enteros",
                    f"el resto de la columna son numeros enteros; este es {v}"))

        # --- 2. Se aleja mucho mas que cualquier otro de su columna ----------
        if desviacion > 0:
            for i, v in numeros:
                z = abs(v - media) / desviacion
                if z >= umbral_z:
                    hallazgos.append(_hallazgo(
                        filas[i][indice_clave], nombre, v,
                        "muy lejos del resto de su columna",
                        f"se aparta {z:.1f} desviaciones de la media "
                        f"({media:.2f}) de esta columna"))

        # --- 3. Un orden de magnitud por debajo del resto --------------------
        if mediana > 0:
            for i, v in numeros:
                if 0 < v <= mediana / 10:
                    hallazgos.append(_hallazgo(
                        filas[i][indice_clave], nombre, v,
                        "diez veces menor que el resto",
                        f"la mediana de la columna es {mediana:.2f}; este valor "
                        f"es {v}. Suele ser una coma mal puesta"))

        # --- 4. Negativo donde todo lo demas es positivo ---------------------
        negativos = [(i, v) for i, v in numeros if v < 0]
        if negativos and len(negativos) < len(numeros):
            for i, v in negativos:
                hallazgos.append(_hallazgo(
                    filas[i][indice_clave], nombre, v,
                    "valor negativo",
                    "una calificacion o un contador negativo no tiene sentido"))

    # Un mismo valor puede disparar dos motivos; se deja uno solo por celda.
    vistos, unicos = set(), []
    for h in hallazgos:
        clave = (h["estudiante"], h["columna"])
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(h)
    return unicos


def _hallazgo(estudiante, columna, valor, motivo, detalle):
    return {
        "estudiante": str(estudiante).strip(),
        "columna": columna,
        "valor": valor,
        "motivo": motivo,
        "detalle": detalle,
        "accion": "ninguna: esta etapa no corrige",
    }
