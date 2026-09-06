"""Crea una BASE_INTEGRADA de mentira, con la misma forma que la de la Etapa 1.

Sirve para comprobar que la habilidad funciona en esta computadora sin usar ni un
dato real de estudiantes. Trae a proposito los casos que la Etapa 2 tiene que saber
resolver: identidad repetida, una escala convertible y otra en conflicto, vacios de
los dos tipos, asistencia en texto y alguien que dejo de participar.

Uso:
    python3 crear_base_de_prueba.py [carpeta_destino]
"""

import sys
from pathlib import Path

import openpyxl

RAIZ = (Path(sys.argv[1]) if len(sys.argv) > 1
        else Path(__file__).resolve().parent / "materia_de_prueba")
CARPETA = RAIZ / "CURSO-PRUEBA-REV" / "bases_de_datos"
CARPETA.mkdir(parents=True, exist_ok=True)

ALUMNOS = [
    ("PR-01", "ALVAREZ SOTO, Ana",      "ana.alvarez@u.edu",   78, 8.2, "activo"),
    ("PR-02", "BENITEZ LARA, Bruno",    "bruno.benitez@u.edu", 65, 6.9, "activo"),
    ("PR-03", "CARDENAS RUIZ, Carla",   "carla.cardenas@u.edu", 91, 9.4, "activo"),
    ("PR-04", "DIAZ MORA, Diego",       "diego.diaz@u.edu",    54, 5.1, "activo"),
    ("PR-05", "ESPINOZA VACA, Elena",   "elena.espinoza@u.edu", 83, 8.8, "activo"),
    ("PR-06", "FLORES PINTO, Fabio",    "fabio.flores@u.edu",  72, 7.3, "activo"),
    ("PR-07", "GOMEZ SILVA, Gabriela",  "gabriela.gomez@u.edu", 88, 9.1, "activo"),
    ("PR-08", "HERRERA LUNA, Hugo",     "hugo.herrera@u.edu",  61, 6.2, "activo"),
    ("PR-09", "IBARRA NOVOA, Irene",    "irene.ibarra@u.edu",  None, None, "abandono"),
    ("PR-10", "JUAREZ PEREZ, Javier",   "javier.juarez@u.edu", 45, 4.7, "activo"),
]

FECHAS = ["2026-03-10", "2026-03-17", "2026-03-24", "2026-04-07", "2026-04-14"]

libro = openpyxl.Workbook()

# ------------------------------------------------------------------ BASE
hoja = libro.active
hoja.title = "BASE"
columnas = (["Codigo", "Apellidos y Nombres", "Correo institucional"]
            + ["[notas · Parcial] Estudiante", "[notas · Parcial] Examen s/100",
               "[notas · Parcial] Practico s/10"]
            + [f"[asistencia] Asistencia {f}" for f in FECHAS]
            + ["[aula virtual] Ultimo acceso"])
hoja.append(columnas)

for codigo, nombre, correo, examen, practico, estado in ALUMNOS:
    asistencias = []
    for indice, _ in enumerate(FECHAS):
        if estado == "abandono" and indice >= 2:
            asistencias.append("A")          # deja de venir a mitad de curso
        else:
            asistencias.append("P" if indice != 3 else "T")
    ultimo = "2026-03-18" if estado == "abandono" else "2026-04-15"
    hoja.append([codigo, nombre, correo, nombre, examen, practico]
                + asistencias + [ultimo])

# Una celda de nota vacia para alguien que si figura en el archivo
hoja.cell(row=3, column=6, value=None)

# -------------------------------------------------------- DICCIONARIO
hoja = libro.create_sheet("DICCIONARIO")
hoja.append(["columna_en_base", "archivo", "hoja", "columna_original",
             "escala_detectada", "papel"])
for columna in columnas:
    if columna.startswith("[notas"):
        archivo, resto = "notas.xlsx", "Parcial"
    elif columna.startswith("[asistencia"):
        archivo, resto = "asistencia.csv", "asistencia"
    elif columna.startswith("[aula"):
        archivo, resto = "aula virtual.csv", "aula virtual"
    else:
        archivo, resto = "matricula.xlsx", "Matricula"
    papel = ("identifica al estudiante"
             if columna.endswith("Estudiante") else "dato")
    hoja.append([columna, archivo, resto, columna, "", papel])

# ---------------------------------------------------------- COBERTURA
hoja = libro.create_sheet("COBERTURA")
hoja.append(["id_estudiante", "estudiante", "archivo", "situacion", "detalle"])
for codigo, nombre, _, examen, _, estado in ALUMNOS:
    for etiqueta in ("notas · Parcial", "asistencia", "aula virtual"):
        if estado == "abandono" and etiqueta != "asistencia":
            situacion = "ausente"
        elif codigo == "PR-02" and etiqueta == "notas · Parcial":
            situacion = "encontrado_vacio"
        else:
            situacion = "encontrado"
        hoja.append([codigo, nombre, etiqueta, situacion, ""])

# ----------------------------------------------------- EMPAREJAMIENTOS
hoja = libro.create_sheet("EMPAREJAMIENTOS")
hoja.append(["archivo", "fila_origen", "valor_original", "id_estudiante",
             "estudiante", "metodo", "puntaje"])
for numero, (codigo, nombre, _, _, _, _) in enumerate(ALUMNOS, start=1):
    hoja.append(["notas · Parcial", numero, nombre, codigo, nombre, "codigo", 1.0])

# ---------------------------------------------------------- INCIDENCIAS
hoja = libro.create_sheet("INCIDENCIAS")
hoja.append(["tipo", "archivo", "fila_origen", "valor_original", "detalle",
             "contenido_fila"])

# --------------------------------------------------- REGLAS_EVALUACION
hoja = libro.create_sheet("REGLAS_EVALUACION")
hoja.append(["instrumento", "valor_declarado", "unidad", "archivo", "linea",
             "texto_original", "columnas_relacionadas", "escala_en_planilla",
             "observacion"])
# Una regla limpia: se puede convertir
hoja.append(["Examen", 40, "puntos", "reglamento.txt", 4, "Examen 40 puntos",
             "[notas · Parcial] Examen s/100", "100", ""])
# Una regla en conflicto: NO se debe convertir, queda pendiente
hoja.append(["Practico", 20, "puntos", "reglamento.txt", 5, "Practico 20 puntos",
             "[notas · Parcial] Practico s/10", "10",
             "el documento declara 20 puntos y la planilla usa escala 10: "
             "revisar antes de convertir"])

destino = CARPETA / "BASE_INTEGRADA.xlsx"
libro.save(destino)
print(f"Base de prueba creada en: {destino}")
print(f"  {len(ALUMNOS)} estudiantes · {len(columnas)} columnas · 7 hojas")
print("\nProcesala con:")
print(f'  python3 {Path(__file__).resolve().parent.parent}/scripts/procesar.py '
      f'"CURSO-PRUEBA" --raiz "{RAIZ}" --proponer')
