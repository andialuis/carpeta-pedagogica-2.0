"""Crea un RESULTADOS_ANALISIS inventado, como el que entrega la Etapa 3.

Sirve para que `instalar_4.py` pruebe la habilidad entera sin tocar un solo dato
real. Los numeros son deterministas: la misma semilla da siempre el mismo curso.

    python3 crear_resultados_de_prueba.py /ruta/donde/crearlo
"""

import random
import sys
from pathlib import Path

import openpyxl

SEMILLA = 11
ESTUDIANTES = 21


def _hoja(libro, titulo, columnas, filas):
    hoja = libro.create_sheet(titulo)
    hoja.append(columnas)
    for fila in filas:
        hoja.append(list(fila))


def crear(destino):
    azar = random.Random(SEMILLA)
    bases = Path(destino) / "CURSO-PRUEBA-REV" / "bases_de_datos"
    bases.mkdir(parents=True, exist_ok=True)

    perfiles = [
        ("En la media del curso", 9, 0.49, 0.57),
        ("Se esfuerza y aun asi no le sale", 4, 0.22, 0.81),
        ("Rinde bien casi sin aparecer", 3, 0.84, 0.41),
        ("Poca presencia y bajo resultado", 2, 0.31, 0.35),
        ("Sin datos suficientes", 2, None, None),
        ("Constante y con buen resultado", 1, 0.66, 0.70),
    ]

    libro = openpyxl.Workbook()
    libro.remove(libro.active)

    _hoja(libro, "HALLAZGOS",
          ["hallazgo", "cifra", "estudiantes_afectados", "si_no_hago_nada",
           "en_que_se_apoya", "prioridad", "grafico"],
          [["El curso perdio estudiantes por el camino",
            "2 de 21 estudiantes (9.5%) dejaron de participar", 2,
            "la perdida no aparecera en ningun indicador", "hoja ABANDONOS",
            "urgente", ""],
           ["Hay estudiantes que se esfuerzan y no les alcanza",
            "4 estudiantes con participacion alta y resultado bajo", 4,
            "se desmotivan y terminan abandonando", "perfiles", "alta", "perfiles"],
           ["Asistencia y nota se mueven juntas",
            "relacion fuerte (+0.58); cuando una sube, la otra tambien", 19,
            "se seguira decidiendo sobre una sin mirar la otra", "cruce",
            "alta", "relacion"],
           ["Un grupo rinde mejor sin vigilancia",
            "brecha de 0.31 a 0.44 puntos en escala 0-1", 3,
            "la evaluacion pierde validez para todo el curso",
            "codigos: EST-03, EST-08, EST-14", "alta", "instrumentos"]])

    _hoja(libro, "HIPOTESIS",
          ["hipotesis", "origen", "veredicto", "cifra", "estudiantes", "p",
           "efecto", "sobrevive_al_ajuste", "detalle"],
          [["los que faltan sacan peor nota", "docente", "no se sostiene",
            "0.512 contra 0.478 (diferencia +0.034)", 19, 0.61, 0.12, "no",
            "puede ser casualidad; con este numero de estudiantes no alcanza"],
           ["los del turno noche participan menos", "el programa", "se sostiene",
            "0.34 contra 0.61 (diferencia -0.27)", 19, 0.008, 0.94, "si",
            "dificilmente sea casualidad"]])

    _hoja(libro, "PERFILES",
          ["perfil", "estudiantes", "codigos", "rendimiento_medio",
           "esfuerzo_medio", "abandonos_en_el_perfil", "que_significa"],
          [[n, c, "", r, e, 0, "grupo detectado por el analisis"]
           for n, c, r, e in perfiles])

    _hoja(libro, "RELACIONES",
          ["columna_a", "columna_b", "relacion", "fuerza", "sentido",
           "estudiantes", "p", "sobrevive_al_ajuste", "tipo", "lectura"],
          [["asistencia del semestre", "rendimiento general", 0.58, "fuerte",
            "cuando una sube, la otra tambien", 19, 0.004, "si",
            "entre variables distintas", "dificilmente sea casualidad"]])

    _hoja(libro, "INDICADORES",
          ["que_medir", "se_enciende_cuando", "por_que_ese_valor", "que_hacer",
           "estudiantes_hoy"],
          [["rendimiento acumulado (escala 0 a 1)", "cae por debajo de 0.30",
            "es el cuarto inferior de este curso",
            "contacto directo antes de la siguiente evaluacion", 5],
           ["proporcion de clases a las que asiste", "baja de 0.70",
            "por debajo de ese punto deja de ser irregular",
            "preguntar antes de que pase otra semana", 4]])

    _hoja(libro, "ACCIONES",
          ["prioridad", "para_quien", "cuantos", "codigos", "que_hacer",
           "en_que_hallazgo_se_apoya", "como_sabre_si_funciono"],
          [["urgente", "estudiantes que ya dejaron de participar", 2, "",
            "verificar uno por uno si el retiro es formal",
            "El curso perdio estudiantes por el camino",
            "que cada caso tenga una situacion definida antes del cierre"],
           ["alta", "Se esfuerza y aun asi no le sale", 4, "EST-05, EST-07",
            "sesion de repaso sobre los temas donde perdieron mas puntos",
            "Hay estudiantes que se esfuerzan y no les alcanza",
            "que su rendimiento suba en la siguiente evaluacion"],
           ["baja", "Constante y con buen resultado", 1, "EST-11",
            "NO necesita intervencion. Sostener lo que ya funciona.",
            "clasificacion por perfiles",
            "que el grupo siga del mismo tamano al cierre"]])

    prioridades = []
    for i in range(1, ESTUDIANTES + 1):
        codigo = f"EST-{i:02d}"
        abandono = i in (7, 16)
        prioridades.append([
            i, codigo, round(azar.uniform(0.2, 1.5), 4),
            "abandono" if abandono else "activo",
            perfiles[i % len(perfiles)][0], 3,
            "figura como abandono" if abandono else "rendimiento por debajo de la mitad"])
    prioridades.sort(key=lambda f: -f[2])
    for puesto, fila in enumerate(prioridades, start=1):
        fila[0] = puesto
    _hoja(libro, "PRIORIDADES",
          ["puesto", "codigo", "urgencia", "situacion", "perfil",
           "senales_disponibles", "motivo"], prioridades)

    graficos = []
    for i in range(1, ESTUDIANTES + 1):
        codigo = f"EST-{i:02d}"
        graficos.append(["relacion", codigo, round(azar.uniform(0.1, 0.95), 3),
                         "asistencia del semestre"])
        graficos.append(["relacion", codigo, round(azar.uniform(0.1, 0.95), 3),
                         "rendimiento general"])
    _hoja(libro, "DATOS_GRAFICOS", ["grafico", "etiqueta", "valor", "serie"],
          graficos)

    _hoja(libro, "NO_SE_PUDO", ["analisis", "por_que"],
          [["linea de tiempo del aula virtual",
            "no se encontro el registro del aula virtual"]])

    libro.save(bases / "RESULTADOS_ANALISIS.xlsx")
    return bases


if __name__ == "__main__":
    print(crear(sys.argv[1] if len(sys.argv) > 1 else "."))
