# Instrucciones para el agente — Analitica del aprendizaje UCB

Este espacio de trabajo contiene **habilidades (skills)** en `AGENTES/`. Cada una
es una carpeta con un `SKILL.md` que describe un procedimiento, y scripts
deterministas que hacen el trabajo pesado.

## Habilidades disponibles

| Habilidad | Cuando usarla |
|---|---|
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
