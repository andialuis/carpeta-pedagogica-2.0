"""Los graficos del tablero, dibujados a mano en SVG.

No es un paso del proceso: es la caja de herramientas de dibujo. Esta escrita asi
por una razon que decide si el tablero sirve o no: el archivo debe abrirse con doble
clic en una sala sin internet. Cualquier libreria de graficos que se enlace desde la
red convierte el tablero en una pantalla en blanco justo cuando se lo esta
proyectando, y una libreria incrustada entera pesa mas que todo el resto del archivo.

Cada funcion devuelve dos cosas: el SVG y la superficie que ocupa. Lo segundo es lo
que permite medir despues si el tablero cumple el equilibrio de 60% grafico y 40%
texto, en vez de suponerlo.
"""

import html as _html


def escapar(texto):
    return _html.escape(str(texto) if texto is not None else "", quote=True)


def _corta(texto, maximo):
    texto = str(texto)
    return texto if len(texto) <= maximo else texto[:maximo - 1] + "…"


class Bloque:
    """Un pedazo del tablero que sabe cuanto ocupa en pantalla y de que tipo es.

    Se mide por ALTURA y no por superficie, y el motivo importa: el tablero es una
    sola columna, asi que lo que decide cuanto grafico ve una persona no es el area
    de cada pieza sino cuantos centimetros de pantalla ocupa mientras baja. Medir
    superficie daba numeros bonitos que no coincidian con lo que se ve.
    """

    def __init__(self, html, ancho, alto, clase):
        self.html = html
        self.ancho = ancho
        self.alto = max(0, int(alto))
        self.area = self.alto          # lo que se suma para el equilibrio
        self.clase = clase             # "grafico" o "texto"

    def __str__(self):
        return self.html


ANCHO_UTIL = 1188          # ancho interior real de una tarjeta a 1280 px
CHROME_TARJETA = 100       # padding + margenes + fila de la insignia, medidos


def texto_de_tarjeta(html, titulo_caracteres, cuerpo_caracteres, campos=1):
    """La altura real de una tarjeta, separando titulo y cuerpo.

    El titulo va a 18 px y el cuerpo a 15 px: contarlos con la misma medida
    subestimaba el texto y hacia que el tablero se declarara mas grafico de lo que
    era. Las constantes salen de medir el archivo ya abierto en el navegador.
    """
    lineas_titulo = max(1, -(-titulo_caracteres // int(ANCHO_UTIL / (18 * 0.52))))
    lineas_cuerpo = max(1, -(-cuerpo_caracteres // int(ANCHO_UTIL / (15 * 0.52))))
    alto = (lineas_titulo * 23.4 + lineas_cuerpo * 23.25
            + campos * 24 + CHROME_TARJETA)
    return Bloque(html, ANCHO_UTIL, alto, "texto")


def texto_plano(html, ancho, caracteres, tamano=15, relleno=0):
    """Un bloque de texto, con la altura que va a ocupar realmente en pantalla.

    Se cuentan las lineas que el texto necesita a ese ancho y se le suma el relleno
    de su contenedor: un parrafo dentro de una tarjeta con 20 px de padding arriba y
    abajo ocupa 40 px mas de pantalla, y esos 40 px son texto a los ojos de quien
    mira.
    """
    por_linea = max(20, int(ancho / (tamano * 0.52)))
    lineas = max(1, -(-caracteres // por_linea))
    return Bloque(html, ancho, lineas * tamano * 1.55 + relleno, "texto")


# ------------------------------------------------------------------ primitivas
def barras_horizontales(datos, ancho=560, alto_barra=30, color="#1fa98a",
                        maximo=None, formato="{:.0f}", titulo=""):
    """Barras horizontales con su etiqueta y su valor. El grafico mas legible de
    lejos que existe: no hay que interpretar angulos ni areas, solo comparar largos."""
    if not datos:
        return Bloque("", 0, 0, "grafico")
    tope = maximo if maximo else max((v for _, v in datos), default=1) or 1
    izquierda = 190
    util = ancho - izquierda - 90
    alto = len(datos) * (alto_barra + 12) + (34 if titulo else 8)
    y = 26 if titulo else 4

    partes = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%" '
              f'style="max-width:{ancho}px" role="img" '
              f'aria-label="{escapar(titulo or "grafico de barras")}">']
    if titulo:
        partes.append(f'<text x="0" y="14" class="g-tit">{escapar(titulo)}</text>')
    for etiqueta, valor in datos:
        largo = max(3, int(util * (float(valor) / tope))) if tope else 3
        partes.append(
            f'<text x="{izquierda - 10}" y="{y + alto_barra * 0.66}" '
            f'text-anchor="end" class="g-eti">{escapar(_corta(etiqueta, 30))}</text>'
            f'<rect x="{izquierda}" y="{y}" width="{util}" height="{alto_barra}" '
            f'rx="6" fill="#eef1f6"/>'
            f'<rect x="{izquierda}" y="{y}" width="{largo}" height="{alto_barra}" '
            f'rx="6" fill="{color}"/>'
            f'<text x="{izquierda + largo + 10}" y="{y + alto_barra * 0.68}" '
            f'class="g-val">{escapar(formato.format(float(valor)))}</text>')
        y += alto_barra + 12
    partes.append("</svg>")
    return Bloque("".join(partes), ancho, alto, "grafico")


def dona(partes_datos, ancho=300, colores=None, centro_valor="", centro_texto=""):
    """Un anillo con el reparto del curso. Se usa una sola vez por pestaña: dos
    donas juntas obligan a comparar angulos, y eso nadie lo hace bien de lejos."""
    total = sum(v for _, v in partes_datos) or 1
    radio, grosor = 92, 30
    cx = cy = 110
    alto = 220
    colores = colores or ["#1fa98a", "#2b5a9c", "#c9a84c", "#e05a3a", "#7b68d4", "#8a8d94"]

    perimetro = 2 * 3.14159265 * radio
    salida = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%" '
              f'style="max-width:{ancho}px" role="img" '
              f'aria-label="reparto: ' +
              escapar(", ".join(f"{e} {v}" for e, v in partes_datos)) + '">']
    recorrido = 0.0
    for i, (_, valor) in enumerate(partes_datos):
        fraccion = float(valor) / total
        largo = perimetro * fraccion
        salida.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radio}" fill="none" '
            f'stroke="{colores[i % len(colores)]}" stroke-width="{grosor}" '
            f'stroke-dasharray="{largo:.2f} {perimetro - largo:.2f}" '
            f'stroke-dashoffset="{-recorrido:.2f}" '
            f'transform="rotate(-90 {cx} {cy})"/>')
        recorrido += largo
    salida.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" '
                  f'class="g-dona-num">{escapar(centro_valor)}</text>')
    salida.append(f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" '
                  f'class="g-dona-txt">{escapar(centro_texto)}</text>')
    y = 30
    for i, (etiqueta, valor) in enumerate(partes_datos):
        salida.append(
            f'<rect x="228" y="{y - 10}" width="12" height="12" rx="3" '
            f'fill="{colores[i % len(colores)]}"/>'
            f'<text x="248" y="{y}" class="g-eti">'
            f'{escapar(_corta(etiqueta, 22))} · {valor}</text>')
        y += 26
    salida.append("</svg>")
    return Bloque("".join(salida), ancho, alto, "grafico")


def matriz_cuadrantes(puntos, ancho=560, alto=330, etiqueta_x="Esfuerzo / Participación (0 a 1)",
                      etiqueta_y="Rendimiento Académico (0 a 1)", destacados=()):
    """Matriz 2D de Comportamiento del Curso dividida en 4 cuadrantes pedagógicos."""
    if not puntos:
        return Bloque("", 0, 0, "grafico")
    izq, aba, arr, der = 55, 42, 24, 20
    w_util = ancho - izq - der
    h_util = alto - aba - arr
    mid_x = izq + w_util / 2
    mid_y = arr + h_util / 2

    def px(v):
        v = max(0.0, min(1.0, float(v)))
        return izq + v * w_util

    def py(v):
        v = max(0.0, min(1.0, float(v)))
        return alto - aba - v * h_util

    s = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%" style="max-width:{ancho}px" role="img" '
         f'aria-label="Matriz de Comportamiento: {len(puntos)} estudiantes">',
         # Cuadrante Superior Derecho: Destacados (Verde)
         f'<rect x="{mid_x}" y="{arr}" width="{w_util/2}" height="{h_util/2}" fill="#f0fdf4" opacity="0.8"/>',
         f'<text x="{ancho - der - 8}" y="{arr + 16}" text-anchor="end" font-size="10.5" font-weight="700" fill="#166534">DESTACADOS (Alto/Alto)</text>',
         # Cuadrante Superior Izquierdo: Autónomos Teóricos (Púrpura)
         f'<rect x="{izq}" y="{arr}" width="{w_util/2}" height="{h_util/2}" fill="#faf5ff" opacity="0.8"/>',
         f'<text x="{izq + 8}" y="{arr + 16}" text-anchor="start" font-size="10.5" font-weight="700" fill="#6b21a8">AUTÓNOMOS (Teoría alta)</text>',
         # Cuadrante Inferior Derecho: Esfuerzo con Dificultad (Ámbar)
         f'<rect x="{mid_x}" y="{mid_y}" width="{w_util/2}" height="{h_util/2}" fill="#fffbeb" opacity="0.8"/>',
         f'<text x="{ancho - der - 8}" y="{alto - aba - 8}" text-anchor="end" font-size="10.5" font-weight="700" fill="#92400e">PARTICIPATIVOS CON REZAGO</text>',
         # Cuadrante Inferior Izquierdo: Riesgo Crítico (Rojo)
         f'<rect x="{izq}" y="{mid_y}" width="{w_util/2}" height="{h_util/2}" fill="#fef2f2" opacity="0.8"/>',
         f'<text x="{izq + 8}" y="{alto - aba - 8}" text-anchor="start" font-size="10.5" font-weight="700" fill="#991b1b">EN RIESGO CRÍTICO</text>',
         # Ejes y líneas divisorias
         f'<line x1="{izq}" y1="{mid_y}" x2="{ancho - der}" y2="{mid_y}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4"/>',
         f'<line x1="{mid_x}" y1="{arr}" x2="{mid_x}" y2="{alto - aba}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4"/>',
         f'<rect x="{izq}" y="{arr}" width="{w_util}" height="{h_util}" fill="none" stroke="#94a3b8" stroke-width="1.2" rx="4"/>']

    for codigo, vx, vy in puntos:
        resaltado = codigo in destacados
        cx_pt = px(vx)
        cy_pt = py(vy)
        # Colores según cuadrante
        if vy >= 0.5 and vx >= 0.5:
            color_pt = "#059669"
        elif vy >= 0.5:
            color_pt = "#7c3aed"
        elif vx >= 0.5:
            color_pt = "#d97706"
        else:
            color_pt = "#dc2626"

        s.append(f'<circle cx="{cx_pt:.1f}" cy="{cy_pt:.1f}" r="{7 if resaltado else 5.8}" '
                 f'fill="{color_pt}" stroke="#ffffff" stroke-width="1.5" opacity="0.9">'
                 f'<title>{escapar(codigo)}: Rendimiento={vy:.2f}, Esfuerzo={vx:.2f}</title></circle>')
        s.append(f'<text x="{cx_pt:.1f}" y="{cy_pt - 8:.1f}" text-anchor="middle" '
                 f'font-size="9" font-family="monospace" font-weight="700" fill="#1e293b">{escapar(codigo)}</text>')

    s.append(f'<text x="{(ancho + izq) / 2:.0f}" y="{alto - 10}" text-anchor="middle" class="g-eje">{escapar(etiqueta_x)}</text>')
    s.append(f'<text x="16" y="{alto / 2:.0f}" text-anchor="middle" class="g-eje" '
             f'transform="rotate(-90 16 {alto / 2:.0f})">{escapar(etiqueta_y)}</text>')
    s.append("</svg>")
    return Bloque("".join(s), ancho, alto, "grafico")


def dispersion(puntos, ancho=560, alto=300, etiqueta_x="", etiqueta_y="",
               color="#003366", destacados=()):
    """Cada punto es un estudiante con etiqueta interactiva."""
    if not puntos:
        return Bloque("", 0, 0, "grafico")
    xs = [p[1] for p in puntos]
    ys = [p[2] for p in puntos]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    if x1 - x0 <= 0:
        x1 = x0 + 1
    if y1 - y0 <= 0:
        y1 = y0 + 1
    izq, aba, arr, der = 55, 42, 20, 18

    def px(v):
        return izq + (v - x0) / (x1 - x0) * (ancho - izq - der)

    def py(v):
        return alto - aba - (v - y0) / (y1 - y0) * (alto - aba - arr)

    s = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%" '
         f'style="max-width:{ancho}px" role="img" aria-label="dispersion de '
         f'{escapar(etiqueta_x)} contra {escapar(etiqueta_y)}, '
         f'{len(puntos)} estudiantes">',
         f'<line x1="{izq}" y1="{alto - aba}" x2="{ancho - der}" y2="{alto - aba}" '
         f'stroke="#cbd5e1" stroke-width="1.5"/>',
         f'<line x1="{izq}" y1="{arr}" x2="{izq}" y2="{alto - aba}" '
         f'stroke="#cbd5e1" stroke-width="1.5"/>']
    for fr in (0.0, 0.5, 1.0):
        vy = y0 + (y1 - y0) * fr
        s.append(f'<line x1="{izq}" y1="{py(vy):.1f}" x2="{ancho - der}" '
                 f'y2="{py(vy):.1f}" stroke="#f1f5f9" stroke-width="1"/>'
                 f'<text x="{izq - 8}" y="{py(vy) + 4:.1f}" text-anchor="end" '
                 f'class="g-tick">{vy:.2f}</text>')
    for codigo, vx, vy in puntos:
        resaltado = codigo in destacados
        s.append(f'<circle cx="{px(vx):.1f}" cy="{py(vy):.1f}" '
                 f'r="{7 if resaltado else 5.5}" '
                 f'fill="{"#dc2626" if resaltado else color}" '
                 f'opacity="{1 if resaltado else 0.8}" stroke="#fff" '
                 f'stroke-width="1.5"><title>{escapar(codigo)}: X={vx:.2f}, Y={vy:.2f}</title></circle>')
    s.append(f'<text x="{(ancho + izq) / 2:.0f}" y="{alto - 10}" '
             f'text-anchor="middle" class="g-eje">{escapar(etiqueta_x)}</text>')
    s.append(f'<text x="16" y="{alto / 2:.0f}" text-anchor="middle" class="g-eje" '
             f'transform="rotate(-90 16 {alto / 2:.0f})">{escapar(etiqueta_y)}</text>')
    s.append("</svg>")
    return Bloque("".join(s), ancho, alto, "grafico")


def barra_de_alcance(afectados, total, ancho=520, color="#e05a3a"):
    """La barra que traduce «afecta a 5» en «afecta a 5 de 25, uno de cada cinco».
    Sin ella, dos hallazgos con alcances muy distintos se leen igual de graves."""
    total = total or 1
    fraccion = min(1.0, float(afectados) / total)
    alto = 96
    unidad = "estudiante" if afectados == 1 else "estudiantes"
    s = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%" '
         f'style="max-width:{ancho}px" role="img" '
         f'aria-label="afecta a {afectados} de {total} estudiantes">',
         f'<text x="0" y="24" class="g-alcance">{afectados}</text>',
         f'<text x="{34 + 14 * len(str(afectados))}" y="24" class="g-eti">'
         f'de {total} {unidad} · {fraccion:.0%} del curso</text>',
         f'<rect x="0" y="46" width="{ancho}" height="36" rx="18" fill="#eef1f6"/>',
         f'<rect x="0" y="46" width="{max(10, int(ancho * fraccion))}" height="36" '
         f'rx="18" fill="{color}"/>', "</svg>"]
    return Bloque("".join(s), ancho, alto, "grafico")


def semaforo(valor, umbral, ancho=200):
    """Un punto de color con su cifra. Ocupa poco y se lee desde el fondo del aula."""
    color = "#e05a3a" if valor >= umbral else "#1fa98a"
    alto = 60
    s = [f'<svg viewBox="0 0 {ancho} {alto}" width="100%" '
         f'style="max-width:{ancho}px" role="img" aria-label="{valor} casos">',
         f'<circle cx="26" cy="30" r="16" fill="{color}"/>',
         f'<text x="54" y="38" class="g-semaforo">{valor}</text>', "</svg>"]
    return Bloque("".join(s), ancho, alto, "grafico")


# ------------------------------------------------- piezas que ocupan pantalla
def titulo_seccion(texto):
    """Un encabezado de seccion. Ocupa pantalla y es texto: se cuenta como tal."""
    return Bloque(f'<h2 class="sec">{escapar(texto)}</h2>', 1180, 68, "texto")


def caja(titulo, bloque):
    """Enmarca un grafico en una tarjeta blanca con su titulo.

    El marco se cuenta como parte del grafico: existe para que el grafico se lea,
    no para llevar texto propio.
    """
    if not bloque.html:
        return Bloque("", 0, 0, "grafico")
    encabezado = f'<h3>{escapar(titulo)}</h3>' if titulo else ""
    html = f'<div class="caja">{encabezado}{bloque.html}</div>'
    return Bloque(html, bloque.ancho, bloque.alto + (61 if titulo else 42), "grafico")


def fila_de_cajas(pares):
    """Dos cajas lado a lado. Su altura es la de la mas alta, no la suma."""
    visibles = [(t, b) for t, b in pares if b.html]
    if not visibles:
        return Bloque("", 0, 0, "grafico")
    cajas = [caja(t, b) for t, b in visibles]
    html = '<div class="rejilla">' + "".join(c.html for c in cajas) + '</div>'
    return Bloque(html, 1180, max(c.alto for c in cajas) + 20, "grafico")
