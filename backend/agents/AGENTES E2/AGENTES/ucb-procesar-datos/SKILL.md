---
name: ucb-procesar-datos
description: >
  Etapa 2 (Procesar) del ciclo de analitica del aprendizaje de la UCB. Toma el
  BASE_INTEGRADA.xlsx que dejo la Etapa 1 y lo depura: protege la identidad,
  unifica las escalas de calificacion, detecta valores anomalos, interpreta las
  celdas vacias y separa a quienes abandonaron, sin sacar ni una conclusion.
  Usalo cuando el docente pida depurar, limpiar, anonimizar o procesar su base
  integrada, o cuando mencione la Etapa 2 / PROCESAR.
---

# Etapa 2 — Procesar los datos del aula (UCB)

El programa que hace el trabajo **ya existe y esta probado**: `scripts/procesar.py`.
Tu papel es conversar con el docente, obtener su aprobacion y ejecutarlo.

> **No escribas codigo de procesamiento de datos.** No generes un script nuevo, no
> reimplementes estos pasos en pandas y no edites el `.xlsx` tu mismo para "ayudar".
> El programa es la fuente de verdad: garantiza que dos computadoras distintas
> produzcan exactamente la misma base depurada. Si algo falla, lee
> `referencias/diagnostico.md`.

## Lo que esta etapa NO hace

Esta habilidad **no vuelve a hacer nada de la Etapa 1**. Aquella consolido y
describio sin tocar un valor; esta transforma. La frontera es estricta:

| La Etapa 1 hizo esto | Esta etapa hace esto otro |
|---|---|
| Detecto el conflicto de escalas y lo reporto | **Aplica** la conversion que el docente apruebe |
| Conservo todas las columnas de identidad | **Las reemplaza** por un codigo |
| Clasifico cada vacio en `COBERTURA` | **Interpreta** ese vacio con esa clasificacion |
| Anoto problemas de integracion en `INCIDENCIAS` | **Detecta anomalias estadisticas** de valor |
| Tenia prohibido separar a nadie | **Separa** a quienes abandonaron |

Si el docente pide algo que ya hizo la Etapa 1 —volver a cruzar archivos, rescatar
una foto, buscar ponderaciones en un silabo— **no lo hagas aqui**: eso significa que
hay que volver a correr `ucb-preparar-datos`.

## Antes de empezar

**Ubica la habilidad.** Localizala una sola vez y usa esa ruta en todos los comandos:

```bash
find . -name procesar.py -path "*ucb-procesar-datos*"
```

En Windows (PowerShell): `Get-ChildItem -Recurse -Filter procesar.py`

En adelante, `<SKILL>` es la carpeta que contiene este archivo. La ruta habitual es
`AGENTES/ucb-procesar-datos`.

**Corre el instalador, una sola vez por computadora.** Lleva el numero de su
etapa —`instalar_2.py`— para no confundirlo con el de la Etapa 1. Comprueba el entorno,
verifica que la habilidad esta completa y la prueba entera con una base inventada
antes de tocar un solo dato real:

```bash
python3 <SKILL>/instalar_2.py
```

Debe terminar con todos los controles en `[OK]`. Si falta una dependencia, el
mensaje trae el comando exacto para instalarla (`pip install openpyxl python-docx`).
El instalador tambien deja anunciada la habilidad en el `AGENTS.md` de la raiz, para
que el agente la descubra por su cuenta.

Si el docente ya lo corrio antes en esta computadora, no hace falta repetirlo.

**Comprueba la entrada.** Esta etapa no empieza de cero: necesita el resultado de la
anterior. Debe existir `NOMBRE_CARPETA-REV/bases_de_datos/BASE_INTEGRADA.xlsx`. Si no
esta, el docente tiene que correr primero la Etapa 1.

> **Sirve para cualquier materia.** El programa no sabe nada del curso que va a
> procesar: no tiene escritos nombres de columnas, ni instrumentos, ni escalas. Todo
> lo descubre leyendo la base y sus hojas de auditoria en cada ejecucion. Da igual
> que sean 12 estudiantes o 200, cuatro columnas o noventa, quimica o derecho.
>
> Si a la base le falta alguna hoja de auditoria, el programa **continua sin ella y
> lo avisa**. Nunca inventa una columna para tapar el hueco.

> En Windows usa `python` en lugar de `python3` en todos los comandos de este
> archivo.

---

## Paso 1 — Encuadre (PAUSA)

Saluda al docente y preguntale exactamente esto:

1. ¿Cual es el nombre exacto del archivo que vamos a procesar? (Ej: `BASE_INTEGRADA`)
2. ¿Pudiste revisar tu BASE INTEGRADA de la etapa previa, o prefieres darme ahora
   tus observaciones?

**Detente y espera la respuesta.** No leas la base todavia.

La segunda pregunta no es de cortesia y admite dos caminos, los dos validos:

- **Si ya la reviso**, lo que traiga es informacion de primera mano: *"me llamo la
  atencion que Fulano aparece con todo vacio"*, *"el tercer parcial creo que esta
  sobre 40"*. Anotalo: cambia como vas a leer las propuestas del Paso 2.
- **Si no la reviso**, no lo hagas sentir en falta. Dile que no hace falta, que el
  Paso 2 le va a mostrar exactamente lo que se propone tocar antes de tocarlo, y que
  ahi podra opinar con las tablas delante.

---

## Paso 2 — Criterios y aprobacion (PAUSA)

Ejecuta el programa en **modo propuesta**. No transforma nada: solo lee la base y
propone.

```bash
python3 <SKILL>/scripts/procesar.py "NOMBRE_CARPETA" --raiz "." --proponer
```

Devuelve **cuatro tablas**. Muestraselas al docente completas, sin resumirlas:

| Tabla | Que propone |
|---|---|
| **A · Identidad** | Columnas con nombre o correo que se reemplazaran por un codigo |
| **B · Escalas** | Instrumento, escala de origen, escala de destino, factor y de donde sale la regla |
| **C · Anomalias** | Valores sospechosos, con su columna y el motivo |
| **D · Abandonos** | Quienes se propone mover a `ABANDONOS`, con el motivo y desde que fecha |

Cierra preguntando: **"¿Apruebas estos criterios? ¿Cambio alguno?"**

**Detente y espera la aprobacion explicita. No transformes nada antes.**

### Que mirar en cada tabla

- **A** debe incluir **todas** las columnas de identidad, no solo la de la lista
  oficial. La base trae la identidad repetida una vez por cada archivo de origen, y
  basta con que una se escape para que la proteccion no sirva de nada.
- **B** es la que mas cuidado exige. Si una regla trae un aviso de escala sin
  resolver, el programa **no la convierte**: la deja pendiente. Eso es correcto.
  Pregunta al docente que hacer con cada una.
- **C** no se corrige nunca en esta etapa. Se reporta y se sigue.
- **D** es donde el docente tiene la ultima palabra. El programa cruza cuatro
  senales, pero solo el sabe si alguien dejo de venir por una razon que no esta en
  los datos.
- **D.1 no la saltes nunca.** Debajo de la tabla D, el programa dice **con que
  senales pudo trabajar en esta base**. Si alguna sale con `[NO]`, leesela al
  docente tal cual. Que la tabla D salga vacia puede significar dos cosas muy
  distintas: que nadie abandono, o que en esta materia no habia con que
  comprobarlo. Nunca le digas "no hubo abandonos" sin mirar antes esa lista.

Cuando el docente apruebe con cambios, escribe sus decisiones en un JSON:

```bash
echo '{"escalas_omitidas":[],"abandonos_excluidos":[],"abandonos_forzados":[]}' > criterios.json
```

Los tres campos van vacios si el docente aprueba todo. Para vetar algo, se copian
**los nombres tal como aparecen en las tablas A a D** de esa corrida — el instrumento
como lo escribe la hoja `REGLAS_EVALUACION`, y el estudiante por su codigo de la
lista oficial. Cambian de materia a materia; el programa los toma como vengan.

- `escalas_omitidas`: instrumentos que **no** se convierten, aunque el programa
  proponga hacerlo.
- `abandonos_excluidos`: estudiantes que el programa propuso mover y el docente
  quiere **dejar en ACTIVOS**.
- `abandonos_forzados`: estudiantes que el docente quiere mover a `ABANDONOS` aunque
  el programa no lo haya propuesto.

Si aprueba todo sin cambios, puedes omitir `--criterios`.

---

## Paso 3 — Ejecutar

```bash
python3 <SKILL>/scripts/procesar.py "NOMBRE_CARPETA" --raiz "." --criterios criterios.json
```

El programa genera, dentro de `NOMBRE_CARPETA-REV/`:

- `bases_de_datos/BASE_DATOS_DEPURADA.xlsx` con siete hojas: `ACTIVOS`,
  `ABANDONOS`, `CAMBIOS`, `ANOMALIAS`, `VACIOS`, `VERIFICACION` y
  `REGLAS_EVALUACION`.
- `bases_de_datos/EQUIVALENCIA_CODIGOS.xlsx`, la tabla que permite volver de un
  codigo al estudiante. **Es el unico archivo que vuelve a contener nombres.**
- `RESULTADOS/ETAPA 2 - PROCESAR/INFORME_PROCESAMIENTO.docx`.

`BASE_INTEGRADA.xlsx` y todo lo que venga de la Etapa 1 **quedan intactos**. El
programa lo verifica al terminar y lo informa.

---

## Paso 4 — Reportar

El programa imprime un RESUMEN DE CONTROL. **Transcribeselo al docente sin
adornarlo** y llama su atencion sobre:

- **La cuenta que tiene que cerrar**: activos + abandonos debe dar exactamente el
  total que entrego la Etapa 1. Si no cierra, algo se perdio y hay que detenerse.
- **Vacios por columna, separados por tipo.** `encontrado_vacio` y `ausente` parecen
  el mismo hueco y no lo son: uno figura en el archivo sin nota, el otro no figura.
- **Anomalias detectadas.** Ninguna fue corregida. Son para el ojo del docente. Las
  que llevan el aviso *"quedo en ABANDONOS"* casi nunca son errores de captura: son
  el rastro de que ese estudiante dejo de venir.
- **Senales de abandono disponibles** (`4 de 4`). Si dice menos de las necesarias, el
  resumen agrega `NO ALCANZAN: revisar a mano`. Dilo en voz alta: la separacion de
  abandonos de esa materia es un indicio, no un veredicto.
- **Conversiones de escala aplicadas, con su factor.** Y las que quedaron pendientes.
- **Relaciones que cambiaron de sentido.** Es el aviso mas importante del informe:
  significa que la limpieza altero lo que los datos decian.
- **Huella de la hoja `ACTIVOS`**: el codigo que permite comparar resultados entre
  computadoras.

Termina con **una linea** diciendole que le toca hacer a el.

### Adelantate a dos confusiones

**"¿Por que sigo viendo nombres?"** En `EQUIVALENCIA_CODIGOS.xlsx`, si. Es
deliberado: sin esa tabla el docente no podria volver del codigo a la persona para
intervenir en el aula. Ese archivo se guarda aparte y no se comparte.

**"¿Por que hay dos columnas de la misma nota?"** Toda conversion **conserva la
columna original al lado** de la convertida. Es lo que permite auditar el factor
aplicado. La hoja `CAMBIOS` dice, columna por columna, que se hizo y por que.

**"Dice 0 conversiones aplicadas, ¿fallo algo?"** No. Cuando la planilla ya usa el
mismo puntaje que declara la normativa, el factor seria 1 y convertir solo dejaria
una columna gemela. Esas aparecen aparte, como *escalas que ya estaban correctas*, y
quedan igual anotadas en la hoja `CAMBIOS`.

### Demuestra R4 antes de cerrar

R4 exige probar que no quedo ningun dato del curso escrito dentro del codigo. Corre
esto con un apellido real y ensenale el resultado vacio:

```bash
grep -ril "APELLIDO_DE_UN_ESTUDIANTE" <SKILL>/scripts/
```

No debe devolver nada. Las escalas tambien se leen de `REGLAS_EVALUACION` en cada
ejecucion: ninguna ponderacion esta escrita en el programa.

---

## Lo que esta prohibido en esta etapa

R1 es la regla de oro: **esta etapa depura, no analiza.** No calcules la nota final,
no promedies instrumentos entre si, no busques correlaciones, no armes perfiles de
estudiantes, no saques conclusiones y no decidas si un vacio vale cero para la nota.
Todo eso es de la Etapa 3 y hacerlo aqui contamina el analisis con decisiones que
nadie aprobo.

*Ante la duda: si el resultado es un dato mas limpio, es de esta etapa; si es una
conclusion sobre los estudiantes, no lo es.*

Las siete restricciones completas estan en `referencias/reglas-etapa2.md`.

---

## Referencias (leelas solo cuando las necesites)

| Archivo | Cuando abrirlo |
|---|---|
| `referencias/formato-salida.md` | El docente pregunta que significa una hoja o columna del resultado |
| `referencias/reglas-etapa2.md` | Dudas sobre si una accion pertenece a esta etapa |
| `referencias/diagnostico.md` | El programa fallo, o un resultado se ve raro |
