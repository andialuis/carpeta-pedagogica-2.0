---
name: ucb-analizar-datos
description: >
  Etapa 3 (Analizar) del ciclo de analitica del aprendizaje de la UCB. Toma el
  BASE_DATOS_DEPURADA.xlsx de la etapa previa y encuentra hallazgos con
  evidencia: pone a prueba la sospecha del docente, cruza asistencia, plataforma
  y notas, descubre los grupos que el promedio esconde y deja indicadores y
  acciones listos para el aula. No limpia datos ni construye tableros.
  Usalo cuando el docente pida analizar, cruzar variables, buscar hallazgos,
  comprobar una sospecha o encontrar estudiantes en riesgo, o cuando mencione la
  Etapa 3 / ANALIZAR.
---

# Etapa 3 — Analizar datos del aula (UCB)

El programa que hace el trabajo **ya existe y esta probado**: `scripts/analizar.py`.
Tu papel es conversar con el docente, ayudarlo a formular su sospecha, obtener su
aprobacion y ejecutarlo.

> **No escribas codigo de analisis.** No generes un script nuevo, no reimplementes
> estos pasos en pandas y no calcules tu mismo un promedio para "adelantar". El
> programa es la fuente de verdad: garantiza que dos computadoras distintas
> produzcan exactamente los mismos hallazgos, con las mismas pruebas estadisticas
> y el mismo ajuste por comparaciones multiples. Si algo falla, lee
> `referencias/diagnostico.md`.

## Antes de empezar

**Ubica la habilidad.** Esta carpeta puede estar en cualquier lugar del espacio de
trabajo. Localizala una sola vez y usa esa ruta en todos los comandos:

```bash
find . -name analizar.py -path "*ucb-analizar-datos*"
```

En Windows (PowerShell): `Get-ChildItem -Recurse -Filter analizar.py`

En adelante, `<SKILL>` es la carpeta que contiene este archivo. La ruta habitual es
`AGENTES/ucb-analizar-datos`.

**Comprueba que la etapa previa termino.** Esta etapa no lee archivos sueltos: lee
lo que dejo la Etapa 2.

```bash
ls "NOMBRE_CARPETA-REV/bases_de_datos/BASE_DATOS_DEPURADA.xlsx"
```

Si no existe, detente y dile al docente que primero hay que correr la Etapa 2.

**Si es la primera vez en esta computadora**, ejecuta el instalador. Comprueba el
entorno, prueba la habilidad entera con un curso inventado y la deja anunciada:

```bash
python3 <SKILL>/instalar_3.py
```

Se llama `instalar_3.py` por su etapa. Cada etapa trae el suyo y no se pisan.

> En Windows usa `python` en lugar de `python3` en todos los comandos de este
> archivo. Si `python3` no existe, esa es la causa.

---

## Paso 1 — Encuadre (PAUSA)

Saluda al docente y preguntale exactamente esto:

1. ¿Cual es el nombre exacto de la carpeta que contiene los datos ya depurados?
   (Ej: `MATERIA SIS-12026`; la habilidad busca sola la carpeta `-REV`)
2. ¿Tienes alguna sospecha, intuicion o problema especifico que quieras someter a
   analisis? (Ej: desercion, bajo rendimiento, poca participacion)
3. ¿Cual es tu hipotesis para explicarlo? Si no tienes una, dimelo y trabajo sin
   ella.

**Al hacer la tercera pregunta, muestrale que hace que una hipotesis se pueda
comprobar** y ofrecele reformular la suya si le falta algo. Una hipotesis
comprobable dice cuatro cosas:

| | Que tiene que decir |
|---|---|
| **a** | **A quien compara**: un grupo contra otro, o un grupo contra el resto del curso |
| **b** | **Que se mide**: una cifra que exista en los datos (nota, asistencia, entregas, entradas a la plataforma), no una impresion |
| **c** | **En que direccion**: mas o menos, mejor o peor |
| **d** | **En que periodo**, si eso cambia la respuesta |

Y sobre todo **tiene que poder salir falsa**. Si no hay ningun resultado posible
que la descarte, no es una hipotesis: es una opinion.

> Mal formulada: *"los virtuales rinden peor"*.
> Bien formulada: *"los estudiantes de modalidad virtual obtienen una nota
> promedio mas baja que los presenciales en las evaluaciones de este semestre"*.

**El programa admite las dos formas en que los docentes suelen hablar:**

- **Comparando grupos** — "los del turno noche faltan mas". Necesita una columna
  que diga a que grupo pertenece cada estudiante.
- **Relacionando dos medidas** — "los que menos entran a la plataforma sacan
  peores notas". No necesita ningun grupo.

Si la hipotesis menciona algo que no esta en los datos, **diselo en ese momento, no
al final**. El programa lo detecta y lo reporta en la tabla A.

**Detente y espera la respuesta.** No leas la base todavia.

---

## Paso 2 — El plan de analisis (PAUSA)

Ejecuta el modo plan. **No escribe ni un solo archivo**:

```bash
python3 <SKILL>/scripts/analizar.py "NOMBRE_CARPETA" --raiz "." --plan --hipotesis "LA HIPOTESIS DEL DOCENTE, ENTRE COMILLAS"
```

Salen cinco tablas. **Transcribeselas al docente** y cierra preguntando:
**"¿Apruebas este plan? ¿Cambio algo?"**

| Tabla | Que muestra |
|---|---|
| **A** | Su hipotesis reescrita: que se mide, a quien compara y si se puede comprobar |
| **B** | Las variables disponibles para cruzar, con el papel que el programa les asigno |
| **C** | Las que no sirven porque valen lo mismo para todos |
| **D** | Los analisis que no se van a poder hacer, y por que |
| **E** | Cuantos estudiantes entran en cada analisis |

### Que mirar en cada tabla

- **A es la mas importante.** Si dice `Se puede medir: NO`, no sigas adelante como
  si nada: leele el motivo al docente y ofrecele reformular. Una hipotesis
  contestada con la columna equivocada es peor que una sin contestar.
- **B es donde se detectan los errores de lectura.** Si una columna de notas quedo
  marcada como `contexto del estudiante`, o una de asistencia como `calificacion`,
  el analisis entero saldra torcido. Se corrige agregando la palabra que use esa
  materia al `config.json`, en el apartado `palabras`.
- **C no es un descarte silencioso.** Una columna que vale lo mismo para todos no
  puede explicar ninguna diferencia; se dice y no se usa.
- **D es la que hay que leer completa.** Es la lista de lo que esta materia no
  permite averiguar. Callarla haria creer al docente que el analisis fue completo.
- **E es el tamano real de cada respuesta.** Si un analisis entra con seis
  estudiantes, su resultado es una pista, no una conclusion.

**Detente y espera la aprobacion explicita.** Aun no analices nada.

---

## Paso 3 — Ejecutar

El mismo comando, sin `--plan`:

```bash
python3 <SKILL>/scripts/analizar.py "NOMBRE_CARPETA" --raiz "." --hipotesis "LA HIPOTESIS DEL DOCENTE"
```

Si el docente no tiene hipotesis, omite `--hipotesis`: el programa analiza igual y
plantea las suyas.

Genera, dentro de la carpeta `-REV`:

- `bases_de_datos/RESULTADOS_ANALISIS.xlsx` — ocho hojas con todas las cifras ya
  calculadas. **Es lo que va a consumir la Etapa 4.**
- `RESULTADOS/ETAPA 3 - ANALIZAR/INFORME_FINAL_ANALISIS.docx` — el informe con sus
  cuatro apartados y los graficos insertados.
- `RESULTADOS/ETAPA 3 - ANALIZAR/graficos/` — las imagenes de respaldo.

La base depurada queda intacta.

---

## Paso 4 — Reportar

El programa imprime un RESUMEN DE CONTROL. **Transcribeselo al docente sin
adornarlo** y llama su atencion sobre:

- **Estudiantes analizados**: activos + abandonos. Los dos grupos entran en todo.
  Si el resumen trae el aviso de que la hoja ABANDONOS solo llego con el motivo,
  **leeselo**: significa que a esos estudiantes se los conto pero no se los pudo
  cruzar.
- **Como se construyo la medida de rendimiento.** No es la nota oficial de nadie:
  es una variable de analisis en escala 0 a 1, armada para poder comparar
  instrumentos con escalas distintas. Dilo antes de que lo pregunte.
- **Hallazgos que se sostienen, y cuantos faltaron.** Si faltaron, el programa dice
  que informacion haria falta. No los completes tu con conclusiones que los datos
  no sostienen.
- **Parejas comprobadas.** Si se cruzaron cientos de parejas, algunas darian
  "significativas" por puro azar. Por eso cada relacion trae
  `sobrevive_al_ajuste`: las que dicen `no` son pistas, no hallazgos.
- **Analisis que no se pudieron hacer.** Nombralos uno por uno. Ninguno es
  decorativo.
- **Huella del analisis**: el codigo que permite comparar resultados entre
  computadoras.

Termina con **una linea** diciendole que le toca hacer a el.

### Adelantate a tres confusiones

**"¿Por que hay un grupo llamado «Sin datos suficientes»?"** Casi siempre son los
que abandonaron: la etapa anterior guarda el motivo de su separacion, no sus
notas. No es un error del analisis, es lo que llego.

**"Esto significa que la asistencia causa la nota."** No. R4: el programa dice que
dos cosas se mueven juntas. Puede ser que una influya en la otra, que las dos
dependan de una tercera, o que sea casualidad. La frase correcta es "van juntas".

**"El programa dice que este estudiante copio."** Nunca dice eso, y tu tampoco. R5:
se presenta la evidencia —una nota alta en una fraccion del tiempo, tres
estudiantes que empiezan con segundos de diferencia— y se dice quien deberia
revisarla. La conclusion sobre una persona la toma el docente.

### Demuestra R6 antes de cerrar

R6 exige que el programa no lleve datos adentro: ni la hipotesis, ni la sospecha,
ni rutas, ni nombres. Corre esto con una palabra distintiva de la hipotesis del
docente y ensenale el resultado vacio:

```bash
grep -ril "PALABRA_DE_SU_HIPOTESIS" <SKILL>/scripts/
```

En Windows: `Select-String -Path <SKILL>\scripts\*.py -Pattern "PALABRA"`

No debe devolver nada. Si devuelve algo, hay un dato del docente incrustado en el
codigo: reportalo de inmediato y no continues.

---

## Lo que esta etapa NO hace

R1 es la regla de oro: **esta etapa analiza, no limpia.** Si aparecen datos sucios,
mal tipados o mal escalados, se reportan y se vuelve a la Etapa 2. Corregirlos aqui
dejaria dos versiones distintas de la misma nota y nadie se enteraria.

| Si el docente pide... | Corresponde a |
|---|---|
| corregir una nota mal cargada | Etapa 1 (el archivo original) y despues Etapa 2 |
| rellenar vacios, unificar escalas, separar abandonos | Etapa 2 — Procesar |
| poner la nota final oficial de cada estudiante | al docente; el programa no la calcula |
| un tablero interactivo, filtros, botones | Etapa 4 — Visualizar |
| decidir quien copio | al docente; esta etapa describe, no acusa |

*Ante la duda: si la accion cambia un dato, no es de esta etapa; si lo mide, lo
compara o lo explica, si.*

Las nueve restricciones completas estan en `referencias/reglas-etapa3.md`.

---

## Funciona con cualquier materia

El programa **no trae escrito ni un nombre de columna, ni un instrumento, ni una
escala**. Reconoce el papel de cada columna por como se comporta y por el
vocabulario de `config.json`. Si una materia usa palabras propias —"quiz",
"coloquio", "taller", "clinica"— se agregan a la lista que corresponda en
`palabras` y el programa las reconoce, sin tocar una linea de codigo.

Lo que si necesita de cualquier materia:

- una columna que identifique al estudiante (la Etapa 2 siempre la deja);
- al menos una columna que se comporte como calificacion;
- para comparar grupos, alguna columna de contexto (turno, modalidad, sede, grupo).

Lo que falte, el programa lo dice en la tabla D y en el apartado de conclusiones
tecnicas. **Nunca lo suple inventando.**

---

## Referencias (leelas solo cuando las necesites)

| Archivo | Cuando abrirlo |
|---|---|
| `referencias/formato-salida.md` | El docente pregunta que significa una hoja, una columna o una cifra del resultado |
| `referencias/reglas-etapa3.md` | Dudas sobre si una accion pertenece a esta etapa |
| `referencias/diagnostico.md` | El programa fallo, o un resultado se ve raro |
