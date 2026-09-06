"""Estadistica minima, con la biblioteca estandar y nada mas.

No es un paso del analisis: es la caja de herramientas que usan todos los pasos.
Esta escrita a mano a proposito. Si dependiera de numpy o de scipy, el resultado
podria cambiar segun lo que cada computadora tenga instalado, y dos docentes con
los mismos datos obtendrian informes distintos.

Todas las pruebas de azar usan una semilla fija que viene en `config.json`: el
mismo dato da siempre el mismo veredicto, en cualquier maquina.
"""

import random


def media(valores):
    valores = [v for v in valores if v is not None]
    return sum(valores) / len(valores) if valores else None


def desviacion(valores):
    valores = [v for v in valores if v is not None]
    if len(valores) < 2:
        return None
    m = sum(valores) / len(valores)
    return (sum((v - m) ** 2 for v in valores) / (len(valores) - 1)) ** 0.5


def mediana(valores):
    valores = sorted(v for v in valores if v is not None)
    if not valores:
        return None
    mitad = len(valores) // 2
    if len(valores) % 2:
        return valores[mitad]
    return (valores[mitad - 1] + valores[mitad]) / 2


def emparejar(a, b):
    """Los pares en que ninguna de las dos series tiene hueco."""
    return [(x, y) for x, y in zip(a, b) if x is not None and y is not None]


def correlacion(a, b):
    """Correlacion de Pearson. Devuelve (r, n) o (None, n) si no se puede."""
    pares = emparejar(a, b)
    n = len(pares)
    if n < 3:
        return None, n
    xs = [p[0] for p in pares]
    ys = [p[1] for p in pares]
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in pares)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None, n
    return sxy / (sxx * syy) ** 0.5, n


def fuerza(r):
    """Como se lee un coeficiente, en palabras que el docente pueda usar."""
    if r is None:
        return "no se pudo calcular"
    a = abs(r)
    if a >= 0.7:
        return "muy fuerte"
    if a >= 0.5:
        return "fuerte"
    if a >= 0.3:
        return "moderada"
    if a >= 0.15:
        return "debil"
    return "practicamente nula"


def sentido(r):
    if r is None:
        return ""
    if r > 0:
        return "cuando una sube, la otra tambien"
    return "cuando una sube, la otra baja"


def z(valores):
    """Cuantas desviaciones se aparta cada valor de la media de su columna."""
    m, s = media(valores), desviacion(valores)
    if m is None or not s:
        return [None] * len(valores)
    return [None if v is None else (v - m) / s for v in valores]


def normalizar_0_1(valores):
    """Lleva una columna a la escala 0-1 para poder comparar peras con manzanas.

    Sin esto no se puede sumar un parcial sobre 100 con un laboratorio sobre 6.
    """
    llenos = [v for v in valores if v is not None]
    if not llenos:
        return [None] * len(valores)
    bajo, alto = min(llenos), max(llenos)
    if alto - bajo <= 0:
        return [None if v is None else 0.5 for v in valores]
    return [None if v is None else (v - bajo) / (alto - bajo) for v in valores]


# --------------------------------------------------------- pruebas de azar
def p_diferencia_de_medias(grupo_a, grupo_b, permutaciones, semilla):
    """¿La diferencia entre dos grupos podria ser casualidad?

    Se baraja quien esta en cada grupo muchas veces y se cuenta cuantas de esas
    reparticiones al azar dan una diferencia tan grande como la observada. Es la
    forma honesta de responder con cursos de veinte o treinta estudiantes, donde
    las formulas clasicas suponen mas datos de los que hay.
    """
    a = [v for v in grupo_a if v is not None]
    b = [v for v in grupo_b if v is not None]
    if len(a) < 2 or len(b) < 2:
        return None
    observada = abs(sum(a) / len(a) - sum(b) / len(b))
    juntos = a + b
    corte = len(a)
    azar = random.Random(semilla)
    extremos = 0
    for _ in range(permutaciones):
        azar.shuffle(juntos)
        ma = sum(juntos[:corte]) / corte
        mb = sum(juntos[corte:]) / (len(juntos) - corte)
        if abs(ma - mb) >= observada - 1e-12:
            extremos += 1
    return (extremos + 1) / (permutaciones + 1)


def p_correlacion(a, b, permutaciones, semilla):
    """Lo mismo para una relacion entre dos columnas."""
    pares = emparejar(a, b)
    if len(pares) < 4:
        return None
    xs = [p[0] for p in pares]
    ys = [p[1] for p in pares]
    observada, _ = correlacion(xs, ys)
    if observada is None:
        return None
    # Dentro del bucle solo cambia el ORDEN de `ys`. `xs` es siempre la misma
    # lista, y ninguna de las dos tiene huecos porque las dos salen de `pares`.
    # Volver a filtrar huecos y a recalcular la media y la dispersion de `xs` en
    # cada permutacion era trabajo repetido: con mil permutaciones se hacia mil
    # veces la misma cuenta. Se hace una sola vez.
    #
    # Lo que NO se saca del bucle es la media ni la dispersion de `ys`: al
    # revolver la lista, la suma recorre los mismos numeros en otro orden y el
    # redondeo del punto flotante no es identico. Sacarlas cambiaria el ultimo
    # decimal de algunas correlaciones y, con el, la huella del analisis. La
    # cuenta que varia se deja tal cual estaba.
    n = len(pares)
    mx = sum(xs) / n
    dx = [x - mx for x in xs]
    sxx = sum(d * d for d in dx)
    if sxx <= 0:
        return None
    limite = abs(observada) - 1e-12
    azar = random.Random(semilla)
    revueltos = list(ys)
    extremos = 0
    for _ in range(permutaciones):
        azar.shuffle(revueltos)
        my = sum(revueltos) / n
        syy = sum((y - my) ** 2 for y in revueltos)
        if syy <= 0:
            continue
        sxy = sum(d * (y - my) for d, y in zip(dx, revueltos))
        if abs(sxy / (sxx * syy) ** 0.5) >= limite:
            extremos += 1
    return (extremos + 1) / (permutaciones + 1)


def veredicto_p(p, umbral):
    """Traduce el numero a una frase que no prometa mas de lo que dice."""
    if p is None:
        return "no se pudo comprobar: hacen falta mas datos"
    if p <= umbral:
        return (f"dificilmente sea casualidad (probabilidad de que lo sea: "
                f"{p:.1%})")
    return (f"puede ser casualidad (probabilidad de que lo sea: {p:.1%}); con "
            "este numero de estudiantes no alcanza para afirmarlo")


def tamano_del_efecto(grupo_a, grupo_b):
    """Cuanto se separan dos grupos, en desviaciones. Sirve para saber si una
    diferencia estadistica ademas IMPORTA."""
    a = [v for v in grupo_a if v is not None]
    b = [v for v in grupo_b if v is not None]
    if len(a) < 2 or len(b) < 2:
        return None
    sa, sb = desviacion(a), desviacion(b)
    if sa is None or sb is None:
        return None
    combinada = (((len(a) - 1) * sa ** 2 + (len(b) - 1) * sb ** 2)
                 / (len(a) + len(b) - 2)) ** 0.5
    if not combinada:
        return None
    return (sum(a) / len(a) - sum(b) / len(b)) / combinada


def benjamini_hochberg(valores_p, umbral):
    """Cuales de una tanda de pruebas sobreviven cuando se hacen muchas a la vez.

    Es la correccion que mas falta hace en un informe como este. Al cruzar
    doscientas parejas de columnas al 5%, diez saldran "significativas" por puro
    azar aunque no exista ninguna relacion. Sin este ajuste, el informe entrega
    diez hallazgos inventados y nadie lo nota.

    Devuelve una lista de booleanos, uno por cada p en el mismo orden de entrada.
    """
    indexados = [(p, i) for i, p in enumerate(valores_p) if p is not None]
    if not indexados:
        return [False] * len(valores_p)
    indexados.sort()
    total = len(indexados)
    corte = 0
    for posicion, (p, _) in enumerate(indexados, start=1):
        if p <= umbral * posicion / total:
            corte = posicion
    sobreviven = [False] * len(valores_p)
    for _, indice in indexados[:corte]:
        sobreviven[indice] = True
    return sobreviven


def cuantas_saldrian_por_azar(pruebas, umbral):
    """Frase para el informe: cuantos falsos hallazgos cabria esperar."""
    esperadas = pruebas * umbral
    if esperadas < 1:
        return (f"Se hicieron {pruebas} comprobaciones, pocas como para que el "
                "azar produzca un resultado falso; aun asi se marca cuales "
                "sobreviven al ajuste por comparaciones multiples.")
    return (f"Se hicieron {pruebas} comprobaciones. Si no existiera ninguna "
            f"relacion real, cerca de {esperadas:.0f} de ellas apareceria como "
            "significativa solo por azar; por eso se marca cuales sobreviven al "
            "ajuste por comparaciones multiples.")
