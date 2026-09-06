"""Paso: construir_tab_intervencion

La tercera pestaña: que hacer el lunes.

Aqui no hay graficos, y es a proposito. Las dos pestañas anteriores existen para
convencer; esta existe para actuar, y una accion se lee, no se mira. Por eso esta
pestaña queda exenta de la regla del 60% grafico: medirla con la misma vara
obligaria a meterle adornos que estorbarian justo donde hay que leer con cuidado.

Cada tarjeta responde cuatro preguntas con esas mismas palabras: para quien, que
hacer, por que y como se sabra si funciono. La ultima es la que casi siempre falta,
y sin ella una accion no es una decision: es una intencion.

Las acciones las escribio la Etapa 3. Aqui se muestran; no se inventan ni se
retocan.
"""

from graficos import Bloque, escapar, texto_plano
from paso_leer_resultados import arreglar_plurales, entero, normalizar, plural

ORDEN = {"urgente": 0, "alta": 1, "media": 2, "baja": 3}


def _sin_intervencion(texto):
    plano = normalizar(texto)
    return "no necesita intervencion" in plano or plano.startswith("no necesita")


def construir(datos, config):
    bloques = []
    acciones = list(datos.get("ACCIONES", []))
    indicadores = datos.get("INDICADORES", [])
    colores = config["prioridades"]

    bloques.append(texto_plano(
        '<div class="intro">Esta pestaña no describe el curso: dice que hacer con '
        'el. Una tarjeta por grupo, de lo mas urgente a lo que no necesita nada, y '
        'cada una con la forma de comprobar dentro de un mes si funciono.</div>',
        1180, 250))
    partes = [bloques[0].html]

    acciones.sort(key=lambda a: (ORDEN.get(str(a.get("prioridad", "media")).strip().lower(), 9),
                                 -entero(a.get("cuantos"))))

    # Si todas las tarjetas dijeran lo mismo, el problema no es de esta etapa: es
    # que el analisis no entrego acciones de verdad. Se avisa en vez de disimularlo.
    textos = [normalizar(a.get("que_hacer", "")) for a in acciones]
    if len(textos) > 2 and len(set(textos)) == 1:
        aviso = texto_plano(
            '<div class="aviso"><b>Todas las acciones del analisis dicen lo '
            'mismo.</b> Eso significa que la etapa anterior no llego a distinguir '
            'grupos: conviene volver a ella antes de usar este plan.</div>',
            1180, 230)
        bloques.append(aviso)
        partes.append(aviso.html)

    if not acciones:
        vacio = texto_plano('<div class="vacio">El analisis no entrego acciones. '
                            'Vuelva a la Etapa 3 antes de usar este tablero para '
                            'decidir.</div>', 1180, 130)
        bloques.append(vacio)
        partes.append(vacio.html)

    for accion in acciones:
        prioridad = str(accion.get("prioridad", "media") or "media").strip().lower()
        color = colores.get(prioridad, colores["media"])
        que_hacer = str(accion.get("que_hacer", "") or "")
        cuantos = entero(accion.get("cuantos"))
        codigos = str(accion.get("codigos", "") or "")
        apoyo = str(accion.get("en_que_hallazgo_se_apoya", "") or "")
        medida = str(accion.get("como_sabre_si_funciono", "") or "")
        sin_nada = _sin_intervencion(que_hacer)

        etiqueta = "No requiere accion" if sin_nada else prioridad.capitalize()
        cuerpo = (
            f'<div class="tarjeta" style="border-left-color:{color}">'
            f'<span class="ver" style="background:{color}">{escapar(etiqueta)}</span>'
            f'<h4>{escapar(str(accion.get("para_quien", ""))[:160])}</h4>'
            f'<div class="campos">'
            f'<div class="campo"><b>Para quien</b>'
            f'{escapar(plural(cuantos, "estudiante"))}'
            + (f'<br><span class="cod" style="font-size:12.5px">{escapar(codigos[:180])}</span>'
               if codigos else "") + '</div>'
            f'<div class="campo"><b>Que hacer</b>{escapar(arreglar_plurales(que_hacer))}</div>'
            f'<div class="campo"><b>Por que</b>{escapar(arreglar_plurales(apoyo))}</div>'
            f'<div class="campo"><b>Como se si funciono</b>{escapar(arreglar_plurales(medida))}</div>'
            f'</div></div>')
        bloques.append(texto_plano(
            cuerpo, 1180,
            len(que_hacer) + len(apoyo) + len(medida) + len(codigos) + 120))
        partes.append(cuerpo)

    # --- Las alertas para el proximo semestre ----------------------------------
    if indicadores:
        partes.append('<h2 class="sec">Señales para vigilar el proximo semestre</h2>')
        filas = []
        caracteres = 0
        for ind in indicadores:
            hoy = entero(ind.get("estudiantes_hoy"))
            color = colores["urgente"] if hoy > 0 else colores["baja"]
            medir = str(ind.get("que_medir", "") or "")
            cuando = str(ind.get("se_enciende_cuando", "") or "")
            hacer = str(ind.get("que_hacer", "") or "")
            caracteres += len(medir) + len(cuando) + len(hacer)
            filas.append(
                f'<tr><td><b>{escapar(medir)}</b></td>'
                f'<td>{escapar(cuando)}</td>'
                f'<td>{escapar(hacer)}</td>'
                f'<td><span class="pill" style="background:{color}">{hoy}</span></td></tr>')
        tabla = ('<table class="tabla"><thead><tr><th>Que medir</th>'
                 '<th>Se enciende cuando</th><th>Que hacer</th>'
                 '<th>Hoy</th></tr></thead><tbody>'
                 + "".join(filas) + '</tbody></table>')
        bloques.append(texto_plano(tabla, 1180, caracteres, 14.5))
        partes.append(tabla)

    resumen = {
        "pestana": "3 · Plan de intervencion",
        "elementos": len(acciones) + len(indicadores),
        "detalle": (f"{plural(len(acciones), 'accion', 'acciones')} y "
                    f"{plural(len(indicadores), 'señal', 'señales')} de alerta"),
        "fuentes": "ACCIONES, INDICADORES",
    }
    return "".join(partes), bloques, resumen
