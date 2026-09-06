# Cuando algo falla o un resultado se ve raro

## El programa no arranca

**`No se encontro BASE_DATOS_DEPURADA*.xlsx`**
La Etapa 2 no termino, o la carpeta tiene otro nombre. Comprueba que existe
`NOMBRE_CARPETA-REV/bases_de_datos/BASE_DATOS_DEPURADA.xlsx`. El nombre que se le
pasa al programa es el de la materia **sin** el `-REV`.

**`Faltan librerias obligatorias`**
Ejecuta el comando exacto que imprime el propio mensaje. Son tres: openpyxl,
python-docx y matplotlib.

**`python3: command not found`** (Windows)
Usa `python` en lugar de `python3` en todos los comandos.

## Un resultado se ve raro

**«Una columna de notas aparece como contexto» (o al reves).**
Mira la tabla B del modo `--plan`, o la hoja `COLUMNAS` del Excel: cada columna
trae el papel que se le asigno y por que. Se corrige agregando la palabra que usa
esa materia al `config.json`, en el apartado `palabras`. No hace falta tocar codigo.

**«No se pudo comprobar mi hipotesis».**
La tabla A dice el motivo exacto. Suele ser una de dos: la hipotesis nombra una
medida que la base no registra, o compara un grupo que no existe como columna. La
solucion no es forzarla con otra columna parecida: es reformularla sobre lo que si
esta, o registrar lo que falta para el proximo semestre.

**«Salieron muy pocos hallazgos».**
Es un resultado honesto, no una falla. El informe dice cuantos faltaron y que
informacion haria falta. Rellenarlos con conclusiones que los datos no sostienen es
peor que entregar cuatro.

**«Salieron demasiadas relaciones y ninguna me sirve».**
Revisa la columna `tipo` en la hoja `RELACIONES`. Las marcadas como *esperable* son
cruces entre medidas del mismo tipo: dos parciales van juntos porque el que rinde
bien rinde bien en todo. Las utiles son las de *entre variables distintas*.

**«Una relacion fuerte que no me creo».**
Mira `estudiantes` y `sobrevive_al_ajuste`. Una relacion sobre seis casos, o una
que no sobrevive al ajuste por comparaciones multiples, es una pista para mirar,
no un hallazgo para actuar.

**«Los que abandonaron salen en “Sin datos suficientes”».**
La hoja `ABANDONOS` de la Etapa 2 guarda el motivo de la separacion, no las
calificaciones de esas personas. Entran en el conteo del curso pero no en los
cruces. El programa lo avisa al empezar; no es un error del analisis.

**«La asistencia da un numero raro».**
Se expresa siempre entre 0 y 1, aunque la materia la registre con letras, con un
puntaje sobre 5 o en porcentaje. Cada columna se divide por su maximo antes de
promediar.

## Comprobar que dos computadoras dieron lo mismo

Compara la **huella del analisis** que imprime el resumen de control. Si coincide,
las dos corridas produjeron exactamente las mismas cifras. La huella no incluye las
imagenes: dos maquinas pueden generar PNG distintos byte a byte y decir lo mismo.

Si no coincide, revisa en este orden: que la base de entrada sea la misma, que la
hipotesis se haya escrito igual, y que el `config.json` no se haya modificado en
una de las dos.

## Volver a empezar

Esta etapa no toca nada de la entrada. Se puede ejecutar tantas veces como haga
falta: cada corrida sobrescribe sus propios resultados y deja la base depurada
intacta.
