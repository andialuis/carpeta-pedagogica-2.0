# Formato de salida — contrato con la Etapa 3

La Etapa 3 (Analizar) lee estos archivos. Los nombres de hojas y columnas son un
**contrato**: si cambian, la etapa siguiente deja de funcionar.

## Que se genera

```
NOMBRE_CARPETA-REV/
├── bases_de_datos/
│   ├── BASE_INTEGRADA.xlsx          ← la entrada, intacta
│   ├── BASE_DATOS_DEPURADA.xlsx     ← la entrega principal
│   └── EQUIVALENCIA_CODIGOS.xlsx    ← el unico archivo con nombres
└── RESULTADOS/
    └── ETAPA 2 - PROCESAR/
        └── INFORME_PROCESAMIENTO.docx
```

## Las 7 hojas de BASE_DATOS_DEPURADA.xlsx

| Hoja | Contenido |
|---|---|
| `ACTIVOS` | Los estudiantes que siguieron el curso, con los datos ya depurados |
| `ABANDONOS` | Quienes dejaron de participar, con el motivo, la fecha y quien decidio |
| `CAMBIOS` | Columna por columna: que se hizo, con que factor y por que |
| `ANOMALIAS` | Los valores sospechosos, **sin corregir** |
| `VACIOS` | Cuantos vacios por columna y de que tipo es cada uno |
| `VERIFICACION` | Las relaciones antes y despues, y cuales cambiaron |
| `REGLAS_EVALUACION` | Las ponderaciones que venian de la Etapa 1, tal cual |

## Las columnas convertidas

Toda conversion **conserva la columna original al lado** de la nueva:

| Original | Convertida | Que paso |
|---|---|---|
| `Examen Teoria s/100` | `Examen Teoria s/100 [sobre 6]` | escala unificada |
| `Asistencia 2026-05-04` | `Asistencia 2026-05-04 [1/0]` | texto a numero |

El sufijo entre corchetes es la marca de que esa columna la produjo esta etapa.
La hoja `CAMBIOS` dice de donde salio el factor.

## Los tres tipos de vacio

La hoja `VACIOS` los separa porque **no significan lo mismo**:

| Tipo | Significa |
|---|---|
| `figura_pero_sin_dato` | El estudiante esta en el archivo con la celda en blanco. Suele ser un *no rindio*. |
| `no_figura_en_el_archivo` | El estudiante no aparece en ese archivo. Suele ser un *no estaba*. |
| `sin_clasificar` | No se pudo determinar cual de los dos. |

La distincion viene de la hoja `COBERTURA` que produjo la Etapa 1.

## Ninguna casilla de nota se rellena

Un cero significa que el estudiante rindio y no obtuvo puntaje; un vacio significa
que no hay dato. **Las columnas numericas vacias se quedan vacias.** Solo en las
columnas de texto se escribe `Sin registro`.

## Huella de la hoja ACTIVOS

SHA-256 (16 caracteres) sobre los valores de `ACTIVOS`, ordenados por el codigo del
estudiante. Dos computadoras con la misma entrada y los mismos criterios deben
producir la misma huella.
