"""Crea una BASE_DATOS_DEPURADA inventada, como la que entrega la Etapa 2.

Sirve para que `instalar_3.py` pruebe la habilidad entera sin tocar ni un dato
real. Los numeros son deterministas: la misma semilla da siempre el mismo curso,
asi que la prueba vale como comprobacion y no como sorteo.

    python3 crear_base_de_prueba.py /ruta/donde/crearla
"""

import csv
import datetime as _dt
import random
import sys
from pathlib import Path

import openpyxl

SEMILLA = 7
ESTUDIANTES = 24


def _hoja(libro, titulo, columnas, filas):
    hoja = libro.create_sheet(titulo)
    hoja.append(columnas)
    for fila in filas:
        hoja.append(list(fila))
    return hoja


def crear(destino):
    azar = random.Random(SEMILLA)
    destino = Path(destino)
    bases = destino / "CURSO-PRUEBA-REV" / "bases_de_datos"
    bases.mkdir(parents=True, exist_ok=True)

    fechas = [_dt.date(2026, 3, 2) + _dt.timedelta(days=7 * s) for s in range(10)]
    columnas = (["codigo", "Apellidos y Nombres", "Modalidad", "Turno",
                 "Sede"]
                + [f"[asistencia] Asistencia {f.isoformat()}" for f in fechas]
                + ["[planilla] Primer Parcial s/30",
                   "[planilla] Segundo Parcial s/30",
                   "[planilla] Laboratorio s/15",
                   "[tareas] Tareas en linea s/15",
                   "[tareas] Proyecto en casa s/10",
                   "[moodle] Total de registros",
                   "[moodle] Dias distintos con actividad",
                   "[moodle] Tiempo empleado en el cuestionario (minutos)",
                   "[moodle] Hora de inicio del cuestionario",
                   "[planilla] Gestion"])

    modalidades = ["Presencial", "Virtual"]
    turnos = ["Manana", "Noche"]
    sedes = ["Central", "Central", "Norte"]

    activos, abandonos = [], []
    inicio_prueba = _dt.datetime(2026, 5, 18, 19, 0, 0)

    for numero in range(1, ESTUDIANTES + 1):
        codigo = f"EST-{numero:02d}"
        modalidad = modalidades[numero % 2]
        turno = turnos[numero % 2]
        sede = sedes[numero % 3]

        # Dos estudiantes dejan de venir a mitad de semestre.
        abandona = numero in (7, 19)
        corte = 4 if numero == 7 else 6

        base = azar.uniform(0.35, 0.95)
        if modalidad == "Virtual":
            base -= 0.10           # diferencia deliberada, para tener que hallar

        asistencia = []
        for indice in range(len(fechas)):
            if abandona and indice >= corte:
                asistencia.append(0)
            else:
                asistencia.append(1 if azar.random() < base + 0.05 else 0)

        def nota(maximo, ruido=0.12):
            valor = max(0.0, min(1.0, base + azar.uniform(-ruido, ruido)))
            return round(valor * maximo, 1)

        parcial1 = nota(30)
        parcial2 = None if abandona else nota(30)
        laboratorio = None if abandona else nota(15)
        # Un grupo rinde mucho mejor en lo que hace sin vigilancia.
        empuje = 0.30 if numero in (3, 11, 16) else 0.0
        tareas = round(min(1.0, base + empuje) * 15, 1)
        proyecto = None if abandona else round(min(1.0, base + empuje) * 10, 1)

        registros = 2 if abandona else azar.randint(12, 60)
        dias = 2 if abandona else azar.randint(6, 24)
        minutos = 6 if numero in (3, 11) else azar.randint(28, 55)
        # Tres estudiantes empiezan el cuestionario casi al mismo segundo.
        if numero in (3, 11, 16):
            hora = inicio_prueba + _dt.timedelta(seconds=(numero % 3) * 20)
        else:
            hora = inicio_prueba + _dt.timedelta(minutes=azar.randint(2, 240))

        fila = ([codigo, codigo, modalidad, turno, sede] + asistencia
                + [parcial1, parcial2, laboratorio, tareas, proyecto,
                   registros, dias, minutos, hora, "2-2026"])
        (abandonos if abandona else activos).append(fila)

    libro = openpyxl.Workbook()
    libro.remove(libro.active)
    _hoja(libro, "ACTIVOS", columnas, activos)
    _hoja(libro, "ABANDONOS", ["codigo", "motivo", "desde", "senales",
                               "quien_decidio"],
          [[f[0], "dejo de asistir y de registrar evaluaciones", "2026-04-13", 2,
            "el programa, aprobado por el docente"] for f in abandonos])
    _hoja(libro, "CAMBIOS", ["columna", "paso", "que_se_hizo", "factor",
                             "por_que"],
          [["Apellidos y Nombres", "anonimizar",
            "el contenido se reemplazo por el codigo del estudiante", "",
            "protege la identidad"]])
    _hoja(libro, "ANOMALIAS", ["estudiante", "columna", "valor", "motivo",
                               "detalle", "accion"],
          [["EST-05", "[planilla] Primer Parcial s/30", 31,
            "muy lejos del resto de su columna", "supera el maximo declarado",
            "ninguna: esta etapa no corrige"]])
    _hoja(libro, "VACIOS", ["columna", "tipo_de_columna", "vacios",
                            "figura_pero_sin_dato", "no_figura_en_el_archivo",
                            "sin_clasificar", "que_se_hizo"],
          [["[planilla] Segundo Parcial s/30", "numerica", 2, 2, 0, 0,
            "se dejaron vacios"]])
    _hoja(libro, "VERIFICACION", ["columna_a", "columna_b", "relacion_antes",
                                  "relacion_despues", "veredicto", "detalle"],
          [["[planilla] Primer Parcial s/30", "[tareas] Tareas en linea s/15",
            0.51, 0.51, "estable", ""]])
    _hoja(libro, "REGLAS_EVALUACION",
          ["instrumento", "puntaje", "archivo_origen"],
          [["Primer Parcial", 30, "silabo.pdf"],
           ["Segundo Parcial", 30, "silabo.pdf"],
           ["Laboratorio", 15, "silabo.pdf"],
           ["Tareas en linea", 15, "silabo.pdf"],
           ["Proyecto en casa", 10, "silabo.pdf"]])
    libro.save(bases / "BASE_DATOS_DEPURADA.xlsx")

    # Registros del aula virtual, como los exporta la plataforma.
    ruta_log = bases / "moodle_log_completo.csv"
    with open(ruta_log, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["Hora", "Usuario", "Evento"])
        momento = _dt.datetime(2026, 3, 2, 8, 0, 0)
        for _ in range(900):
            salto = azar.choice([7, 19, 45, 90, 240, 700])
            momento += _dt.timedelta(minutes=salto)
            if momento > _dt.datetime(2026, 6, 20):
                break
            escritor.writerow([momento.strftime("%Y-%m-%d %H:%M:%S"),
                               f"EST-{azar.randint(1, ESTUDIANTES):02d}",
                               azar.choice(["Modulo visto", "Envio entregado",
                                            "Cuestionario iniciado"])])
    return bases


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "."
    print(crear(destino))
