# Que hay en cada archivo que produce la Etapa 3

## RESULTADOS_ANALISIS.xlsx

Vive en `bases_de_datos/`, junto a la base depurada. **Es el archivo que consume la
Etapa 4**: trae todas las cifras ya calculadas para que la visualizacion no vuelva
a calcular nada. El Word y este Excel salen de la misma corrida y dicen lo mismo.

| Hoja | Que contiene |
|---|---|
| `HALLAZGOS` | Uno por fila, con su cifra, a cuantos afecta, que pasa si no se hace nada, en que se apoya y su prioridad |
| `HIPOTESIS` | Cada sospecha con su veredicto, el numero que lo respalda, sobre cuantos estudiantes y si sobrevive al ajuste |
| `PERFILES` | Cada grupo oculto con su nombre, cuantos estudiantes tiene, sus codigos y que significa |
| `RELACIONES` | Cada cruce con su fuerza, su sentido, su tamano de muestra y si sobrevive al ajuste |
| `INDICADORES` | Que medir, con que valor se enciende la alarma, por que ese valor y que hacer |
| `ACCIONES` | Prioridad, para quien, cuantos, que hacer, en que hallazgo se apoya y como sabra si funciono |
| `PRIORIDADES` | Todos los estudiantes por codigo, ordenados por urgencia, con el motivo de su posicion |
| `DATOS_GRAFICOS` | Los datos exactos detras de cada grafico del informe |
| `COLUMNAS` | Que papel le asigno el programa a cada columna y por que |
| `NO_SE_PUDO` | Los analisis que esta base no permite hacer, con su motivo |

Las dos ultimas no las pedia el formato, pero sin ellas no se puede auditar por que
el programa analizo unas columnas y otras no.

## Las cifras que mas se preguntan

**`rendimiento` (0 a 1).** No es la nota oficial de nadie. Es una variable de
analisis: cada instrumento se lleva a la escala 0-1 y se promedia, ponderando con
el puntaje que declara `REGLAS_EVALUACION` cuando existe. Sirve para poder comparar
un parcial sobre 100 con un laboratorio sobre 6. **Las casillas vacias no cuentan
como cero**: cada estudiante se promedia sobre los instrumentos que tiene, y se
anota cuantos le faltaban.

**`asistencia` (0 a 1).** La fraccion de clases registradas a las que asistio. Cada
columna se lleva a su propia escala antes de promediar, dividiendo por su maximo:
asi da lo mismo que la materia marque P/A/T, un puntaje sobre 5 o un porcentaje.

**`p`.** La probabilidad de que lo observado sea casualidad. Se calcula barajando
los datos muchas veces con una semilla fija, no con una formula que suponga mas
datos de los que tiene un curso de veinticinco.

**`sobrevive_al_ajuste`.** Al probar muchas parejas a la vez, algunas salen
"significativas" por azar: con doscientas comprobaciones al 5%, unas diez. Esta
columna dice cuales siguen en pie despues de corregirlo. **Las que dicen `no` son
pistas, no hallazgos.**

**`efecto`.** Cuanto se separan dos grupos, en desviaciones. Una diferencia puede
ser real y aun asi tan pequena que no valga la pena actuar sobre ella.

## INFORME_FINAL_ANALISIS.docx

En `RESULTADOS/ETAPA 3 - ANALIZAR/`. Cuatro apartados:

1. **Lo que descubrimos** — los hallazgos, cada uno en su bloque con sus tres datos
   en lineas separadas y su grafico al lado; el panorama del curso; los perfiles.
2. **Verificacion de sospechas** — que resulto cierto y que quedo descartado, mas
   las relaciones entre variables y los cruces apartados por triviales.
3. **Mis proximos pasos** — una accion por grupo y las senales de alerta.
4. **Conclusiones tecnicas** — si los datos alcanzaron, que no se pudo analizar y
   como leyo el programa cada columna.

## Los graficos

En `RESULTADOS/ETAPA 3 - ANALIZAR/graficos/`. Son **imagenes fijas de respaldo**:
cada una acompana al hallazgo que sustenta. El tablero interactivo es de la Etapa 4.

Los datos exactos de cada imagen estan en la hoja `DATOS_GRAFICOS`, para que se
puedan rehacer o auditar sin abrir el programa.
