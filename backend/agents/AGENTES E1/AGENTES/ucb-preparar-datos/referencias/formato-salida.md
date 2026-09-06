# Formato de salida — contrato con la Etapa 2

La Etapa 2 (Procesar) lee estos archivos. Los nombres de hojas, columnas y
etiquetas son un **contrato**: si cambian, la Etapa 2 deja de funcionar.

## Que se genera

```
NOMBRE_CARPETA-REV/
├── bases_de_datos/
│   ├── BASE_INTEGRADA.xlsx              ← la entrega principal
│   ├── registros_logs.csv               ← los originales, copiados sin tocar
│   └── *_PENDIENTE_TRANSCRIPCION.xlsx   ← plantillas de imagenes no leidas
├── presentaciones/  imagenes/  documentos/
├── INFORME_PREPARACION.md               ← el resumen de control, en texto
└── manifiesto.json                      ← huellas SHA-256 de cada archivo de entrada
```

## Las 6 hojas de BASE_INTEGRADA.xlsx

| Hoja | Contenido |
|---|---|
| `BASE` | Una fila por estudiante de la lista oficial. Las columnas de la lista oficial van primero con su nombre original; las demas se prefijan con `[archivo]` o `[archivo · hoja]`. |
| `DICCIONARIO` | De donde salio cada columna: `columna_en_base`, `archivo`, `hoja`, `columna_original`, `escala_detectada`, `papel`. |
| `COBERTURA` | Un registro por estudiante y por archivo. Ver las cuatro situaciones abajo. |
| `EMPAREJAMIENTOS` | Como se reconocio a cada estudiante en cada fila de origen, con metodo y puntaje. Es la hoja para auditar los reconocimientos dudosos. |
| `INCIDENCIAS` | Todo lo que no encajo, con la fila de origen completa. |
| `REGLAS_EVALUACION` | Ponderaciones halladas en los documentos, la columna con la que se relacionan y los conflictos de escala detectados. |

## Las cuatro situaciones de COBERTURA

La Etapa 2 necesita distinguirlas; **no son sinonimos**:

| Etiqueta | Significa |
|---|---|
| `encontrado` | El estudiante figura en ese archivo y tiene cifras. |
| `encontrado_vacio` | Figura, pero todas sus columnas de valor estan vacias. No rindio ≠ no figura. |
| `ausente` | No aparece en ese archivo. |
| `no_reconocido` | Hay una fila en el origen que podria ser suya pero quedo ambigua. |

## Metodos de reconocimiento (hoja EMPAREJAMIENTOS)

De mas seguro a mas dudoso:

`codigo` → `correo` → `nombre_exacto` → `nombre_con_inicial` → `parecido` →
`resuelto_por_eliminacion`

Los dos ultimos son **conjeturas** y siempre deben mostrarse al docente para su
revision.

## Tipos de incidencia

`ambiguedad_resuelta_por_eliminacion`, `archivo_no_aprobado`,
`archivo_tratado_como_registro_de_actividad`, `codigo_repetido_en_lista_oficial`,
`colision_dos_filas_al_mismo_estudiante`, `datos_rescatados_de_documento`,
`extension_desconocida`, `formato_aprobado_que_no_se_puede_abrir`,
`identidad_del_registro_no_reconocida`,
`imagen_pendiente_de_transcripcion`, `imagen_transcrita`,
`pdf_pendiente_de_transcripcion`, `pdf_transcrito`, `normativa_transcrita`,
`planilla_vacia`,
`registro_sin_columna_de_fecha`, `fila_no_reconocida`, `fila_ambigua_sin_resolver`,
`fila_apartada_sin_datos`

## Columnas del resumen del aula virtual

Si hay un archivo de registros (miles de filas, pocas identidades), se resume asi:

`Total de registros`, `Primer registro`, `Ultimo registro`,
`Dias distintos con actividad`, `Franja horaria mas frecuente`, y una columna
`Veces: X` por cada tipo de accion. El archivo original queda entero en
`bases_de_datos/`.

## Huella de contenido

SHA-256 (16 caracteres) sobre los **valores** de `BASE`, ordenados por codigo de
estudiante. No incluye los nombres de columna. Dos computadoras con los mismos
archivos de entrada deben producir la misma huella.

## Imagenes y PDF: quien transcribe

El programa **no lee imagenes ni PDF**. Genera
`<archivo>_PENDIENTE_TRANSCRIPCION.xlsx` y sigue. El **agente** lo lee, y segun lo
que traiga guarda una de estas dos cosas en `bases_de_datos/`:

- **calificaciones** -> `<archivo>_transcripcion_asistida.xlsx`, que se integra a la
  base como una fuente mas;
- **normativa** (ponderaciones, escalas) -> `<archivo>_transcripcion_asistida.txt`,
  de donde se leen las reglas hacia `REGLAS_EVALUACION`.

Al volver a ejecutar, el programa las recoge y borra la plantilla.

Columnas de ese archivo: `identidad_en_imagen`, el nombre del dato, `archivo_origen`,
`confianza` (`alta`/`media`/`baja` por fila), `origen`.

Es deliberado: un OCR por libreria opcional haria que la base saliera distinta en
cada computadora, lo que rompe R5. Asi la transcripcion queda auditable y el
programa sigue siendo identico en todas las maquinas.
