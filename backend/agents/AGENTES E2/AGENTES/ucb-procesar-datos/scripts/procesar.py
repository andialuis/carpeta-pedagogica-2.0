"""procesamiento_datos_docente — ETAPA 2: PROCESAR

Punto de entrada unico. Toma el BASE_INTEGRADA.xlsx que dejo la Etapa 1 y lo
depura: protege la identidad, unifica escalas, detecta anomalias, interpreta los
vacios y separa a quienes abandonaron.

Esta etapa DEPURA, NO ANALIZA: no calcula la nota final, no promedia instrumentos
entre si, no busca correlaciones para sacar conclusiones ni arma perfiles. Todo eso
corresponde a la etapa siguiente.

Uso:
    python procesar.py NOMBRE_CARPETA [--raiz RUTA] [--proponer]
                                      [--criterios criterios.json]

    --proponer    muestra las cuatro tablas de la segunda pausa y no escribe nada
    --criterios   JSON con las decisiones del docente

El programa no contiene ningun dato de ninguna materia: las escalas se leen de la
hoja REGLAS_EVALUACION en cada ejecucion.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import paso_anonimizar
import paso_convertir_texto
import paso_detectar_anomalias
import paso_imputar_vacios
import paso_limpiar_tipos
import paso_reportar
import paso_separar_abandonos
import paso_verificar
from paso_leer_base import columna_clave, leer

VERSION_MINIMA = (3, 8)


def comprobar_entorno():
    print("CHEQUEO PREVIO")
    print(f"  Python           : {sys.version.split()[0]}")
    print(f"  Sistema          : {sys.platform}")
    if sys.version_info < VERSION_MINIMA:
        minima = ".".join(str(n) for n in VERSION_MINIMA)
        print(f"\nEste programa necesita Python {minima} o superior.")
        print("Instala una version mas nueva desde https://www.python.org/downloads/")
        sys.exit(1)
    faltan = []
    try:
        import openpyxl
        print(f"  openpyxl         : {openpyxl.__version__}")
    except ImportError:
        print("  openpyxl         : NO INSTALADO")
        faltan.append("openpyxl")
    try:
        import docx  # noqa: F401
        print("  python-docx      : instalado")
    except ImportError:
        print("  python-docx      : NO INSTALADO")
        faltan.append("python-docx")
    if faltan:
        print("\nFaltan dependencias obligatorias. Instalalas con:")
        print(f"    pip install {' '.join(faltan)}")
        sys.exit(1)


def cargar_config(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def cargar_criterios(ruta):
    """Las decisiones del docente. Sin archivo, se aprueba todo tal cual."""
    vacio = {"escalas_omitidas": [], "abandonos_excluidos": [], "abandonos_forzados": []}
    if not ruta:
        return vacio
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    vacio.update({k: list(datos.get(k, [])) for k in vacio})
    return vacio


def _huella_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def _localizar_entrada(raiz, carpeta, nombre_archivo):
    """Encuentra el BASE_INTEGRADA dentro de la carpeta -REV."""
    rev = Path(raiz) / f"{carpeta}-REV"
    if not rev.is_dir():
        rev = Path(raiz) / carpeta
    bases = rev / "bases_de_datos"
    if not bases.is_dir():
        return None, rev
    candidatos = sorted(bases.glob(f"{nombre_archivo}*.xlsx"))
    candidatos = [c for c in candidatos if not c.name.startswith("~$")]
    return (candidatos[0] if candidatos else None), rev


# ------------------------------------------------------------------ propuesta
def construir_propuestas(datos, config, columnas, filas, clave):
    identidad, indices_identidad = paso_anonimizar.proponer(
        columnas, filas, datos["columnas_marcadas_identidad"], clave)
    escalas, pendientes = paso_limpiar_tipos.proponer_escalas(
        columnas, filas, datos["reglas_evaluacion"])
    anomalias = paso_detectar_anomalias.revisar(columnas, filas, clave, config)
    abandonos = paso_separar_abandonos.proponer(
        columnas, filas, clave, datos["cobertura"], config)
    diagnostico = paso_separar_abandonos.diagnosticar(
        columnas, filas, datos["cobertura"], config)
    return {
        "diagnostico_abandonos": diagnostico,
        "identidad": identidad, "indices_identidad": indices_identidad,
        "escalas": escalas, "escalas_pendientes": pendientes,
        "anomalias": anomalias, "abandonos": abandonos,
    }


def _imprimir_diagnostico(d):
    """Que señales se pudieron medir en esta base. Se imprime siempre."""
    print("\nD.1 · CON QUE SEÑALES SE PUDO TRABAJAR")
    print("-" * 38)
    for s in d["señales"]:
        marca = s["disponible"]
        print(f"  [{marca}] {s['señal']:32} {s['detalle']}")
    if not d["fiable"]:
        print(f"\n  AVISO: solo {d['disponibles']} de 4 señales se pueden medir y "
              f"hacen falta {d['minimo']}.")
        print("  La separacion de abandonos NO es fiable en esta base. Si la lista D")
        print("  sale vacia, no significa que nadie haya abandonado: significa que")
        print("  no hay con que comprobarlo. Revise esos casos usted.")


def imprimir_propuestas(p):
    def tabla(titulo, filas, campos, anchos):
        print(f"\n{titulo}")
        print("-" * len(titulo))
        if not filas:
            print("  (ninguna)")
            return
        cabecera = "  " + "".join(f"{c[:a-1]:<{a}}" for c, a in zip(campos, anchos))
        print(cabecera)
        print("  " + "-" * (sum(anchos) - 1))
        for r in filas:
            print("  " + "".join(f"{str(r.get(c, ''))[:a-1]:<{a}}"
                                 for c, a in zip(campos, anchos)))

    print("\n" + "=" * 78)
    print(" CRITERIOS PROPUESTOS — nada se ha transformado todavia")
    print("=" * 78)

    tabla("A · IDENTIDAD que se reemplazara por un codigo",
          p["identidad"], ["columna", "tipo", "ejemplo", "motivo"], [40, 9, 24, 44])
    tabla("B · ESCALAS que se unificaran",
          p["escalas"], ["instrumento", "columna", "escala_origen",
                         "escala_destino", "factor", "de_donde_sale"],
          [22, 34, 15, 16, 10, 30])
    if p["escalas_pendientes"]:
        tabla("B.1 · ESCALAS QUE NO SE CONVIERTEN (quedan pendientes)",
              p["escalas_pendientes"], ["instrumento", "columnas", "motivo"],
              [22, 36, 56])
    tabla("C · VALORES SOSPECHOSOS (no se corrigen)",
          p["anomalias"], ["estudiante", "columna", "valor", "motivo"],
          [14, 40, 10, 40])
    tabla("D · ESTUDIANTES que se moverian a ABANDONOS",
          p["abandonos"], ["codigo", "desde", "senales", "motivo"],
          [12, 13, 10, 78])
    _imprimir_diagnostico(p["diagnostico_abandonos"])

    print("\n" + "=" * 78)
    print(" Si apruebas todo, ejecuta de nuevo sin --proponer.")
    print(" Para vetar algo, crea criterios.json con:")
    print('   {"escalas_omitidas": [], "abandonos_excluidos": [], '
          '"abandonos_forzados": []}')
    print("=" * 78 + "\n")


# ------------------------------------------------------------------ ejecucion
def ejecutar(carpeta, raiz, ruta_config, nombre_archivo, solo_proponer,
             ruta_criterios):
    config = cargar_config(ruta_config)
    criterios = cargar_criterios(ruta_criterios)

    entrada, rev = _localizar_entrada(raiz, carpeta, nombre_archivo)
    if entrada is None:
        print(f"ERROR: no se encontro '{nombre_archivo}*.xlsx' dentro de "
              f"'{rev / 'bases_de_datos'}'.")
        print("Esta etapa necesita el resultado de la Etapa 1. Corre primero "
              "'ucb-preparar-datos'.")
        sys.exit(1)

    print(f"\nPROCESANDO: {entrada.name}")
    print(f"Carpeta de trabajo: {rev.name}\n")
    huella_entrada = _huella_archivo(entrada)

    datos = leer(entrada, config)
    columnas = list(datos["base_columnas"])
    filas = [list(f) for f in datos["base_filas"]]
    clave = columna_clave(columnas, filas)
    total_entrada = len(filas)

    print(f"1. Base leida: {total_entrada} fila(s) y {len(columnas)} columna(s).")
    if datos["faltantes"]:
        print(f"   AVISO: la base no trae {', '.join(datos['faltantes'])}. "
              f"Se continua sin esa informacion.")

    propuestas = construir_propuestas(datos, config, columnas, filas, clave)

    if solo_proponer:
        imprimir_propuestas(propuestas)
        return {"modo": "propuesta"}

    cambios = []

    # --- 1. Fotografia inicial ------------------------------------------------
    antes = paso_verificar.fotografiar(columnas, filas, clave, config)
    print(f"2. Fotografia inicial: {len(antes['resumenes'])} columna(s) numericas, "
          f"{len(antes['relaciones'])} relacion(es) relevantes.")

    # --- 2. Anonimizar --------------------------------------------------------
    filas, equivalencia, cambios_id = paso_anonimizar.aplicar(
        columnas, filas, propuestas["indices_identidad"], clave)
    cambios.extend(cambios_id)
    print(f"3. Identidad protegida: {len(propuestas['indices_identidad'])} "
          f"columna(s) reemplazadas por el codigo.")

    # --- 3. Tipos y escalas ---------------------------------------------------
    filas, cambios_tipos = paso_limpiar_tipos.normalizar_valores(
        columnas, filas, config)
    cambios.extend(cambios_tipos)

    columnas, filas, cambios_escalas, aplicadas, omitidas, creadas_escala = \
        paso_limpiar_tipos.aplicar(columnas, filas, propuestas["escalas"],
                                    criterios["escalas_omitidas"])
    derivadas = set(creadas_escala)
    cambios.extend(cambios_escalas)
    clave = columna_clave(columnas, filas)
    # Una escala que ya coincide con la normativa no se convierte: multiplicar
    # por 1 solo dejaria una columna gemela. Se cuenta aparte para que "0
    # conversiones" no se lea como si algo hubiera fallado.
    sin_efecto = sum(1 for c in cambios_escalas if c["factor"] == 1)
    print(f"4. Escalas unificadas: {len(aplicadas)} conversion(es) aplicadas, "
          f"{sin_efecto} que ya estaban en la escala correcta, "
          f"{len(omitidas) + len(propuestas['escalas_pendientes'])} pendiente(s).")

    # --- 4. Anomalias (se recalculan sobre la base ya tipada) -----------------
    anomalias = paso_detectar_anomalias.revisar(columnas, filas, clave, config,
                                                derivadas)
    print(f"5. Anomalias detectadas: {len(anomalias)} (ninguna corregida).")

    # --- 5. Vacios ------------------------------------------------------------
    vacios, cambios_vacios = paso_imputar_vacios.revisar(
        columnas, filas, clave, datos["cobertura"], datos["origen_de_columna"],
        config, derivadas)
    cambios.extend(cambios_vacios)
    total_vacios = sum(v["vacios"] for v in vacios)
    print(f"6. Vacios: {total_vacios} celda(s) en {len(vacios)} columna(s).")

    # --- 6. Texto a numero ----------------------------------------------------
    columnas, filas, cambios_texto, notas_texto, creadas_texto = \
        paso_convertir_texto.convertir(columnas, filas, config)
    # Las columnas [1/0] nacen aqui, despues de los dos escaneos, asi que ningun
    # paso anterior puede confundirlas con datos originales.
    derivadas |= creadas_texto
    cambios.extend(cambios_texto)
    clave = columna_clave(columnas, filas)
    print(f"7. Asistencia a numero: {len(cambios_texto)} columna(s) convertidas.")

    # --- 7. Separar abandonos -------------------------------------------------
    propuesta_abandonos = paso_separar_abandonos.proponer(
        columnas, filas, clave, datos["cobertura"], config)
    activos, abandonos, decisiones = paso_separar_abandonos.aplicar(
        filas, clave, propuesta_abandonos,
        criterios["abandonos_excluidos"], criterios["abandonos_forzados"])
    print(f"8. Separacion: {len(activos)} activo(s) y {len(abandonos)} abandono(s).")

    # Una nota baja o dos accesos son cifras raras para un estudiante que curso, y
    # perfectamente normales para uno que dejo de venir. Marcarlo evita que el
    # docente persiga un error de datos donde solo hay un abandono.
    codigos_abandono = {str(f[clave]).strip() for f in abandonos}
    for a in anomalias:
        if a["estudiante"] in codigos_abandono:
            a["accion"] = ("ninguna: esta etapa no corrige. OJO: este estudiante "
                           "quedo en ABANDONOS, asi que el valor raro puede ser "
                           "consecuencia de haber dejado el curso")

    diagnostico = paso_separar_abandonos.diagnosticar(
        columnas, filas, datos["cobertura"], config)
    _imprimir_diagnostico(diagnostico)

    # --- 8. Comprobacion final ------------------------------------------------
    # Se mide sobre el MISMO conjunto que la fotografia inicial: activos y
    # abandonos juntos. Comparar solo contra los que quedaron daria una falsa
    # alarma provocada por haber separado a los que se fueron.
    despues = paso_verificar.fotografiar(columnas, activos + abandonos, clave, config)
    verificacion, alertas = paso_verificar.comparar(antes, despues, config)
    print(f"9. Verificacion: {alertas} relacion(es) que cambiaron y hay que mirar.")

    # --- 9. Escribir ----------------------------------------------------------
    bases = entrada.parent
    plegar = {p["columna"] for p in propuestas["identidad"]}
    salida = bases / "BASE_DATOS_DEPURADA.xlsx"
    paso_reportar.escribir_base_depurada(
        salida, columnas, activos, abandonos, decisiones, cambios, anomalias,
        vacios, verificacion, datos["reglas_evaluacion"], plegar)

    ruta_equivalencia = bases / "EQUIVALENCIA_CODIGOS.xlsx"
    paso_reportar.escribir_equivalencia(
        ruta_equivalencia,
        paso_anonimizar.columnas_de_equivalencia(equivalencia), equivalencia)

    codigo_huella = paso_reportar.huella(columnas, activos, clave)
    intacta = _huella_archivo(entrada) == huella_entrada

    resumen = _resumen(total_entrada, activos, abandonos, datos, columnas,
                       vacios, anomalias, aplicadas, omitidas,
                       propuestas["escalas_pendientes"], verificacion, alertas,
                       codigo_huella, intacta, notas_texto, salida,
                       ruta_equivalencia, diagnostico, sin_efecto)

    carpeta_informe = rev / "RESULTADOS" / "ETAPA 2 - PROCESAR"
    carpeta_informe.mkdir(parents=True, exist_ok=True)
    ruta_informe = carpeta_informe / "INFORME_PROCESAMIENTO.docx"
    paso_reportar.escribir_informe(
        ruta_informe, carpeta, resumen,
        _secciones(cambios, anomalias, vacios, decisiones, verificacion,
                   aplicadas, propuestas["escalas_pendientes"], notas_texto,
                   diagnostico, sin_efecto))

    _imprimir_resumen(resumen)
    return {"salida": salida, "huella": codigo_huella}


def _resumen(total, activos, abandonos, datos, columnas, vacios, anomalias,
             aplicadas, omitidas, pendientes, verificacion, alertas, huella,
             intacta, notas_texto, salida, equivalencia, diagnostico,
             sin_efecto):
    cuadra = len(activos) + len(abandonos) == total
    por_tipo = {
        "figura pero sin dato": sum(v["figura_pero_sin_dato"] for v in vacios),
        "no figura en el archivo": sum(v["no_figura_en_el_archivo"] for v in vacios),
        "sin clasificar": sum(v["sin_clasificar"] for v in vacios),
    }
    return [
        ("Filas de entrada", total),
        ("Activos", len(activos)),
        ("Abandonos", len(abandonos)),
        ("La cuenta cierra", "SI" if cuadra else "NO — REVISAR"),
        ("Columnas antes", len(datos["base_columnas"])),
        ("Columnas despues", len(columnas)),
        ("Vacios en total", sum(v["vacios"] for v in vacios)),
        ("  · figura pero sin dato", por_tipo["figura pero sin dato"]),
        ("  · no figura en el archivo", por_tipo["no figura en el archivo"]),
        ("  · sin clasificar", por_tipo["sin clasificar"]),
        ("Anomalias detectadas", len(anomalias)),
        ("Conversiones de escala aplicadas", len(aplicadas)),
        ("Escalas que ya estaban correctas", sin_efecto),
        ("Escalas pendientes", len(omitidas) + len(pendientes)),
        ("Relaciones que hay que mirar", alertas),
        ("Señales de abandono disponibles", f"{diagnostico['disponibles']} de 4"
         + ("" if diagnostico["fiable"] else "  — NO ALCANZAN: revisar a mano")),
        ("Avisos de conversion de texto", len(notas_texto)),
        ("Archivo de entrada sin modificar", "SI" if intacta else "NO — REVISAR"),
        ("Huella de la hoja ACTIVOS", huella),
        ("Base depurada", str(salida)),
        ("Tabla de equivalencia", str(equivalencia)),
    ]


def _secciones(cambios, anomalias, vacios, decisiones, verificacion, aplicadas,
               pendientes, notas_texto, diagnostico, sin_efecto):
    return [
        ("0. Con que señales se pudo trabajar",
         "Si alguna señal no se pudo medir, la separacion de abandonos es menos "
         "fiable y conviene revisar esos casos a mano."
         + ("" if diagnostico["fiable"] else
            "  AVISO: no se alcanzo el minimo de señales necesarias."),
         ["señal", "disponible", "detalle"], diagnostico["señales"]),
        ("1. Que se le hizo a cada columna",
         "Toda transformacion conserva la columna original al lado de la nueva.",
         ["columna", "paso", "que_se_hizo", "factor", "por_que"], cambios),
        ("2. Escalas unificadas",
         "Las ponderaciones salen unicamente de la hoja REGLAS_EVALUACION que "
         "entrego la etapa anterior."
         + (f"  {sin_efecto} columna(s) no necesitaron conversion: la planilla "
            "ya usaba el mismo puntaje que declara la normativa."
            if sin_efecto else ""),
         ["instrumento", "columna", "escala_origen", "escala_destino", "factor",
          "de_donde_sale"], aplicadas),
        ("3. Escalas que quedaron pendientes",
         "No se convirtieron porque la regla llegaba con un conflicto sin "
         "resolver. Requieren una decision del docente.",
         ["instrumento", "columnas", "motivo"], pendientes),
        ("4. Valores sospechosos",
         "Detectados y reportados. Esta etapa no corrige ninguno.",
         ["estudiante", "columna", "valor", "motivo", "detalle"], anomalias),
        ("5. Celdas vacias",
         "Una casilla de nota vacia se deja vacia: un cero significaria que el "
         "estudiante rindio y no obtuvo puntaje.",
         ["columna", "tipo_de_columna", "vacios", "figura_pero_sin_dato",
          "no_figura_en_el_archivo", "que_se_hizo"], vacios),
        ("6. Conversion de asistencia a numero",
         "Avisos que conviene confirmar con el docente.",
         ["columna", "aviso"], notas_texto),
        ("7. Estudiantes separados",
         "Nadie fue borrado: quienes dejaron de participar quedan en la hoja "
         "ABANDONOS con el motivo de la clasificacion.",
         ["codigo", "motivo", "desde", "ultimo_acceso", "senales",
          "quien_decidio"], decisiones),
        ("8. Comprobacion final",
         "Las relaciones entre columnas antes y despues de depurar, medidas "
         "sobre el mismo conjunto de estudiantes.",
         ["columna_a", "columna_b", "relacion_antes", "relacion_despues",
          "veredicto", "detalle"], verificacion),
    ]


def _imprimir_resumen(resumen):
    print("\n" + "=" * 70)
    print(" RESUMEN DE CONTROL")
    print("=" * 70)
    for titulo, contenido in resumen:
        print(f"  {titulo:36} {contenido}")
    print("=" * 70 + "\n")


def main():
    analizador = argparse.ArgumentParser(
        description="Etapa 2 — PROCESAR: depura la base integrada de una materia.")
    analizador.add_argument("carpeta", nargs="?",
                            help="nombre de la carpeta de la materia")
    analizador.add_argument("--raiz", default=".",
                            help="carpeta que contiene a la de la materia")
    analizador.add_argument("--archivo", default="BASE_INTEGRADA",
                            help="nombre del archivo a procesar")
    analizador.add_argument("--config",
                            default=str(Path(__file__).resolve().parent / "config.json"))
    analizador.add_argument("--proponer", action="store_true",
                            help="muestra los criterios y no transforma nada")
    analizador.add_argument("--criterios",
                            help="JSON con las decisiones del docente")
    argumentos = analizador.parse_args()

    comprobar_entorno()
    carpeta = argumentos.carpeta or input(
        "Nombre exacto de la carpeta de la materia: ").strip()
    ejecutar(carpeta, argumentos.raiz, argumentos.config, argumentos.archivo,
             argumentos.proponer, argumentos.criterios)


if __name__ == "__main__":
    main()
