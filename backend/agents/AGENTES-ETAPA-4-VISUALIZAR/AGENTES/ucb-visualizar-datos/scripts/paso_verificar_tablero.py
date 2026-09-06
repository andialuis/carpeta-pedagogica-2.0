"""Paso: verificar_tablero

Las comprobaciones que se hacen ANTES de entregar el archivo.

Un tablero que se contradice con el informe delante de una reunion hace mas daño que
no tener tablero: a partir de ese momento nadie cree ninguno de los dos. Por eso
aqui no se confia en que todo salio bien, se comprueba una por una.

Y se mide algo que casi nunca se mide: el equilibrio entre grafico y texto. La
proporcion que hace que un tablero se entienda desde el fondo de la sala ronda el
60% de superficie grafica. No es un capricho estetico: por debajo de eso el publico
deja de mirar la pantalla y espera a que alguien lea en voz alta, que es
exactamente lo que el tablero venia a evitar.
"""

import re

from paso_leer_resultados import normalizar


def equilibrio(bloques):
    """Devuelve (proporcion_grafica, alto_grafico, alto_texto) de una pestaña.

    Se cuenta como grafico todo lo que comunica sin leerse: un grafico, una cifra
    grande, una barra y tambien una insignia de color, porque el color es la señal
    que se capta desde el fondo del aula. Se cuenta como texto lo que hay que leer
    palabra por palabra.
    """
    grafico = sum(b.area for b in bloques if b.clase == "grafico")
    texto = sum(b.area for b in bloques if b.clase == "texto")
    total = grafico + texto
    return (grafico / total if total else 0.0), grafico, texto


def revisar_equilibrio(por_pestana, config):
    """Comprueba el 60/40 en las pestañas que se miden, y explica cada resultado."""
    reglas = config["equilibrio"]
    objetivo, tolerancia = reglas["objetivo_grafico"], reglas["tolerancia"]
    filas, todas_bien = [], True
    for clave, bloques in por_pestana.items():
        proporcion, g, t = equilibrio(bloques)
        if clave == reglas["pestana_exenta"]:
            filas.append({
                "pestana": clave, "grafico": f"{proporcion:.0%}",
                "texto": f"{1 - proporcion:.0%}", "veredicto": "exenta",
                "por_que": reglas["por_que_exenta"]})
            continue
        dentro = abs(proporcion - objetivo) <= tolerancia
        todas_bien = todas_bien and dentro
        if dentro:
            por_que = "dentro del objetivo"
        elif proporcion < objetivo:
            por_que = ("demasiado texto: convierta alguna cifra en barra o en "
                       "tarjeta con numero grande")
        else:
            por_que = "demasiado grafico: puede haber adornos que no dicen nada"
        filas.append({"pestana": clave, "grafico": f"{proporcion:.0%}",
                      "texto": f"{1 - proporcion:.0%}",
                      "veredicto": "cumple" if dentro else "REVISAR",
                      "por_que": por_que})
    return filas, todas_bien


def revisar_archivo(html, datos, config, equivalencia_prohibida=()):
    """Las cuatro comprobaciones del formato, sobre el HTML ya armado."""
    controles = []

    # 1 · Nada de internet.
    externos = re.findall(r'(?:src|href)\s*=\s*["\'](https?:)?//', html)
    controles.append({
        "control": "no pide nada a internet",
        "resultado": "SI" if not externos else f"NO — {len(externos)} enlace(s) externo(s)",
        "bien": not externos})

    # 2 · Ningun nombre ni correo.
    correos = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html)
    nombres = [n for n in equivalencia_prohibida
               if n and len(str(n)) > 4 and normalizar(n) in normalizar(html)]
    controles.append({
        "control": "no aparece ningun nombre ni correo",
        "resultado": "SI" if not correos and not nombres else
                     f"NO — {len(correos)} correo(s), {len(nombres)} nombre(s)",
        "bien": not correos and not nombres})

    # 3 · Ninguna pestaña vacia por error.
    vacias = [i + 1 for i, p in enumerate(re.findall(
        r'<section class="panel"[^>]*>(.*?)</section>', html, re.S))
        if len(re.sub(r"<[^>]+>", "", p).strip()) < 120]
    controles.append({
        "control": "ninguna pestaña quedo vacia",
        "resultado": "SI" if not vacias else f"NO — pestaña(s) {vacias}",
        "bien": not vacias})

    # 4 · Las cifras del tablero coinciden con las del Excel.
    descuadres = _comparar_cifras(html, datos)
    controles.append({
        "control": "las cifras coinciden con el analisis",
        "resultado": "SI" if not descuadres else f"NO — {'; '.join(descuadres[:3])}",
        "bien": not descuadres})

    return controles


def _comparar_cifras(html, datos):
    """Comprueba los conteos que el tablero afirma contra las hojas del Excel.

    Se comparan los conteos y no cada numero suelto a proposito: si el tablero dice
    «8 hallazgos» y la hoja trae 7, ahi hay un error de construccion. Comparar cada
    decimal daria falsos positivos por el formato y nadie volveria a mirar esta
    comprobacion.
    """
    problemas = []
    sin_etiquetas = re.sub(r"<[^>]+>", " ", html)
    esperados = {
        "hallazgo": len({str(f.get("hallazgo", ""))[:70].lower()
                         for f in datos.get("HALLAZGOS", [])}),
        "accion": len(datos.get("ACCIONES", [])),
    }
    for palabra, esperado in esperados.items():
        encontrados = re.findall(rf"El analisis entrego (\d+) {palabra}", sin_etiquetas)
        for texto in encontrados:
            if int(texto) != esperado:
                problemas.append(f"{palabra}s: el tablero dice {texto} y el Excel "
                                 f"trae {esperado}")
    return problemas


def buscar_datos_en_el_codigo(carpeta_scripts, palabras):
    """R6: ni la metrica pedida ni ninguna cifra pueden quedar dentro del programa."""
    encontrados = []
    for ruta in sorted(carpeta_scripts.glob("*.py")):
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for palabra in palabras:
            if palabra and len(str(palabra)) > 4 and \
                    normalizar(palabra) in normalizar(texto):
                encontrados.append(f"{ruta.name}: «{palabra}»")
    return encontrados
