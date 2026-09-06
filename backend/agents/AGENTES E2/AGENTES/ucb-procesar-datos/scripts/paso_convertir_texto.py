"""Paso: convertir_texto

Cambia las palabras de asistencia por numeros, para que se puedan sumar y sacar
porcentajes: 'Presente' pasa a 1 y 'Falta' a 0.

Dos cuidados:

1. Si la asistencia ya viene en numeros, no se toca nada y se dice en el informe.
   Convertir lo ya convertido solo genera ruido.

2. Muchas planillas tienen un TERCER estado —tarde, atraso— que no es ni presente
   ni ausente. Aplastarlo a 0 seria decidir por el docente que llegar tarde
   equivale a faltar. Se convierte a un valor intermedio y queda anotado de forma
   destacada en la hoja CAMBIOS, para que el docente lo confirme o lo cambie.

Como siempre en esta etapa, la columna original se conserva al lado de la nueva.
"""

from paso_leer_base import NUMERO, VACIO, tipo_de


def _mapa(config):
    """{palabra: valor} a partir de config.json, todo en minusculas."""
    tabla = {}
    for valor, palabras in config["marcas_asistencia"].items():
        for palabra in palabras:
            tabla[str(palabra).strip().lower()] = float(valor)
    return tabla


def _es_columna_de_marcas(valores, tabla, relleno_de_vacios=""):
    """True si casi todos los valores con dato son marcas de asistencia.

    El relleno que el paso de vacios escribio antes ('Sin registro') no cuenta ni
    a favor ni en contra: no es una marca del docente, es la constancia de que
    ahi no habia nada. Antes se contaba como valor no reconocido, y bastaba con
    que un 10% del curso no figurara en la planilla de asistencia para que la
    columna quedara por debajo del umbral y **toda la asistencia de la materia se
    perdiera sin un solo aviso**. Es justo la situacion mas comun: los que se
    dieron de baja no aparecen en la planilla.
    """
    relleno = str(relleno_de_vacios).strip().lower()
    con_dato = [str(v).strip().lower() for v in valores if tipo_de(v) != VACIO]
    con_dato = [v for v in con_dato if v != relleno]
    if len(con_dato) < 3:
        return False
    reconocidas = sum(1 for v in con_dato if v in tabla)
    if reconocidas < len(con_dato) * 0.9:
        return False
    # Una columna con un solo valor distinto no es asistencia, es una constante.
    return len(set(con_dato)) >= 2


def convertir(columnas, filas, config):
    """Devuelve (columnas, filas, cambios, notas).

    Las notas son los avisos que hay que subir al informe: columnas que ya venian
    en numeros, y estados intermedios que el docente debe confirmar.
    """
    tabla = _mapa(config)
    intermedios = {p for p, v in tabla.items() if 0 < v < 1}

    objetivo = {}
    notas = []

    for indice, nombre in enumerate(columnas):
        valores = [f[indice] for f in filas]
        con_dato = [v for v in valores if tipo_de(v) != VACIO]
        if not con_dato:
            continue

        if all(tipo_de(v) == NUMERO for v in con_dato):
            numeros = {float(str(v).replace(",", ".")) for v in con_dato}
            if numeros <= {0.0, 0.5, 1.0} and len(numeros) >= 2:
                notas.append({
                    "columna": nombre,
                    "aviso": "ya venia en numeros: no se toco",
                })
            continue

        if _es_columna_de_marcas(valores, tabla, config["texto_vacio"]):
            objetivo[indice] = nombre

    nuevas_columnas, plan, cambios, creadas = [], [], [], set()
    for indice, nombre in enumerate(columnas):
        plan.append(("original", indice, nombre))
        nuevas_columnas.append(nombre)
        if indice in objetivo:
            etiqueta = f"{nombre} [1/0]"
            plan.append(("convertida", indice, etiqueta))
            nuevas_columnas.append(etiqueta)
            creadas.add(etiqueta)

            usados = {str(f[indice]).strip().lower() for f in filas
                      if tipo_de(f[indice]) != VACIO}
            hay_intermedio = usados & intermedios
            cambios.append({
                "columna": nombre,
                "paso": "texto a numero",
                "que_se_hizo": f"se agrego '{etiqueta}' al lado, sin tocar la original",
                "factor": "",
                "por_que": "permite sumar asistencias y calcular porcentajes",
            })
            if hay_intermedio:
                notas.append({
                    "columna": nombre,
                    "aviso": "tiene un estado intermedio (tarde/atraso) que se "
                             "convirtio a 0,5. CONFIRMAR con el docente: si "
                             "llegar tarde debe contar como falta, vale 0.",
                })

    nuevas_filas = []
    for fila in filas:
        nueva = []
        for clase, indice, _ in plan:
            if clase == "original":
                nueva.append(fila[indice])
            else:
                bruto = fila[indice]
                if tipo_de(bruto) == VACIO:
                    nueva.append(None)
                else:
                    nueva.append(tabla.get(str(bruto).strip().lower()))
        nuevas_filas.append(nueva)

    return nuevas_columnas, nuevas_filas, cambios, notas, creadas
