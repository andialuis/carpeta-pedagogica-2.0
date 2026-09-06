# Instrucciones para el agente — Analitica del aprendizaje UCB

Este espacio de trabajo contiene **habilidades (skills)** en `AGENTES/`. Cada una
es una carpeta con un `SKILL.md` que describe un procedimiento, y scripts
deterministas que hacen el trabajo pesado.

## Habilidades y Comandos Rápidos

| Comando / Habilidad | Cuando usarla |
|---|---|
| `/estilo-docente` o `/redactar` | Aplica de inmediato el **Skill de Estilo Editorial Docente** (`.agents/skills/estilo-editorial-docente/SKILL.md`). Redacta, mejora o ajusta el texto con tono sobrio, directo y profesional, sin palabras grandilocuentes ni exageraciones. |
| `AGENTES/ucb-preparar-datos/SKILL.md` | El docente pide **ordenar, preparar, consolidar o integrar** los archivos de una materia; o menciona la Etapa 1 / PREPARAR. Consolida una carpeta desordenada en un unico `BASE_INTEGRADA.xlsx` sin alterar ningun valor. |

## Como usarlas

1. Cuando la peticion del docente coincida con una habilidad, **lee su `SKILL.md`
   completo antes de actuar** y sigue sus pasos al pie de la letra.
2. Los `SKILL.md` tienen **pausas obligatorias**. Cuando una diga "detente y
   espera", detente de verdad: no adelantes trabajo ni supongas la respuesta.
3. Los archivos de `referencias/` se leen **solo cuando hacen falta**, no por
   adelantado. Cada `SKILL.md` indica cuando abrir cada uno.
4. Los archivos de `scripts/` **se ejecutan, no se leen ni se reescriben**. Estan
   probados y garantizan que el resultado sea identico en cualquier computadora.

## Reglas del espacio de trabajo

- Los archivos originales del docente son de **solo lectura**. Todo el trabajo
  ocurre en una carpeta `-REV` aparte.
- **No inventes datos.** Si algo no se puede resolver, va al informe de
  incidencias; nunca se descarta ni se rellena a ojo.
- No escribas datos de estudiantes (nombres, correos, notas) dentro de ningun
  archivo de codigo.


## Etapa 2 · Procesar

Cuando el docente pida **depurar, limpiar, anonimizar o procesar** su base
integrada, o mencione la Etapa 2 / PROCESAR, lee
`AGENTES/ucb-procesar-datos/SKILL.md` completo y siguelo al pie de la letra,
respetando sus dos pausas. Los archivos de `scripts/` se ejecutan; no se leen ni se
reescriben.


## Etapa 3 · Analizar

Cuando el docente pida **analizar, cruzar variables, buscar hallazgos, poner a
prueba una sospecha o encontrar grupos de riesgo** en su base ya depurada, o
mencione la Etapa 3 / ANALIZAR, lee `AGENTES/ucb-analizar-datos/SKILL.md`
completo y siguelo al pie de la letra, respetando sus dos pausas. Los archivos de
`scripts/` se ejecutan; no se leen ni se reescriben.


## Etapa 4 · Visualizar

Cuando el docente pida **un tablero, un dashboard, visualizar los resultados o
mostrar el analisis**, o mencione la Etapa 4 / VISUALIZAR, lee
`AGENTES/ucb-visualizar-datos/SKILL.md` completo y siguelo al pie de la letra,
respetando sus dos pausas. Los archivos de `scripts/` se ejecutan; no se leen ni se
reescriben.
