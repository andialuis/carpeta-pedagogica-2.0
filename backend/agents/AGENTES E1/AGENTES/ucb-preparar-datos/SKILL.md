---
name: ucb-preparar-datos
description: >
  Etapa 1 (Preparar) del ciclo de analitica del aprendizaje de la UCB. Consolida
  una carpeta desordenada de una materia — planillas de notas, listas de
  asistencia, registros del aula virtual, fotos de calificaciones, silabos — en un
  unico BASE_INTEGRADA.xlsx con hojas de auditoria, sin alterar ni un solo valor.
  Usalo cuando el docente pida ordenar, preparar, consolidar o integrar los
  archivos de una materia, o cuando mencione la Etapa 1 / PREPARAR.
---

# Etapa 1 — Preparar datos del aula (UCB)

El programa que hace el trabajo **ya existe y esta probado**: `scripts/organizar.py`.
Tu papel es conversar con el docente, obtener su aprobacion y ejecutarlo.

> **No escribas codigo de procesamiento de datos.** No generes un script nuevo, no
> reimplementes estos pasos en pandas y no leas los `.xlsx` tu mismo para "ayudar".
> El programa es la fuente de verdad: garantiza que dos computadoras distintas
> produzcan exactamente la misma base. Si algo falla, lee `referencias/diagnostico.md`.

## Antes de empezar

**Ubica la habilidad.** Esta carpeta puede estar en cualquier lugar del espacio de
trabajo. Localizala una sola vez y usa esa ruta en todos los comandos:

```bash
find . -name organizar.py -path "*ucb-preparar-datos*"
```

En Windows (PowerShell): `Get-ChildItem -Recurse -Filter organizar.py`

En adelante, `<SKILL>` es la carpeta que contiene este archivo. La ruta habitual es
`AGENTES/ucb-preparar-datos`.

**Comprueba el entorno.** Unica dependencia: openpyxl.

```bash
python3 -c "import openpyxl; print(openpyxl.__version__)"
```

Si falla, el comando es `pip install openpyxl`. No continues sin el.

> En Windows usa `python` en lugar de `python3` en todos los comandos de este
> archivo. Si `python3` no existe, esa es la causa.

---

## Paso 1 — Encuadre (PAUSA)

Saluda al docente y preguntale exactamente esto:

1. ¿Cual es el nombre exacto de la carpeta que deseas organizar? (Ej: `MATERIA SIS-12026`)
2. ¿Sabes si dentro hay algun documento que indique la ponderacion o el valor en
   puntos de cada evaluacion? Si no lo sabes, no importa: lo buscare.

**Detente y espera la respuesta.** No escanees nada todavia.

---

## Paso 2 — Inventario y aprobacion (PAUSA)

Lista los archivos de la carpeta (`ls`) y muestra una tabla con **todos**, sin omitir ninguno:

| Archivo | Tipo | Que contiene | ¿Clave para el analisis? | Por que |

- **CLAVE** = aporta datos de estudiantes: planillas de notas y asistencia,
  registros del aula virtual, fotos de listas de calificaciones, documentos que
  declaren ponderaciones.
- **NO CLAVE** = material de clase: presentaciones de contenido, lecturas, guias,
  plantillas.

Cierra preguntando: **"¿Apruebas esta lista? ¿Agrego o quito alguno?"**

**Detente y espera la aprobacion explicita.** Aun no toques los datos.

Cuando el docente apruebe, escribe la lista aprobada en un JSON (solo nombres de
archivo, sin rutas):

```bash
echo '["registro_matricula_oficial.xlsx","notas_parciales.xlsx","asistencia_lunes.csv"]' > aprobados.json
```

---

## Paso 3 — Ejecutar

Un solo comando. `--raiz` es la carpeta que **contiene** a la de la materia:

```bash
python3 <SKILL>/scripts/organizar.py "NOMBRE_CARPETA" --raiz "." --aprobados aprobados.json
```

El programa funciona desde cualquier directorio: encuentra su propia configuracion.

Si el docente aprueba todo sin cambios, puedes omitir `--aprobados`.

El programa crea `NOMBRE_CARPETA-REV/` con `bases_de_datos/BASE_INTEGRADA.xlsx`,
`INFORME_PREPARACION.md` y `manifiesto.json`. Los originales quedan intactos.

---

## Paso 3b — Transcribir imagenes y PDF (solo si hay)

**El programa no lee imagenes ni PDF. Esa parte te toca a ti**, porque tu si puedes
verlos.

Si el resumen reporta `imagen_pendiente_de_transcripcion` o
`pdf_pendiente_de_transcripcion`, el programa dejo una plantilla vacia. Para cada
archivo aprobado, primero decide **que trae**:

### Si trae CALIFICACIONES

1. **Abre el archivo y leelo con tu propia vision.**
2. Escribe lo que leas en un archivo con este nombre exacto, en
   `NOMBRE_CARPETA-REV/bases_de_datos/`:

   `<nombre_del_archivo_sin_extension>_transcripcion_asistida.xlsx`

   Con estas columnas: la identidad del estudiante (`identidad_en_imagen` o
   `identidad_en_pdf`, como diga la plantilla), el nombre del dato (por ejemplo
   `Nota (sobre 100)`), `archivo_origen`, `confianza`.
3. En `confianza` pon `alta`, `media` o `baja` **por fila**. Lo que no puedas leer
   con seguridad va como celda vacia con `confianza: baja` — **nunca lo adivines.**
4. **Muestrale al docente lo que transcribiste y pidele que lo confirme** antes de
   seguir. Es un dato que nadie mas verifico.
5. Vuelve a ejecutar el comando del Paso 3. El programa detecta el archivo
   `_transcripcion_asistida.xlsx`, lo integra a la base y borra la plantilla.

### Si trae NORMATIVA (ponderaciones, escalas, criterios)

Un silabo o un acta en PDF suele traer reglas, no calificaciones. En ese caso **no
llenes la plantilla**: copia el texto tal cual a un archivo de texto plano, en la
misma carpeta `bases_de_datos/`:

`<nombre_del_archivo_sin_extension>_transcripcion_asistida.txt`

Transcribe las reglas **tal como estan**, una por linea (`Primer Parcial 50 puntos`).
No las interpretes ni las conviertas. Al volver a ejecutar, el programa las lee y
las suma a `REGLAS_EVALUACION` con su archivo de origen.

Si el archivo trae **las dos cosas**, puedes generar ambos: la planilla `.xlsx` con
las calificaciones y el `.txt` con la normativa.

> Por que asi: si el programa dependiera de una libreria de OCR o de lectura de PDF,
> la base saldria distinta segun lo que cada computadora tenga instalado, y eso rompe
> R5. Tu transcripcion queda en un archivo permanente y auditable, con su nivel de
> confianza y la revision del docente. El programa sigue siendo identico en todas las
> maquinas.

---

## Paso 4 — Reportar

El programa imprime un RESUMEN DE CONTROL. **Transcribeselo al docente sin
adornarlo** y llama su atencion sobre:

- **Filas**: lista oficial vs. BASE_INTEGRADA. Si no coinciden, explica por que
  (lo dice la hoja INCIDENCIAS).
- **Metodos de reconocimiento**: `parecido` y `resuelto_por_eliminacion` son
  conjeturas — pidele que las revise.
- **Cobertura**: `ausente` y `no_reconocido` son casos que necesitan su ojo.
- **Incidencias**: nombralas una por una. Ninguna es decorativa.
- **Reglas de evaluacion**: los conflictos de escala se reportan, **no se resuelven**.
- **Huella de contenido**: el codigo que permite comparar resultados entre computadoras.

Termina con **una linea** diciendole que le toca hacer a el (revisar tal hoja,
transcribir tal imagen, convertir tal archivo).

### Adelantate a la confusion de las columnas repetidas

La hoja `BASE` tiene **una sola fila por estudiante**, pero **varias columnas con
nombres o correos**: una por cada archivo de origen. Al docente esto lo desconcierta
y cree que la base esta mal. No lo esta. Explicaselo asi, sin que te lo pregunte:

> "Ves varias columnas con nombres porque cada archivo escribia al estudiante a su
> manera, y R6 obliga a conservar el original de cada uno para que puedas auditar
> como se hizo cada cruce. La columna que manda es la de la lista oficial, al
> principio. Las demas son el comprobante de donde salio cada dato: la hoja
> DICCIONARIO marca cada una con `papel: identifica al estudiante`, y en Excel
> puedes ocultarlas sin borrarlas."

Si te pide eliminarlas, **no lo hagas**: violaria R6. El programa ya las deja
**plegadas** en Excel (se abren con el signo `+`), asi que por defecto solo se ve
el nombre de la lista oficial.

### Demuestra R3 antes de cerrar

R3 exige probar que no quedo ningun dato personal escrito dentro del codigo. Corre
esto con un apellido real del curso y ensenale el resultado vacio:

```bash
grep -ril "APELLIDO_DE_UN_ESTUDIANTE" <SKILL>/scripts/
```

En Windows: `Select-String -Path <SKILL>\scripts\*.py -Pattern "APELLIDO"`

No debe devolver nada. Si devuelve algo, hay un dato personal incrustado en el
codigo: reportalo al docente de inmediato y no continues.

---

## Lo que esta prohibido en esta etapa

R1 es la regla de oro: **esta etapa solo prepara, no limpia.** No corrijas
ortografia, no rellenes vacios con cero, no conviertas escalas, no promedies, no
separes a quien abandono, no anonimices. Todo eso es de la Etapa 2 y hacerlo aqui
borra la evidencia que esa etapa necesita.

*Ante la duda: si la accion transforma un valor, no es de esta etapa; si lo
describe o lo conserva, si.*

Las seis restricciones completas estan en `referencias/reglas-etapa1.md`.
Leelo si el docente te pide algo y no estas seguro de si corresponde aqui.

---

## Referencias (leelas solo cuando las necesites)

| Archivo | Cuando abrirlo |
|---|---|
| `referencias/formato-salida.md` | El docente pregunta que significa una hoja o columna del resultado |
| `referencias/reglas-etapa1.md` | Dudas sobre si una accion pertenece a esta etapa |
| `referencias/diagnostico.md` | El programa fallo, o un resultado se ve raro |
| `GUIA-USO.md` | El docente pregunta como funciona el skill o como usarlo |
