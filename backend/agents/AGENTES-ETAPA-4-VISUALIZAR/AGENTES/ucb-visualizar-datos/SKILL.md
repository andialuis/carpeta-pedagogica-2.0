---
name: ucb-visualizar-datos
description: >
  Etapa 4 (Visualizar) del ciclo de analitica del aprendizaje de la UCB. Convierte
  el RESULTADOS_ANALISIS.xlsx de la etapa previa en un tablero de tres pestañas —
  vision general, hipotesis y hallazgos, plan de intervencion— en un unico archivo
  HTML que se abre con doble clic, sin internet y sin servidor. No calcula ni una
  cifra nueva: muestra las del analisis. Usalo cuando el docente pida un tablero,
  un dashboard, visualizar resultados o proyectar el analisis, o cuando mencione la
  Etapa 4 / VISUALIZAR.
---

# Etapa 4 — Visualizar datos del aula (UCB)

El programa que hace el trabajo **ya existe y esta probado**: `scripts/visualizar.py`.
Tu papel es conversar con el docente, obtener su aprobacion y ejecutarlo.

> **No escribas HTML a mano.** No generes un tablero nuevo, no enlaces librerias de
> graficos y no calcules una sola cifra para "completar". El programa es la fuente
> de verdad: garantiza que el tablero diga exactamente lo mismo que el informe y que
> el archivo se abra sin internet. Si algo falla, lee `referencias/diagnostico.md`.

## Antes de empezar

**Ubica la habilidad.** Localizala una sola vez y usa esa ruta en todos los comandos:

```bash
find . -name visualizar.py -path "*ucb-visualizar-datos*"
```

En Windows (PowerShell): `Get-ChildItem -Recurse -Filter visualizar.py`

En adelante, `<SKILL>` es la carpeta que contiene este archivo.

**Comprueba que la etapa previa termino.** Esta etapa no lee la base de datos: lee
las cifras que el analisis ya calculo.

```bash
ls "NOMBRE_CARPETA-REV/bases_de_datos/RESULTADOS_ANALISIS.xlsx"
```

Si no existe, detente y dile al docente que primero hay que correr la Etapa 3.

**Si es la primera vez en esta computadora**, ejecuta el instalador:

```bash
python3 <SKILL>/instalar_4.py
```

Se llama `instalar_4.py` por su etapa. Cada etapa trae el suyo y no se pisan.

> En Windows usa `python` en lugar de `python3` en todos los comandos.

---

## Paso 1 — Encuadre (PAUSA)

Saluda al docente y preguntale exactamente esto:

1. ¿Cual es el nombre exacto de la carpeta que contiene el analisis?
   (Ej: `MATERIA SIS-12026`; la habilidad busca sola la carpeta `-REV`)
2. Basado en el analisis previo, ¿hay alguna metrica o descubrimiento clave que
   quieras que resalte con mayor importancia en la pantalla principal?

**Sobre la segunda pregunta**, ayudalo si duda. Lo que va en ese lugar es lo primero
que vera la sala: conviene que sea una cifra que **exija una decision**, no la mas
llamativa. «Cuantos estudiantes estan bajo el umbral de riesgo» sirve; «el promedio
del curso» no, porque no le dice a nadie que hacer.

Si pide algo que el analisis no calculo, el programa **no lo inventa**: pone el
numero de hallazgos y explica en pantalla que no encontro lo pedido.

**Detente y espera la respuesta.** No abras el archivo todavia.

---

## Paso 2 — Que se va a mostrar (PAUSA)

Ejecuta el modo plan. **No escribe ni un solo archivo**:

```bash
python3 <SKILL>/scripts/visualizar.py "NOMBRE_CARPETA" --raiz "." --plan --destacar "LO QUE PIDIO EL DOCENTE"
```

Salen cuatro tablas. **Transcribeselas al docente** y cierra preguntando:
**"¿Apruebas esto? ¿Cambio algo?"**

| Tabla | Que muestra |
|---|---|
| **A** | Cuantos hallazgos, hipotesis, perfiles e indicadores trae el analisis |
| **B** | Que va a contener cada una de las tres pestañas |
| **C** | Que cifra ira en el lugar destacado |
| **D** | Que no se va a poder mostrar porque el analisis no lo produjo |

### Que mirar en cada tabla

- **A es el termometro del tablero.** Si el analisis trae tres hallazgos, el tablero
  tendra tres: no se rellena con adornos. Un tablero corto y honesto es util; uno
  inflado hace tomar malas decisiones.
- **B deja ver si alguna pestaña va a quedar pobre.** Si es asi, revisa primero que
  no se este dejando fuera algo que el analisis si produjo.
- **C es la unica decision estetica que toma el docente.** Confirmasela con sus
  palabras antes de seguir.
- **D es la que hay que leer completa.** Es lo que el tablero no podra responder, y
  se dice antes de construirlo, no despues.

**Detente y espera la aprobacion explicita.**

---

## Paso 3 — Construir

El mismo comando, sin `--plan`:

```bash
python3 <SKILL>/scripts/visualizar.py "NOMBRE_CARPETA" --raiz "." --destacar "LO QUE PIDIO EL DOCENTE"
```

Genera un unico archivo en `NOMBRE_CARPETA-REV/RESULTADOS/ETAPA 4 - VISUALIZAR/`:
`DASHBOARD_ANALISIS.html`. Se abre con doble clic. El analisis queda intacto.

Si alguna comprobacion falla, **el programa no guarda el tablero**. Es deliberado:
mas vale no tener tablero que tener uno que contradiga al informe.

---

## Paso 4 — Reportar

El programa imprime un RESUMEN DE CONTROL. **Transcribeselo al docente sin
adornarlo** y llama su atencion sobre:

- **Que contiene cada pestaña y de que hoja salio cada cifra.** Toda cifra del
  tablero tiene una hoja de origen; ninguna se calculo aqui.
- **El equilibrio entre grafico y texto.** El programa lo mide y lo dice pestaña por
  pestaña. Se busca cerca del **60% grafico y 40% texto** en las dos primeras: es la
  proporcion a la que un tablero se entiende desde el fondo de la sala. La tercera
  esta exenta y se dice por que.
- **Las cuatro comprobaciones**: que no pida nada a internet, que no aparezca ningun
  nombre, que ninguna pestaña quedo vacia y que las cifras coincidan con el Excel.
- **Lo que no se pudo mostrar.** Nombralo. Es la agenda de lo que conviene registrar
  el proximo semestre.

Termina con **una linea**: como abrir el archivo y que hacer con el.

### Adelantate a tres preguntas

**"¿Por que no aparecen los nombres?"** Porque el tablero se proyecta. Solo hay
codigos, y la tabla que traduce codigo a persona **no esta dentro del archivo**, ni
siquiera oculta en el codigo. Esa la abre el docente por separado.

**"¿Puedo mandarlo por correo?"** Si, es un solo archivo y no necesita internet.
Justamente por eso no lleva nombres.

**"La tercera pestaña no tiene graficos."** Es a proposito. Las dos primeras existen
para convencer; la tercera, para actuar. Una accion se lee, no se mira.

### Demuestra R6 antes de cerrar

R6 exige que el programa no lleve datos adentro. Corre esto con una palabra de lo
que el docente pidio destacar y ensenale el resultado vacio:

```bash
grep -ril "PALABRA_DE_LO_QUE_PIDIO" <SKILL>/scripts/
```

No debe devolver nada.

---

## Lo que esta etapa NO hace

R1 es la regla de oro: **esta etapa muestra, no analiza.** No calcula ni una cifra,
no saca conclusiones propias y no reordena a nadie con un criterio suyo.

| Si el docente pide... | Corresponde a |
|---|---|
| «agrega el promedio de tal grupo» | Etapa 3 — Analizar |
| «cambia el orden de los estudiantes» | Etapa 3: el orden sale de PRIORIDADES |
| «pon una accion para este grupo» | Etapa 3: las acciones las escribe el analisis |
| «corrige esta nota» | Etapa 1 y despues Etapa 2 |
| «que se vea mejor proyectado» | **Si**, es de esta etapa |

*Ante la duda: si la accion produce una cifra nueva, no es de esta etapa; si cambia
como se ve una cifra existente, si.*

Las nueve restricciones completas estan en `referencias/reglas-etapa4.md`.

---

## Funciona con cualquier materia

El programa **no trae escrita ni una cifra, ni un nombre de columna, ni una ruta**.
Lee las hojas del analisis y arma lo que haya. Si una hoja no vino, esa parte del
tablero no aparece y se dice en pantalla en vez de fabricarla.

Lo que si necesita de cualquier materia: un `RESULTADOS_ANALISIS.xlsx` con al menos
las hojas `HALLAZGOS`, `ACCIONES` y `PRIORIDADES`. Sin esas tres, el programa se
detiene y pide volver a la Etapa 3.

---

## Referencias (leelas solo cuando las necesites)

| Archivo | Cuando abrirlo |
|---|---|
| `referencias/formato-salida.md` | El docente pregunta que significa una parte del tablero |
| `referencias/reglas-etapa4.md` | Dudas sobre si una accion pertenece a esta etapa |
| `referencias/diagnostico.md` | El programa fallo, o el tablero se ve raro |
