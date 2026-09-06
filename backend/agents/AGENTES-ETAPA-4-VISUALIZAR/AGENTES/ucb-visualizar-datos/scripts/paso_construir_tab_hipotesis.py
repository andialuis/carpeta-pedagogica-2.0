"""Paso: construir_tab_hipotesis

La segunda pestaña: que se sospechaba y que resulto.

Lo primero que se ve, antes que cualquier detalle, es un marcador con tres numeros
grandes: confirmadas, descartadas y sin comprobar. Es lo unico que se entiende desde
el fondo de la sala, y es justo lo que la audiencia quiere saber.

Despues vienen dos cosas que se parecen y no son lo mismo, por eso se muestran
distinto:

  - Una HIPOTESIS es algo que alguien sospechaba. Lleva veredicto en color y, debajo,
    una frase en castellano llano que lo explique. El dato tecnico —la p, el tamaño
    del efecto— se esconde detras de un «ver detalle»: quien lo necesita lo abre, y
    quien no, no se traba con el.
  - Un HALLAZGO es algo que aparecio solo. Lleva una barra de alcance, porque «afecta
    a 5» y «afecta a 5 de 25» son frases muy distintas y solo la segunda permite
    decidir.
"""

import re

from graficos import (Bloque, barra_de_alcance, barras_horizontales, caja,
                      escapar, texto_de_tarjeta, texto_plano, titulo_seccion)
from paso_leer_resultados import (arreglar_plurales, clasificar_veredicto,
                                  entero, limpiar_titulo, numero, plural)

ETIQUETAS = {
    "confirmada": ("Confirmada", "#1fa98a"),
    "descartada": ("Descartada", "#e05a3a"),
    "sin_comprobar": ("Sin comprobar", "#8a8d94"),
}


def _frase_llana(fila, clase):
    """Traduce el veredicto a una frase que se entienda sin saber estadistica."""
    cifra = str(fila.get("cifra", "") or "").strip()
    n = entero(fila.get("estudiantes"))
    if clase == "sin_comprobar":
        detalle = str(fila.get("detalle", "") or "")
        return detalle or ("Los datos disponibles no permiten responder esta "
                           "pregunta. No es un fallo del analisis: es lo que hay.")
    if clase == "confirmada":
        base = "Los numeros respaldan la sospecha"
    else:
        base = "Los numeros no respaldan la sospecha"
    if cifra and n:
        return f"{base}: {cifra}, medido sobre {plural(n, 'estudiante')}."
    if cifra:
        return f"{base}: {cifra}."
    return base + "."


def _barras_de_la_hipotesis(fila, config):
    """Si la hipotesis comparo dos grupos, se dibujan como barras.

    Dos numeros en una frase se olvidan; dos barras de distinto largo, no.
    """
    cifra = str(fila.get("cifra", "") or "")
    if " contra " not in cifra:
        return Bloque("", 0, 0, "grafico")
    try:
        izquierda, resto = cifra.split(" contra ", 1)
        derecha = resto.split("(")[0]
        a, b = numero(izquierda.strip()), numero(derecha.strip())
    except (ValueError, IndexError):
        return Bloque("", 0, 0, "grafico")
    if a == 0 and b == 0:
        return Bloque("", 0, 0, "grafico")
    grupo = str(fila.get("grupo", "") or "el grupo")
    return barras_horizontales(
        [(limpiar_titulo(grupo, config)[:28] or "grupo señalado", a),
         ("el resto del curso", b)],
        ancho=520, color=config["colores"]["ucb2"], formato="{:.3f}",
        maximo=max(a, b) * 1.15)


def _chip_de_cifra(cifra, color):
    """La cifra del hallazgo, en grande y con su frase al lado.

    Antes esto era un campo de texto entre otros tres. Una cifra escondida dentro de
    un parrafo no se lee desde el fondo del aula; puesta en grande, es lo primero
    que se ve de la tarjeta.
    """
    if not cifra:
        return Bloque("", 0, 0, "grafico"), ""
    encontrado = re.search(r"(-?\d+(?:[.,]\d+)?%?)", cifra)
    if not encontrado:
        return Bloque("", 0, 0, "grafico"), cifra
    numero_visible = encontrado.group(1)
    resto = (cifra[:encontrado.start()] + cifra[encontrado.end():]).strip(" ·;,")
    html = (f'<div style="display:flex;align-items:center;gap:16px;'
            f'background:#faf9f6;border-radius:10px;padding:20px 18px;margin-top:12px">'
            f'<div style="font-size:38px;font-weight:800;line-height:1;color:{color}">'
            f'{escapar(numero_visible)}</div>'
            f'<div style="font-size:14.5px;color:#3a3d44">{escapar(resto)}</div></div>')
    return Bloque(html, 1090, 84, "grafico"), ""


def construir(datos, config):
    bloques = []
    hipotesis = datos.get("HIPOTESIS", [])
    hallazgos = datos.get("HALLAZGOS", [])
    total_curso = len(datos.get("PRIORIDADES", [])) or 1

    bloques.append(texto_plano(
        '<div class="intro">Esta pestaña separa dos cosas: lo que alguien '
        'sospechaba antes de mirar los datos, y lo que aparecio sin que nadie lo '
        'buscara. Cada tarjeta trae su cifra y a cuantos estudiantes alcanza.</div>',
        1180, 235, relleno=58))

    # --- El marcador -----------------------------------------------------------
    conteo = {"confirmada": 0, "descartada": 0, "sin_comprobar": 0}
    for fila in hipotesis:
        conteo[clasificar_veredicto(fila.get("veredicto"), config)] += 1
    marcador = []
    for clase in ("confirmada", "descartada", "sin_comprobar"):
        nombre, color = ETIQUETAS[clase]
        marcador.append(f'<div class="m" style="background:{color}">'
                        f'<div class="n">{conteo[clase]}</div>'
                        f'<div class="t">{nombre}s</div></div>')
    html_marcador = '<div class="marcador">' + "".join(marcador) + '</div>'
    bloques.append(Bloque(html_marcador, 1180, 168, "grafico"))

    # --- Las hipotesis ---------------------------------------------------------
    partes = [bloques[0].html, html_marcador]
    titulo = titulo_seccion("Lo que se sospechaba")
    bloques.append(titulo)
    partes.append(titulo.html)
    if not hipotesis:
        vacio = texto_plano('<div class="vacio">El analisis no puso ninguna '
                            'hipotesis a prueba.</div>', 1180, 70)
        bloques.append(vacio)
        partes.append(vacio.html)
    for fila in hipotesis:
        clase = clasificar_veredicto(fila.get("veredicto"), config)
        nombre, color = ETIQUETAS[clase]
        graf = _barras_de_la_hipotesis(fila, config)
        llano = _frase_llana(fila, clase)
        origen = str(fila.get("origen", "") or "")
        tecnico = " · ".join(
            f"{k}: {fila[k]}" for k in ("p", "efecto", "sobrevive_al_ajuste", "detalle")
            if fila.get(k) not in (None, ""))
        cuerpo = (f'<div class="tarjeta" style="border-left-color:{color}">'
                  f'<span class="ver" style="background:{color}">{nombre}</span>'
                  f'<h4>{escapar(str(fila.get("hipotesis", ""))[:220])}</h4>'
                  f'<p class="llano">{escapar(arreglar_plurales(llano))}</p>'
                  + (f'<div style="margin-top:14px">{graf.html}</div>' if graf.html else "")
                  + (f'<details class="detalle"><summary>Ver el detalle tecnico</summary>'
                     f'<div class="cuerpo">{escapar(tecnico)}'
                     + (f' · la planteo: {escapar(origen)}' if origen else "")
                     + '</div></details>' if tecnico else "")
                  + '</div>')
        bloques.append(Bloque("", 1120, 38, "grafico"))   # la insignia de color
        bloques.append(texto_de_tarjeta(
            cuerpo, len(str(fila.get("hipotesis", ""))), len(llano), campos=0))
        if graf.html:
            bloques.append(graf)
        partes.append(cuerpo)

    # --- Los hallazgos, de mayor a menor alcance -------------------------------
    titulo = titulo_seccion("Lo que aparecio sin buscarlo")
    bloques.append(titulo)
    partes.append(titulo.html)
    vistos, unicos = set(), []
    for fila in hallazgos:
        firma = str(fila.get("hallazgo", ""))[:70].lower()
        if firma in vistos:
            continue
        vistos.add(firma)
        unicos.append(fila)
    unicos.sort(key=lambda f: -entero(f.get("estudiantes_afectados")))

    if not unicos:
        vacio = texto_plano('<div class="vacio">El analisis no reporto hallazgos '
                            'que se sostengan.</div>', 1180, 70)
        bloques.append(vacio)
        partes.append(vacio.html)

    # Antes de las tarjetas, todos los hallazgos juntos: es la unica forma de ver
    # cual pesa mas. Leidos de a uno, el ultimo parece tan grave como el primero.
    if len(unicos) >= 2:
        comparativo = caja("Cuantos estudiantes alcanza cada hallazgo",
                           barras_horizontales(
                               [(limpiar_titulo(f.get("hallazgo", ""), config)[:34],
                                 entero(f.get("estudiantes_afectados")))
                                for f in unicos],
                               ancho=1090, alto_barra=28,
                               color=config["colores"]["lav"],
                               maximo=total_curso, formato="{:.0f}"))
        bloques.append(comparativo)
        partes.append(comparativo.html)

    colores_prioridad = config["prioridades"]
    for fila in unicos:
        afectados = entero(fila.get("estudiantes_afectados"))
        prioridad = str(fila.get("prioridad", "media") or "media").strip().lower()
        color = colores_prioridad.get(prioridad, colores_prioridad["media"])
        barra = barra_de_alcance(afectados, total_curso, ancho=1090, color=color)
        cifra = arreglar_plurales(str(fila.get("cifra", "") or ""))
        consecuencia = str(fila.get("si_no_hago_nada", "") or "")
        chip, sobrante = _chip_de_cifra(cifra, color)
        cuerpo = (f'<div class="tarjeta" style="border-left-color:{color}">'
                  f'<span class="ver" style="background:{color}">'
                  f'{escapar(prioridad.capitalize())}</span>'
                  f'<h4>{escapar(arreglar_plurales(limpiar_titulo(fila.get("hallazgo", ""), config))[:110])}</h4>'
                  f'<div style="margin-top:10px">{barra.html}</div>'
                  + (chip.html if chip.html else
                     f'<p class="llano">{escapar(sobrante)}</p>')
                  + f'<div class="campo" style="margin-top:12px">'
                    f'<b>Que pasa si no se hace nada</b>{escapar(consecuencia)}</div>'
                  + '</div>')
        bloques.append(barra)
        bloques.append(Bloque("", 1120, 38, "grafico"))   # la insignia de color
        if chip.html:
            bloques.append(chip)
        bloques.append(texto_de_tarjeta(
            cuerpo, min(110, len(str(fila.get("hallazgo", "")))),
            len(consecuencia) + len(sobrante), campos=1))
        partes.append(cuerpo)

    partes.append(f'<p style="font-size:14px;color:#5c5f66;margin-top:18px">'
                  f'El analisis entrego {plural(len(unicos), "hallazgo")} y '
                  f'{plural(len(hipotesis), "hipotesis", "hipotesis")}. '
                  f'Se muestran todos: ni uno mas, ni uno menos.</p>')

    resumen = {
        "pestana": "2 · Hipotesis y hallazgos",
        "elementos": len(hipotesis) + len(unicos) + 1,
        "detalle": (f"{conteo['confirmada']} confirmadas, "
                    f"{conteo['descartada']} descartadas, "
                    f"{conteo['sin_comprobar']} sin comprobar; "
                    f"{plural(len(unicos), 'hallazgo')}"),
        "fuentes": "HIPOTESIS, HALLAZGOS",
    }
    return "".join(partes), bloques, resumen
