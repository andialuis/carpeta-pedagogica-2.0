"""Skill: integrar

Une todas las planillas aprobadas en una sola tabla, con una fila por estudiante de
la lista oficial y todas las columnas de origen conservadas.

Nada se transforma: los valores se copian tal como vinieron. Lo que no se puede
resolver no se descarta, se reporta.
"""

import re

from skill_descubrir_reglas import escala_de_columna
from skill_identidad import Reconocedor, normalizar
from skill_leer_planillas import VACIO, _tipo
from skill_resumir_registros import parece_registro_de_actividad, resumir

PATRON_CODIGO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-_./]*$")


# --------------------------------------------------------------- lista oficial
def _columna_correo(columnas, filas):
    mejor, mejor_conteo = None, 0
    for indice in range(len(columnas)):
        conteo = sum(1 for f in filas
                     if isinstance(f[indice], str) and "@" in f[indice])
        if conteo > mejor_conteo:
            mejor, mejor_conteo = indice, conteo
    return mejor if mejor_conteo >= max(1, len(filas) // 2) else None


def _columna_nombre(columnas, filas, excluidas):
    """Busca la columna con el nombre de la persona.

    Ademas de tener varias palabras, tiene que ser practicamente UNICA por fila:
    una columna 'Carrera' o 'Turno' repite el mismo texto para todo el curso y, si
    se la confunde con el nombre, ninguna planilla vuelve a reconocer a nadie.
    """
    mejor, mejor_puntaje = None, 0.0
    for indice in range(len(columnas)):
        if indice in excluidas:
            continue
        textos = [f[indice] for f in filas
                  if isinstance(f[indice], str) and "@" not in f[indice]]
        if not textos or len(set(textos)) < len(filas) * 0.8:
            continue
        puntaje = sum(len(t.split()) for t in textos) / len(filas)
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = indice, puntaje
    return mejor if mejor_puntaje >= 1.5 else None


def _es_numeracion_de_filas(valores):
    """1, 2, 3... no es un codigo de estudiante: es el numero de fila."""
    if not all(v.isdigit() for v in valores):
        return False
    return sorted(int(v) for v in valores) == list(range(1, len(valores) + 1))


def _columna_codigo(columnas, filas, excluidas):
    """Elige la columna de codigo, prefiriendo la que mezcla letras y numeros.

    Muchas nominas empiezan con una columna 'N°' que solo enumera las filas. Si se
    la toma por codigo, cualquier columna con numeros chicos (un puntaje del 1 al 5,
    por ejemplo) pasa a parecer una lista de identidades.
    """
    candidatas = []
    for indice in range(len(columnas)):
        if indice in excluidas:
            continue
        valores = [str(f[indice]).strip() for f in filas if _tipo(f[indice]) != VACIO]
        if len(valores) != len(filas) or len(set(valores)) != len(valores):
            continue
        if not all(PATRON_CODIGO.match(v) and any(c.isdigit() for c in v)
                   for v in valores):
            continue
        if _es_numeracion_de_filas(valores):
            continue
        tiene_letras = all(any(c.isalpha() for c in v) for v in valores)
        candidatas.append((0 if tiene_letras else 1, indice))
    return min(candidatas)[1] if candidatas else None


def puede_ser_lista_oficial(hoja):
    """Una nomina tiene UNA FILA POR PERSONA. Un registro de eventos, no.

    Sin esta comprobacion, un archivo llamado 'registros_logs.csv' coincide con el
    patron 'registro' y se toma por lista de matricula: la base sale con una fila
    por cada acceso al aula virtual en vez de una por estudiante.
    """
    filas = hoja["filas"]
    if not filas:
        return False
    correo = _columna_correo(hoja["columnas"], filas)
    excluidas = {correo} if correo is not None else set()
    nombre = _columna_nombre(hoja["columnas"], filas, excluidas)
    indice = nombre if nombre is not None else correo
    if indice is None:
        return False
    valores = [str(f[indice]).strip() for f in filas if _tipo(f[indice]) != VACIO]
    if not valores:
        return False
    return len(set(valores)) >= len(filas) * 0.9


def elegir_lista_oficial(fuentes, config):
    """Devuelve la fuente que hace de lista oficial, o None si no hay candidata."""
    candidatas = [f for f in fuentes if puede_ser_lista_oficial(f["hojas"][0])]
    if not candidatas:
        return None, "ninguna tabla tiene una fila por persona"

    patrones = [normalizar(p) for p in config["patrones_lista_oficial"]]
    for fuente in candidatas:
        nombre = normalizar(fuente["archivo"])
        if any(p in nombre for p in patrones):
            return fuente, "coincide con los patrones de lista oficial"

    mejor, mejor_conteo = None, 0
    for fuente in candidatas:
        hoja = fuente["hojas"][0]
        indice = _columna_correo(hoja["columnas"], hoja["filas"])
        conteo = 0 if indice is None else len({f[indice] for f in hoja["filas"]})
        if conteo > mejor_conteo:
            mejor, mejor_conteo = fuente, conteo
    if mejor:
        return mejor, "es la tabla con mas correos unicos de persona"

    mejor = max(candidatas, key=lambda f: len(f["hojas"][0]["filas"]))
    return mejor, "es la tabla con una fila por persona mas completa"


def construir_estudiantes(hoja):
    correo = _columna_correo(hoja["columnas"], hoja["filas"])
    excluidas = {correo} if correo is not None else set()
    nombre = _columna_nombre(hoja["columnas"], hoja["filas"], excluidas)
    if nombre is not None:
        excluidas.add(nombre)
    codigo = _columna_codigo(hoja["columnas"], hoja["filas"], excluidas)

    estudiantes = []
    for numero, fila in enumerate(hoja["filas"], start=1):
        estudiantes.append({
            "id": str(fila[codigo]).strip() if codigo is not None else f"FILA-{numero:03d}",
            "nombre": str(fila[nombre]).strip() if nombre is not None else "",
            "correo": str(fila[correo]).strip() if correo is not None else "",
        })
    return estudiantes, {"codigo": codigo, "nombre": nombre, "correo": correo}


# ------------------------------------------------------------------ integracion
MUESTRA_IDENTIDAD = 60


def valor_identidad(fila, clave):
    partes = [str(fila[i]).strip() for i in clave
              if i < len(fila) and fila[i] is not None and str(fila[i]).strip()]
    return " ".join(partes)


def _claves_candidatas(total_columnas):
    """Cada columna sola, y despues cada par de columnas vecinas.

    El par hace falta cuando la planilla parte la identidad en dos, por ejemplo
    'Apellidos' en una columna y 'Nombres' en la de al lado.
    """
    for indice in range(total_columnas):
        yield (indice,)
    for indice in range(total_columnas - 1):
        yield (indice, indice + 1)


# Cuanto vale cada forma de reconocer. Una coincidencia exacta es evidencia dura;
# un parecido de texto es una conjetura. Sin esta diferencia, juntar dos columnas
# casi siempre "resuelve" mas filas, aunque sea por caminos mucho mas debiles.
CALIDAD = {"codigo": 1.0, "correo": 1.0, "nombre_exacto": 1.0,
           "nombre_con_inicial": 0.75, "parecido": 0.4}


def _clave_identidad(hoja, reconocedor):
    """Elige que columna (o par de columnas) identifica al estudiante."""
    muestra = hoja["filas"][:MUESTRA_IDENTIDAD]
    mejor, mejor_puntaje = (0,), (-1.0, -1)
    for clave in _claves_candidatas(len(hoja["columnas"])):
        calidad, distintos = 0.0, set()
        for fila in muestra:
            est, metodo, _, candidatos = reconocedor.buscar(valor_identidad(fila, clave))
            if est is not None:
                calidad += CALIDAD.get(metodo, 0.4)
                distintos.add(est["id"])
            elif candidatos:
                calidad += 0.1
        puntaje = (calidad, len(distintos))
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = clave, puntaje
    return mejor, mejor_puntaje


def integrar(fuentes, estudiantes, reconocedor, columnas_oficial, fuente_oficial):
    """Devuelve (columnas_base, filas_base, cobertura, emparejamientos, incidencias,
    diccionario)."""
    columnas_base, diccionario = [], []
    valores = {est["id"]: {} for est in estudiantes}
    cobertura, emparejamientos, incidencias = [], [], []

    # La lista oficial abre la base con sus columnas tal cual.
    hoja_oficial = fuente_oficial["hojas"][0]
    for indice, columna in enumerate(hoja_oficial["columnas"]):
        columnas_base.append(columna)
        diccionario.append({
            "columna_en_base": columna,
            "archivo": fuente_oficial["archivo"],
            "hoja": hoja_oficial["hoja"],
            "columna_original": columna,
            "escala_detectada": escala_de_columna(columna) or "",
            "papel": "lista oficial",
        })
    for est, fila in zip(estudiantes, hoja_oficial["filas"]):
        for indice, columna in enumerate(hoja_oficial["columnas"]):
            valores[est["id"]][columna] = fila[indice]

    for fuente in fuentes:
        if fuente is fuente_oficial:
            continue
        varias_hojas = len(fuente["hojas"]) > 1
        for hoja in fuente["hojas"]:
            etiqueta = (f"{fuente['etiqueta']} · {hoja['hoja']}"
                        if varias_hojas else fuente["etiqueta"])
            _integrar_hoja(hoja, etiqueta, fuente, reconocedor, estudiantes, valores,
                           columnas_base, diccionario, cobertura, emparejamientos,
                           incidencias)

    filas_base = [[valores[est["id"]].get(c) for c in columnas_base]
                  for est in estudiantes]
    incidencias.extend(_detectar_columnas_gemelas(columnas_base, filas_base,
                                                  diccionario))
    return columnas_base, filas_base, cobertura, emparejamientos, incidencias, diccionario


def _detectar_columnas_gemelas(columnas_base, filas_base, diccionario):
    """Avisa cuando dos archivos distintos traen exactamente los mismos valores.

    Dos exportaciones del mismo cuestionario guardadas con nombres distintos tienen
    huellas SHA-256 distintas (cambia una fecha interna del Excel) pero los mismos
    datos. La huella no las detecta; comparar los valores ya integrados, si.
    No se elimina nada: solo se reporta, porque dos columnas pueden coincidir de
    forma legitima.
    """
    procedencia = {d["columna_en_base"]: d["archivo"] for d in diccionario}
    grupos = {}
    for indice, columna in enumerate(columnas_base):
        valores = tuple("" if f[indice] is None else str(f[indice])
                        for f in filas_base)
        if not any(valores):
            continue
        grupos.setdefault(valores, []).append(columna)

    incidencias = []
    for columnas in grupos.values():
        archivos = {procedencia.get(c, "?") for c in columnas}
        if len(columnas) < 2 or len(archivos) < 2:
            continue
        incidencias.append({
            "tipo": "columnas_con_valores_identicos",
            "archivo": " | ".join(sorted(archivos)),
            "detalle": (f"estas columnas tienen exactamente los mismos valores en "
                        f"todos los estudiantes: {' | '.join(columnas)}. Puede que "
                        f"sean el mismo dato exportado dos veces. NO se elimino "
                        f"ninguna: revisa si necesitas todas."),
        })
    return incidencias


def _columnas_de_valor(hoja, identidad):
    """Columnas que llevan cifras. Una fila esta 'vacia' si le faltan todas estas.

    Sin esto, una fila que solo trae el nombre del estudiante y ninguna nota
    parece completa, y la etapa siguiente no puede distinguir 'no rindio' de
    'no figura'.
    """
    numericas = []
    for indice in range(len(hoja["columnas"])):
        if indice in identidad:
            continue
        tipos = [_tipo(f[indice]) for f in hoja["filas"]]
        llenas = [t for t in tipos if t != VACIO]
        if llenas and sum(1 for t in llenas if t == "numero") >= len(llenas) * 0.6:
            numericas.append(indice)
    if numericas:
        return numericas
    return [i for i in range(len(hoja["columnas"])) if i not in identidad]


# Nombres que produce nuestra propia plantilla de transcripcion: son rastro de
# procedencia, no datos del estudiante.
METADATOS = {"archivo_origen", "origen"}


def _parece_codigo_de_persona(hoja, indice):
    """Una columna de codigos: un identificador por fila, no una medicion.

    'EST-2026-001' es un codigo; una nota de 18 no lo es. Se exige que TODOS los
    valores sean distintos y que mezclen letras y digitos: asi una calificacion
    o un numero de fila nunca se confunde con un codigo.
    """
    valores = [str(f[indice]).strip() for f in hoja["filas"]
               if _tipo(f[indice]) != VACIO]
    if len(valores) != len(hoja["filas"]) or len(set(valores)) != len(valores):
        return False
    if _es_numeracion_de_filas(valores):
        return False
    return all(PATRON_CODIGO.match(v) and any(c.isdigit() for c in v)
               and any(c.isalpha() for c in v) for v in valores)


def _otras_columnas_de_identidad(hoja, reconocedor, clave):
    """Columnas que TAMBIEN identifican a la persona, aunque no sean la clave.

    Son de dos tipos, y ambos ensucian la base repitiendo la identidad fila a fila:

    1. Las que el reconocedor resuelve a un estudiante de la lista oficial
       (por ejemplo una segunda columna de nombre).
    2. Las que son un codigo de OTRO sistema. El aula virtual puede numerar
       'EST-2026-001' mientras la matricula usa 'EST-101': no cruzan con nadie,
       pero siguen siendo identificadores, no datos que medir.

    Devuelve (indices_de_identidad, indices_de_codigo_ajeno).
    """
    muestra = hoja["filas"][:MUESTRA_IDENTIDAD]
    if not muestra:
        return set(), set()
    extras, ajenos = set(), set()
    for indice in range(len(hoja["columnas"])):
        if indice in clave:
            continue
        aciertos = sum(1 for f in muestra
                       if reconocedor.buscar(valor_identidad(f, (indice,)))[0])
        if aciertos >= len(muestra) * 0.8:
            extras.add(indice)
        elif _parece_codigo_de_persona(hoja, indice):
            ajenos.add(indice)
    return extras, ajenos


def _integrar_hoja(hoja, etiqueta, fuente, reconocedor, estudiantes, valores,
                   columnas_base, diccionario, cobertura, emparejamientos,
                   incidencias):
    identidad, _ = _clave_identidad(hoja, reconocedor)
    identidad_extra, codigos_ajenos = _otras_columnas_de_identidad(
        hoja, reconocedor, identidad)
    for indice in sorted(codigos_ajenos):
        incidencias.append({
            "tipo": "codigo_de_otro_sistema",
            "archivo": etiqueta,
            "valor_original": str(hoja["filas"][0][indice]).strip(),
            "detalle": (f"la columna '{hoja['columnas'][indice]}' es un codigo de "
                        f"estudiante, pero NO coincide con ningun codigo de la lista "
                        f"oficial: son dos numeraciones distintas. El cruce de este "
                        f"archivo se hizo por nombre, que es menos seguro. Revisa "
                        f"EMPAREJAMIENTOS."),
        })
    # Las columnas que identifican no son cifras: si no se excluyen todas, una
    # hoja con los nombres cargados y las notas en blanco parece completa, y la
    # etapa siguiente ya no distingue 'no rindio' de 'no figura'.
    columnas_valor = _columnas_de_valor(
        hoja, set(identidad) | identidad_extra | codigos_ajenos)

    # Un archivo de registros del aula virtual se resume, no se integra fila a fila.
    claves_unicas = len({valor_identidad(f, identidad) for f in hoja["filas"]})
    if parece_registro_de_actividad(hoja, claves_unicas, len(estudiantes)):
        columnas, resumen, inc = resumir(hoja, identidad, reconocedor, etiqueta)
        incidencias.extend(inc)
        incidencias.append({
            "tipo": "archivo_tratado_como_registro_de_actividad",
            "archivo": etiqueta,
            "detalle": f"{len(hoja['filas'])} filas y {claves_unicas} identidades "
                       f"distintas: se resumio por estudiante y el archivo completo "
                       f"queda intacto en bases_de_datos",
        })
        for columna in columnas:
            if columna not in columnas_base:
                columnas_base.append(columna)
                diccionario.append({
                    "columna_en_base": columna, "archivo": fuente["archivo"],
                    "hoja": hoja["hoja"], "columna_original": "(resumen del registro)",
                    "escala_detectada": "", "papel": "resumen de actividad",
                })
        for est in estudiantes:
            fila = resumen.get(est["id"])
            if fila:
                valores[est["id"]].update(fila)
            cobertura.append({
                "id_estudiante": est["id"], "estudiante": est["nombre"],
                "archivo": etiqueta,
                "situacion": "encontrado" if fila else "ausente",
                "detalle": "" if fila else "no tiene ningun registro en la plataforma",
            })
        return

    nuevas = []
    for indice, columna in enumerate(hoja["columnas"]):
        nombre = f"[{etiqueta}] {columna}"
        nuevas.append(nombre)
        if nombre not in columnas_base:
            columnas_base.append(nombre)
            diccionario.append({
                "columna_en_base": nombre,
                "archivo": fuente["archivo"],
                "hoja": hoja["hoja"],
                "columna_original": columna,
                "escala_detectada": escala_de_columna(columna) or "",
                "papel": _papel(indice, columna, identidad,
                                identidad_extra | codigos_ajenos),
            })

    asignados = {}          # id_estudiante -> numero de fila de origen
    pendientes = []         # filas ambiguas, se reintentan por eliminacion
    sin_resolver = []

    for numero, fila in enumerate(hoja["filas"], start=1):
        crudo = valor_identidad(fila, identidad)
        est, metodo, puntaje, candidatos = reconocedor.buscar(crudo)

        if est is None and candidatos:
            pendientes.append((numero, fila, crudo, candidatos, metodo, puntaje))
            continue
        if est is None:
            sin_resolver.append((numero, fila, crudo, metodo, puntaje))
            continue

        _asignar(est, fila, hoja, nuevas, valores, asignados, numero, etiqueta,
                 crudo, metodo, puntaje, emparejamientos, incidencias)

    # Segunda vuelta: si de los candidatos ambiguos solo queda uno libre, es ese.
    for numero, fila, crudo, candidatos, metodo, puntaje in pendientes:
        libres = [c for c in candidatos if c["id"] not in asignados]
        if len(libres) == 1:
            est = libres[0]
            _asignar(est, fila, hoja, nuevas, valores, asignados, numero, etiqueta,
                     crudo, "resuelto_por_eliminacion", puntaje, emparejamientos,
                     incidencias)
            incidencias.append({
                "tipo": "ambiguedad_resuelta_por_eliminacion",
                "archivo": etiqueta,
                "fila_origen": numero,
                "valor_original": str(crudo),
                "detalle": (f"'{crudo}' podia ser {' o '.join(c['nombre'] for c in candidatos)}; "
                            f"los demas ya estaban asignados en este archivo, "
                            f"se asigno a {est['nombre']} ({est['id']}). REVISAR."),
                "contenido_fila": _texto_fila(hoja["columnas"], fila),
            })
        else:
            nombres = " o ".join(c["nombre"] for c in candidatos)
            sin_resolver.append((numero, fila, crudo,
                                 f"{metodo} (candidatos: {nombres})", puntaje))
            for candidato in candidatos:
                cobertura.append({
                    "id_estudiante": candidato["id"],
                    "estudiante": candidato["nombre"],
                    "archivo": etiqueta,
                    "situacion": "no_reconocido",
                    "detalle": f"fila {numero} ambigua: '{crudo}'",
                })

    for numero, fila, crudo, metodo, puntaje in sin_resolver:
        datos = [fila[i] for i in range(len(hoja["columnas"])) if i not in identidad]
        es_nota_al_pie = all(_tipo(v) == VACIO for v in datos)
        tipo = ("fila_apartada_sin_datos" if es_nota_al_pie
                else "fila_ambigua_sin_resolver" if "candidatos" in metodo
                else "fila_no_reconocida")
        incidencias.append({
            "tipo": tipo,
            "archivo": etiqueta,
            "fila_origen": numero,
            "valor_original": str(crudo),
            "detalle": f"metodo: {metodo}; mejor parecido: {puntaje:.2f}",
            "contenido_fila": _texto_fila(hoja["columnas"], fila),
        })

    ya_registrados = {(c["id_estudiante"], c["archivo"]) for c in cobertura}
    for est in estudiantes:
        if (est["id"], etiqueta) in ya_registrados:
            continue
        if est["id"] in asignados:
            fila = hoja["filas"][asignados[est["id"]] - 1]
            vacia = all(_tipo(fila[i]) == VACIO for i in columnas_valor)
            situacion = "encontrado_vacio" if vacia else "encontrado"
            detalle = "figura en el archivo pero sin ninguna cifra" if vacia else ""
        else:
            situacion, detalle = "ausente", "no figura en este archivo"
        cobertura.append({
            "id_estudiante": est["id"],
            "estudiante": est["nombre"],
            "archivo": etiqueta,
            "situacion": situacion,
            "detalle": detalle,
        })


def _papel(indice, columna, identidad, identidad_extra):
    """Que cumple una columna en la base: identifica, es rastro, o es un dato."""
    if indice in identidad or indice in identidad_extra:
        return "identifica al estudiante"
    if str(columna).strip().lower() in METADATOS:
        return "metadato de procedencia"
    return "dato"


def _asignar(est, fila, hoja, nuevas, valores, asignados, numero, etiqueta, crudo,
             metodo, puntaje, emparejamientos, incidencias):
    if est["id"] in asignados:
        incidencias.append({
            "tipo": "colision_dos_filas_al_mismo_estudiante",
            "archivo": etiqueta,
            "fila_origen": numero,
            "valor_original": str(crudo),
            "detalle": (f"la fila {asignados[est['id']]} ya se habia asignado a "
                        f"{est['nombre']} ({est['id']}); esta fila NO se sobrescribio "
                        f"y se conserva aqui completa"),
            "contenido_fila": _texto_fila(hoja["columnas"], fila),
        })
        return

    asignados[est["id"]] = numero
    for indice, columna in enumerate(nuevas):
        valores[est["id"]][columna] = fila[indice]
    emparejamientos.append({
        "archivo": etiqueta,
        "fila_origen": numero,
        "valor_original": str(crudo),
        "id_estudiante": est["id"],
        "estudiante": est["nombre"],
        "metodo": metodo,
        "puntaje": round(puntaje, 3),
    })


def _texto_fila(columnas, fila):
    partes = []
    for columna, valor in zip(columnas, fila):
        if _tipo(valor) != VACIO:
            partes.append(f"{columna}={valor}")
    return " ; ".join(partes)
