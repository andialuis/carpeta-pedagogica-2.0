"""Paso: construir_tab_general

La primera pestaña: el estado del curso de un vistazo.

Quien abre el tablero en una reunion mira esta pantalla durante diez segundos antes
de que alguien empiece a hablar. En esos diez segundos tiene que quedarle claro
cuantos estudiantes hay, como se reparten y a quien hay que atender primero. Por eso
casi todo aqui es cifra grande, barra o color: el texto corrido se lee de cerca, y
esta pantalla se ve de lejos.

Dos cosas que se hacen aparte a proposito: los estudiantes se muestran por su codigo
—el tablero se proyecta— y quienes abandonaron van en su propio bloque, para que no
se mezclen con los promedios de quienes siguieron.
"""

from graficos import (Bloque, barras_horizontales, caja, matriz_cuadrantes, dispersion, dona,
                      escapar, fila_de_cajas, texto_plano, titulo_seccion)
from paso_leer_resultados import (arreglar_plurales, entero, limpiar_titulo,
                                  numero, plural)


def _kpi(valor, texto, color):
    html = (f'<div class="kpi" style="border-top-color:{color}">'
            f'<div class="n" style="color:{color}">{escapar(valor)}</div>'
            f'<div class="t">{escapar(texto)}</div></div>')
    return Bloque(html, 290, 30, "grafico")


def _barras_de_urgencia(filas, config, cuantos=12):
    datos = [(f"{f.get('codigo','')} · {str(f.get('perfil','') or '')[:20]}",
              numero(f.get("urgencia")))
             for f in filas[:cuantos]]
    if not datos:
        return Bloque("", 0, 0, "grafico")
    return barras_horizontales(
        datos, ancho=1120, alto_barra=26, color=config["prioridades"]["urgente"],
        formato="{:.2f}", titulo="Estudiantes con mayor necesidad de intervención (Urgencia de 0 a 2)")


def _tabla_prioridades(filas, config, limite):
    if not filas:
        return Bloque('<div class="vacio">El análisis no entregó una lista de '
                      'prioridades.</div>', 560, 90, "texto")
    colores = config["prioridades"]
    cuerpo, caracteres = [], 0
    for fila in filas[:limite]:
        urgencia = numero(fila.get("urgencia"))
        situacion = str(fila.get("situacion", "") or "")
        color = colores["urgente"] if situacion == "abandono" else (
            colores["alta"] if urgencia >= 1.0 else
            colores["media"] if urgencia >= 0.6 else colores["baja"])
        motivo = str(fila.get("motivo", "") or "")
        perfil = str(fila.get("perfil", "") or "")
        caracteres += len(motivo) + len(perfil) + 24
        cuerpo.append(
            f'<tr><td><b>{escapar(fila.get("puesto", ""))}</b></td>'
            f'<td class="cod">{escapar(fila.get("codigo", ""))}</td>'
            f'<td><span class="pill" style="background:{color}">'
            f'{escapar(f"{urgencia:.2f}")}</span></td>'
            f'<td><b>{escapar(perfil)}</b></td>'
            f'<td style="color:#475569">{escapar(motivo)}</td></tr>')
    extra = ""
    if len(filas) > limite:
        extra = (f'<p style="font-size:13px;color:#64748b;margin:10px 0 0">'
                 f'Se muestran los {limite} primeros de {len(filas)}. '
                 f'La lista completa está en la hoja PRIORIDADES de Excel.</p>')
        caracteres += 90
    html = ('<table class="tabla"><thead><tr><th>#</th><th>Código</th>'
            '<th>Urgencia</th><th>Perfil Detectado</th><th>Motivo / Diagnóstico Clave</th></tr></thead>'
            f'<tbody>{"".join(cuerpo)}</tbody></table>{extra}')
    return Bloque(html, 1180, 46 + len(filas[:limite]) * 44 + (34 if extra else 0),
                  "texto")


def _tarjetas_perfiles(perfiles):
    """Renderiza tarjetas nítidas de cohortes/perfiles con códigos y significado."""
    if not perfiles:
        return Bloque("", 0, 0, "texto")
    html_cards = ['<div class="perfiles-grid">']
    caracteres = 0
    for p in perfiles:
        nom = str(p.get("perfil", "")).strip()
        count = entero(p.get("estudiantes", 0))
        significado = str(p.get("que_significa", "") or "")
        cods = str(p.get("codigos", "") or "")
        r_med = numero(p.get("rendimiento_medio"))
        e_med = numero(p.get("esfuerzo_medio"))

        clase_p = "medio"
        if "destacado" in nom.lower() or "alto" in nom.lower():
            clase_p = "destacado"
        elif "riesgo" in nom.lower() or "bajo" in nom.lower() or "abandono" in nom.lower():
            clase_p = "riesgo"
        elif "autonomo" in nom.lower() or "teorico" in nom.lower():
            clase_p = "autonomo"
        elif "dificultad" in nom.lower() or "rezago" in nom.lower() or "esfuerzo" in nom.lower():
            clase_p = "alerta"

        caracteres += len(nom) + len(significado) + len(cods) + 50
        html_cards.append(
            f'<div class="perfil-card {clase_p}">'
            f'<div class="header-p"><span class="nom">{escapar(nom)}</span>'
            f'<span class="count">{count} {plural(count, "estudiante")}</span></div>'
            f'<p class="desc">{escapar(significado)}</p>'
            f'<div class="metricas">'
            f'<span><b>Rendimiento:</b> {r_med:.2f}</span>'
            f'<span><b>Esfuerzo:</b> {e_med:.2f}</span></div>'
            f'<div class="codigos"><b>Integrantes:</b> {escapar(cods)}</div>'
            f'</div>')
    html_cards.append('</div>')
    return Bloque("".join(html_cards), 1180, len(perfiles) * 45, "grafico")


def construir(datos, config, metrica_destacada):
    """Devuelve (html, bloques, resumen) de la pestaña 1."""
    bloques = []
    prioridades = datos.get("PRIORIDADES", [])
    perfiles = datos.get("PERFILES", [])
    hallazgos = datos.get("HALLAZGOS", [])
    acciones = datos.get("ACCIONES", [])

    total = len(prioridades)
    abandonos = [f for f in prioridades
                 if str(f.get("situacion", "")).strip().lower() == "abandono"]
    activos = total - len(abandonos)

    bloques.append(texto_plano(
        '<div class="intro"><b>Radiografía del Curso:</b> Esta pestaña ofrece una vista ejecutiva '
        'de la distribución del grupo, los perfiles de comportamiento detectados y la priorización de estudiantes '
        'para intervención temprana en el aula.</div>',
        1180, 210, relleno=58))

    # --- La cifra que el docente pidio destacar --------------------------------
    if metrica_destacada:
        cifra, explicacion = _buscar_metrica(metrica_destacada, datos, config)
        bloques.append(Bloque(
            f'<div class="hero"><div class="cifra">{escapar(cifra)}</div>'
            f'<div class="lado"><div class="eti">Hallazgo / Métrica Destacada</div>'
            f'<p class="txt"><b>{escapar(metrica_destacada)}</b></p>'
            f'<p class="txt" style="font-size:14.5px;opacity:.9;margin-top:6px">'
            f'{escapar(explicacion)}</p></div></div>',
            1180, 160, "grafico"))

    # --- Cifras de cabecera ----------------------------------------------------
    c = config["colores"]
    retencion = f"{(activos / total * 100):.0f}%" if total else "100%"
    tarjetas = [
        _kpi(f"{total}", f"Total estudiantes ({activos} activos)", c["ucb2"]),
        _kpi(retencion, "Tasa de retención activa", "#059669"),
        _kpi(len(abandonos), "Deserción / Abandonos", "#dc2626"),
        _kpi(len(hallazgos), "Hallazgos demostrados", "#7c3aed"),
    ]
    html_kpis = '<div class="kpis">' + "".join(t.html for t in tarjetas) + '</div>'
    bloques.append(Bloque(html_kpis, 1180, 142, "grafico"))

    # --- Como se reparte el curso ---------------------------------------------
    partes = [(str(p.get("perfil", "")), entero(p.get("estudiantes")))
              for p in perfiles if entero(p.get("estudiantes")) > 0]
    graf_dona = dona(partes, ancho=560, centro_valor=str(total),
                     centro_texto="estudiantes") if partes else Bloque("", 0, 0, "grafico")

    # --- Matriz 2D de Comportamiento ------------------------------------------
    puntos_perfil = []
    for p in perfiles:
        cods = [c.strip() for c in str(p.get("codigos", "")).split(",") if c.strip()]
        r_val = numero(p.get("rendimiento_medio"))
        e_val = numero(p.get("esfuerzo_medio"))
        for cd in cods:
            puntos_perfil.append((cd, e_val, r_val))

    graf_matriz = matriz_cuadrantes(puntos_perfil, ancho=560, alto=320) if puntos_perfil else Bloque("", 0, 0, "grafico")

    fila_grupos = fila_de_cajas([("Distribución por Perfiles", graf_dona),
                                 ("Matriz 2D: Esfuerzo vs. Rendimiento", graf_matriz)])
    bloques.append(fila_grupos)

    # --- Cohortes / Perfiles detallados ---------------------------------------
    tarjetas_perfil = _tarjetas_perfiles(perfiles)
    bloques.append(tarjetas_perfil)

    # --- Prioridades -----------------------------------------------------------
    activos_ordenados = [f for f in prioridades
                         if str(f.get("situacion", "")).strip().lower() != "abandono"]
    caja_urgencia = caja("", _barras_de_urgencia(activos_ordenados, config))
    tabla = _tabla_prioridades(activos_ordenados, config,
                               config["maximo_estudiantes_en_tabla"])
    bloques.append(tabla)

    # --- Los que se fueron, en su propio bloque --------------------------------
    if abandonos:
        codigos = ", ".join(escapar(f.get("codigo", "")) for f in abandonos)
        bloque_ab = texto_plano(
            f'<div class="aviso"><b>{plural(len(abandonos), "estudiante")} '
            f'en abandono / retiro</b> (separados para auditoría y seguimiento formal): {codigos}.</div>',
            1180, 160, relleno=40)
        bloques.append(bloque_ab)
    else:
        bloque_ab = Bloque("", 0, 0, "texto")

    html = [bloques[0].html]
    if metrica_destacada:
        html.append(bloques[1].html)
    html.append(html_kpis)

    tit_dist = titulo_seccion("Distribución y Matriz de Comportamiento")
    bloques.append(tit_dist)
    html.append(tit_dist.html)
    html.append(fila_grupos.html)

    tit_perf = titulo_seccion("Detalle de Perfiles y Grupos de Aprendizaje")
    bloques.append(tit_perf)
    html.append(tit_perf.html)
    html.append(tarjetas_perfil.html)

    if caja_urgencia.html:
        tit_urg = titulo_seccion("Prioridades de Atención e Intervención Docente")
        bloques.append(tit_urg)
        html.append(tit_urg.html)
        html.append(caja_urgencia.html)
        bloques.append(caja_urgencia)

    html.append(tabla.html)
    if bloque_ab.html:
        html.append(bloque_ab.html)

    resumen = {
        "pestana": "1 · Vision general",
        "elementos": len(tarjetas) + len(perfiles) + 4,
        "detalle": (f"{plural(total, 'estudiante')}, "
                    f"{plural(len(perfiles), 'perfil', 'perfiles')}, "
                    f"{plural(len(acciones), 'accion', 'acciones')} disponibles"),
        "fuentes": "PRIORIDADES, PERFILES, HALLAZGOS, DATOS_GRAFICOS",
    }
    return "".join(html), bloques, resumen


def _buscar_metrica(pedido, datos, config):
    """Busca en las hojas del analisis la cifra que el docente quiso destacar.

    El lugar mas visible del tablero tiene que llevar un NUMERO, no un pedazo de
    frase. Por eso se busca la fila que mejor coincide con lo que se pidio y de ahi
    se extrae una cifra de verdad: primero los campos que ya son numeros, y si no,
    el numero con el que empieza el texto de la cifra.

    Si no se encuentra nada, NO se inventa: se muestra el numero de hallazgos y se
    dice por que. Poner cualquier cosa ahi porque quedaba bonito es la peor forma de
    arruinar un tablero.
    """
    from paso_leer_resultados import normalizar
    buscado = normalizar(pedido)
    palabras = [p for p in buscado.split() if len(p) > 3]

    # La hoja INDICADORES son, por definicion, las metricas del curso: si algo
    # coincide ahi, gana. Buscar una «metrica» y devolver el titulo de un hallazgo
    # es contestar otra pregunta.
    peso_hoja = {"INDICADORES": 1.6, "PERFILES": 1.1, "HALLAZGOS": 1.0,
                 "HIPOTESIS": 1.0}
    mejor, mejor_puntaje, mejor_hoja = None, 0, ""
    for hoja in ("INDICADORES", "PERFILES", "HALLAZGOS", "HIPOTESIS"):
        for fila in datos.get(hoja, []):
            texto = normalizar(" ".join(str(v) for v in fila.values() if v))
            puntaje = sum(1 for p in palabras if p in texto) * peso_hoja[hoja]
            if puntaje > mejor_puntaje:
                mejor, mejor_puntaje, mejor_hoja = fila, puntaje, hoja

    if mejor is None or mejor_puntaje < max(1, len(palabras) // 2):
        hallazgos = datos.get("HALLAZGOS", [])
        return (str(len(hallazgos)),
                f"No se encontro «{pedido}» entre las cifras del analisis, asi que "
                f"se muestra cuantos hallazgos trae. Nada se invento para llenar "
                f"este lugar.")

    cifra = _primer_numero(mejor)
    titulo = ""
    for campo in ("que_medir", "hallazgo", "perfil", "hipotesis"):
        if mejor.get(campo):
            titulo = limpiar_titulo(mejor[campo], config)
            break
    detalle = str(mejor.get("cifra") or mejor.get("se_enciende_cuando") or "")
    explicacion = arreglar_plurales(
        " ".join(x for x in (titulo, detalle) if x).strip())
    return (cifra, f"{explicacion} · Sale de la hoja {mejor_hoja} del analisis.")


def _primer_numero(fila):
    """La cifra de la fila: primero los campos que ya son numeros; si no, el numero
    con el que empieza el texto."""
    import re
    for campo in ("estudiantes_hoy", "estudiantes_afectados", "estudiantes",
                  "cuantos"):
        if fila.get(campo) not in (None, ""):
            return str(entero(fila[campo]))
    encontrado = re.match(r"\s*(-?\d+(?:[.,]\d+)?)", str(fila.get("cifra", "")))
    if encontrado:
        return encontrado.group(1).replace(".", ",")
    return "—"


def _puntos_de_dispersion(datos):
    """Arma la nube a partir de la hoja DATOS_GRAFICOS del analisis."""
    filas = datos.get("DATOS_GRAFICOS", [])
    por_codigo = {}
    for fila in filas:
        if str(fila.get("grafico", "")).strip() != "relacion":
            continue
        codigo = str(fila.get("etiqueta", "")).strip()
        serie = str(fila.get("serie", "")).strip()
        por_codigo.setdefault(codigo, {})[serie] = numero(fila.get("valor"))
    series = []
    for valores in por_codigo.values():
        for s in valores:
            if s not in series:
                series.append(s)
    if len(series) < 2:
        # Sin dos series no hay nube posible. Se devuelve vacio y la pestaña
        # sencillamente no muestra ese grafico, en vez de fabricar un eje.
        return []
    a, b = series[0], series[1]
    return [(c, v[a], v[b]) for c, v in por_codigo.items() if a in v and b in v]
