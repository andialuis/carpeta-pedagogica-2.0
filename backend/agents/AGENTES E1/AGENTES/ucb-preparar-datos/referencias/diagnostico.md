# Diagnostico — que hacer cuando algo falla

## El programa se detiene

| Mensaje | Causa | Solucion |
|---|---|---|
| `openpyxl : NO INSTALADO` | Falta la unica dependencia | `pip install openpyxl` |
| `ERROR: no existe la carpeta '...'` | Nombre o `--raiz` equivocados | `--raiz` es la carpeta que **contiene** a la de la materia, no la materia misma. Si el nombre tiene espacios, va entre comillas. |
| `ERROR: no se pudo identificar la lista oficial` | Ninguna planilla parece una nomina | Renombra la lista de matricula para que incluya `registro`, `matricula`, `oficial` o `nomina`; o agrega el termino a `patrones_lista_oficial` en `config.json`. |

## El resultado se ve raro

**Faltan estudiantes en BASE.** BASE tiene exactamente una fila por estudiante de
la lista oficial. Si sobran o faltan, el problema esta en que se eligio la lista
oficial equivocada: revisalo en el resumen, linea `Lista oficial`.

**Una columna se llama `columna_sin_titulo_D`.** Esa columna no tenia encabezado
en el origen. Es correcto conservarla: R6 prohibe descartarla.

**Un archivo aparece como `formato_aprobado_que_no_se_puede_abrir`.** Formatos
como `.xls`, `.ods`, `.doc` o `.rtf` se organizan pero no se leen. (Los `.pdf` ya
no caen aqui: van al circuito de transcripcion, igual que las imagenes.)
Conviertelos a `.xlsx` o `.csv` y vuelve a ejecutar. **No es un fallo silencioso:
el programa lo reporta en INCIDENCIAS.**

**Muchas filas `fila_no_reconocida`.** Casi siempre significa que en esa planilla
se eligio mal la columna de identidad. Revisa la hoja `EMPAREJAMIENTOS`: si el
`valor_original` no es un nombre, ese es el problema. Los umbrales estan en
`config.json` (`umbral_similitud`, `margen_minimo_similitud`).

**Un encabezado quedo partido o pegado.** El programa prueba hasta
`max_filas_encabezado` (3 por defecto) y elige el corte que deja las columnas mas
homogeneas. Si tu planilla tiene 4 filas de encabezado, subele ese valor en
`config.json`.

**Una foto de notas no se leyo.** Es lo esperado y es por diseño: **el programa no
lee imagenes**, porque un OCR por libreria opcional haria que la base saliera
distinta en cada computadora (rompe R5). Quien transcribe es el agente, que si
puede ver.

El programa deja `*_PENDIENTE_TRANSCRIPCION.xlsx`. Rellenalo (el agente puede
hacerlo leyendo la imagen; marca la confianza por fila y confirma con el docente),
renombralo a `<nombre_imagen>_transcripcion_asistida.xlsx`, dejalo en
`bases_de_datos/` y vuelve a ejecutar: se integra solo y la plantilla se borra.

**Veo varias columnas con nombres de alumnos y me marea.** Es correcto: R6 obliga a
conservar la columna de identidad de cada archivo de origen para poder auditar los
cruces. La hoja `BASE` sigue teniendo **una sola fila por estudiante**. La hoja
`DICCIONARIO` marca esas columnas con `papel: identifica al estudiante`. Ocultalas
en Excel si molestan; no las borres.

## Windows

Usa `python` en lugar de `python3`, y barras invertidas en las rutas:

```bash
python AGENTES\ucb-preparar-datos\scripts\organizar.py "NOMBRE_CARPETA" --raiz "."
```

Si `python` tampoco existe, Python no esta en el PATH: reinstalalo marcando
"Add Python to PATH".

## Probar sin datos reales

```bash
python3 AGENTES/instalar.py
```

El instalador crea una materia inventada, la procesa, comprueba el resultado y
borra la prueba. Tambien puedes generarla y quedartela:

```bash
python3 AGENTES/ucb-preparar-datos/ejemplos/crear_materia_de_prueba.py
```

Crea una materia sintetica con encabezados combinados, nombres invertidos,
abreviados, una fila huerfana y 1.200 registros de aula virtual. Sirve para
verificar la instalacion sin exponer datos de estudiantes reales.

## Volver a ejecutar

Es seguro. Para partir limpio, borra la carpeta `-REV` desde el explorador de
archivos, o por terminal:

```bash
rm -rf "NOMBRE_CARPETA-REV"
```

En Windows (PowerShell): `Remove-Item -Recurse -Force "NOMBRE_CARPETA-REV"`
