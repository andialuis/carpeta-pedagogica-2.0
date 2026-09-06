"""Paso: limpiar_tipos

Dos trabajos distintos que conviene no confundir:

1. Forzar el tipo correcto de cada columna y quitarle la basura invisible. Es
   inocuo: el valor sigue siendo el mismo, solo deja de estar guardado como texto
   cuando es un numero.

2. Unificar las escalas de evaluacion. Esto SI transforma el valor, y por eso
   solo se hace con lo que declara la hoja REGLAS_EVALUACION. Nunca se deduce una
   ponderacion del titulo de una columna ni se inventa un factor.

Toda conversion deja la columna original al lado de la convertida. Es lo que
permite auditar despues que factor se aplico, y volver atras si estuvo mal.

Si una regla viene con un aviso de escala sin resolver desde la Etapa 1, NO se
convierte: se reporta y queda pendiente hasta que el docente decida.
"""

from paso_leer_base import (FECHA, NUMERO, TEXTO, VACIO, a_numero,
                             limpiar_texto, tipo_de)


def _escala_declarada(regla):
    """La escala con la que la planilla califica ese instrumento, si se sabe."""
    bruto = str(regla.get("escala_en_planilla", "") or "").strip()
    if not bruto:
        return None
    # La Etapa 1 puede reportar varias escalas separadas por barra cuando el mismo
    # instrumento se califico distinto en cada parcial. Si hay mas de una, no se
    # puede elegir por el docente.
    partes = [p for p in bruto.split("/") if p.strip()]
    if len(partes) != 1:
        return None
    try:
        valor = float(partes[0].replace(",", "."))
    except ValueError:
        return None
    return valor if valor > 0 else None


def _columnas_de_la_regla(regla, columnas):
    """Las columnas de la base que esa regla dice medir."""
    bruto = str(regla.get("columnas_relacionadas", "") or "")
    if not bruto:
        return []
    nombres = [p.strip() for p in bruto.split("|") if p.strip()]
    # La Etapa 1 puede anotar '(toda la hoja X)' cuando el instrumento no da
    # nombre a una columna concreta. Eso no se puede convertir sin adivinar.
    return [n for n in nombres if n in columnas and not n.startswith("(")]


def proponer_escalas(columnas, filas, reglas):
    """Que conversiones se harian y con que factor. No transforma nada.

    Devuelve (propuestas, pendientes). Las pendientes son las que la Etapa 1 dejo
    con un conflicto sin resolver: se muestran para que el docente decida, pero no
    se aplican.
    """
    propuestas, pendientes = [], []

    for regla in reglas:
        instrumento = str(regla.get("instrumento", "") or "").strip()
        if not instrumento:
            continue
        destino = a_numero(regla.get("valor_declarado"))
        origen = _escala_declarada(regla)
        objetivo = _columnas_de_la_regla(regla, columnas)
        observacion = str(regla.get("observacion", "") or "").strip()

        if not objetivo:
            continue

        motivo_pendiente = None
        if observacion:
            motivo_pendiente = observacion
        elif destino is None:
            motivo_pendiente = "la regla no declara cuantos puntos vale"
        elif origen is None:
            motivo_pendiente = ("no se pudo determinar una unica escala de origen "
                                "en la planilla")

        if motivo_pendiente:
            pendientes.append({
                "instrumento": instrumento,
                "columnas": " | ".join(objetivo),
                "motivo": motivo_pendiente,
            })
            continue

        factor = destino / origen
        for nombre in objetivo:
            propuestas.append({
                "instrumento": instrumento,
                "columna": nombre,
                "escala_origen": origen,
                "escala_destino": destino,
                "factor": round(factor, 6),
                "de_donde_sale": f"{regla.get('archivo', '')} "
                                 f"(linea {regla.get('linea', '')})".strip(),
            })

    return propuestas, pendientes


def aplicar(columnas, filas, propuestas, instrumentos_omitidos):
    """Convierte las escalas aprobadas y devuelve la base ampliada.

    La columna convertida se agrega INMEDIATAMENTE despues de la original, para
    que al abrir el Excel se vean una al lado de la otra.
    """
    omitidos = {str(i).strip().lower() for i in instrumentos_omitidos}
    aplicadas = [p for p in propuestas
                 if p["instrumento"].strip().lower() not in omitidos]
    omitidas = [p for p in propuestas
                if p["instrumento"].strip().lower() in omitidos]

    # Una regla puede apuntar a una columna que no tiene ni un valor numerico
    # —la asistencia escrita como P/A/T, por ejemplo—. Convertirla produciria una
    # columna entera vacia, que despues confunde a los pasos siguientes.
    indice_de = {nombre: i for i, nombre in enumerate(columnas)}
    por_columna, sin_efecto = {}, []
    for p in aplicadas:
        indice = indice_de.get(p["columna"])
        if indice is None:
            continue
        if not any(a_numero(f[indice]) is not None for f in filas):
            continue
        # Convertir con factor 1 duplica la columna sin cambiar un solo valor.
        # Solo agrega ruido al informe y hace dudar de las cuentas.
        if abs(p["factor"] - 1.0) < 1e-9:
            sin_efecto.append(p)
            continue
        por_columna.setdefault(p["columna"], p)
    aplicadas = [p for p in aplicadas if p["columna"] in por_columna]

    nuevas_columnas, cambios, creadas = [], [], set()
    plan = []
    for indice, nombre in enumerate(columnas):
        plan.append(("original", indice, nombre))
        nuevas_columnas.append(nombre)
        p = por_columna.get(nombre)
        if p:
            etiqueta = f"{nombre} [sobre {_bonito(p['escala_destino'])}]"
            plan.append(("convertida", indice, etiqueta))
            nuevas_columnas.append(etiqueta)
            creadas.add(etiqueta)
            cambios.append({
                "columna": nombre,
                "paso": "unificar escala",
                "que_se_hizo": f"se agrego '{etiqueta}' al lado, sin tocar la original",
                "factor": p["factor"],
                "por_que": f"{p['instrumento']}: la planilla califica sobre "
                           f"{_bonito(p['escala_origen'])} y la normativa le da "
                           f"{_bonito(p['escala_destino'])} puntos "
                           f"({p['de_donde_sale']})",
            })

    nuevas_filas = []
    for fila in filas:
        nueva = []
        for clase, indice, _ in plan:
            if clase == "original":
                nueva.append(fila[indice])
            else:
                valor = a_numero(fila[indice])
                p = por_columna[columnas[indice]]
                nueva.append(None if valor is None
                             else round(valor * p["factor"], 3))
        nuevas_filas.append(nueva)

    for p in sin_efecto:
        cambios.append({
            "columna": p["columna"],
            "paso": "unificar escala",
            "que_se_hizo": "no se convirtio: la escala de la planilla ya coincide "
                           "con el puntaje de la normativa",
            "factor": 1,
            "por_que": f"{p['instrumento']}: convertir con factor 1 habria "
                       f"duplicado la columna sin cambiar ningun valor",
        })

    return nuevas_columnas, nuevas_filas, cambios, aplicadas, omitidas, creadas


def _bonito(numero):
    if numero is None:
        return "?"
    return str(int(numero)) if float(numero).is_integer() else str(numero)


def normalizar_valores(columnas, filas, config):
    """Fuerza el tipo de cada columna y limpia caracteres invisibles.

    No cambia ningun valor: un 7 guardado como texto pasa a ser el numero 7, y un
    nombre con un espacio de ancho cero pasa a estar sin el. Nada mas.
    """
    cambios = []
    nuevas = [list(f) for f in filas]

    for indice, nombre in enumerate(columnas):
        valores = [f[indice] for f in filas]
        tipos = [tipo_de(v) for v in valores]
        con_dato = [t for t in tipos if t != VACIO]
        if not con_dato:
            continue

        mayoria_numero = sum(1 for t in con_dato if t == NUMERO) >= len(con_dato) * 0.8
        mayoria_fecha = sum(1 for t in con_dato if t == FECHA) >= len(con_dato) * 0.8

        if mayoria_fecha:
            continue                      # una fecha se deja exactamente como vino

        tocadas = 0
        if mayoria_numero:
            enteros = True
            for fila in nuevas:
                valor = a_numero(fila[indice])
                if valor is None:
                    continue
                if not float(valor).is_integer():
                    enteros = False
            for fila in nuevas:
                valor = a_numero(fila[indice])
                if valor is None:
                    continue
                nuevo = int(valor) if enteros else round(valor, 4)
                if nuevo != fila[indice]:
                    fila[indice] = nuevo
                    tocadas += 1
            if tocadas:
                cambios.append({
                    "columna": nombre, "paso": "tipos",
                    "que_se_hizo": f"{tocadas} celda(s) guardadas como texto pasaron "
                                   f"a ser {'enteros' if enteros else 'decimales'}",
                    "factor": "",
                    "por_que": "un numero guardado como texto no se puede sumar",
                })
        else:
            for fila in nuevas:
                if isinstance(fila[indice], str):
                    limpio = limpiar_texto(fila[indice])
                    if limpio != fila[indice]:
                        fila[indice] = limpio
                        tocadas += 1
            if tocadas:
                cambios.append({
                    "columna": nombre, "paso": "tipos",
                    "que_se_hizo": f"{tocadas} celda(s) tenian espacios o caracteres "
                                   f"invisibles y se limpiaron",
                    "factor": "",
                    "por_que": "dos valores iguales dejaban de parecerlo",
                })

    return nuevas, cambios
