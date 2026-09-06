# Las siete restricciones de la Etapa 2

## R1 — Esta etapa depura, no analiza

Prohibido: calcular la nota final, promediar instrumentos entre si, buscar
correlaciones para sacar conclusiones, armar perfiles de estudiantes, proponer
indicadores o decidir si un vacio vale cero para la nota.

**Ante la duda:** si el resultado es un dato mas limpio, es de esta etapa; si es una
conclusion sobre los estudiantes, no lo es.

*Por que importa:* la Etapa 3 analiza. Si aqui se decide que un vacio vale cero, ese
juicio entra al analisis disfrazado de dato y nadie vuelve a cuestionarlo.

*Como se cumple:* las unicas correlaciones que calcula el programa son las de la
hoja `VERIFICACION`, y solo sirven para comprobar que la limpieza no altero lo que
los datos decian. No se interpretan ni se reportan como hallazgo.

## R2 — No se toca la entrada

`BASE_INTEGRADA.xlsx` y todo lo que venga de la Etapa 1 quedan intactos.

*Como se cumple:* el programa calcula la huella SHA-256 del archivo de entrada al
empezar y la vuelve a calcular al terminar. El resumen informa
`Archivo de entrada sin modificar: SI`.

## R3 — No se pierde nadie ni nada

Activos + abandonos debe dar exactamente el total que entrego la etapa anterior.
Ninguna columna desaparece sin quedar registrada en `CAMBIOS`, y toda
transformacion conserva la columna original al lado.

*Como se cumple:* el resumen trae la linea `La cuenta cierra`. Si dice
`NO — REVISAR`, hay que detenerse.

## R4 — El programa no lleva datos adentro

Ni el nombre de la carpeta, ni nombres, ni notas, ni ponderaciones. Las escalas se
leen de `REGLAS_EVALUACION` en cada ejecucion.

*Como se comprueba:*

```bash
grep -ril "APELLIDO_DE_UN_ESTUDIANTE" scripts/
```

No debe devolver nada.

## R5 — Un solo punto de entrada

Un unico comando ejecuta todo el flujo: `procesar.py`. La logica esta repartida en
modulos `paso_*` —uno por paso— para poder mantenerla y reutilizarla, pero el
docente nunca corre mas de un comando.

## R6 — Que funcione en cualquier computadora

Dos dependencias: **openpyxl** para Excel y **python-docx** para el informe.
Ninguna libreria opcional puede cambiar el resultado. Si falta una obligatoria, el
programa se detiene y dice el comando exacto para instalarla.

## R7 — Si falta algo, lo dice

Si la base no trae alguna hoja de auditoria, o no existe el archivo de registros
del aula virtual, el programa **continua sin ella y lo avisa**. No inventa datos ni
columnas para rellenar el hueco.
