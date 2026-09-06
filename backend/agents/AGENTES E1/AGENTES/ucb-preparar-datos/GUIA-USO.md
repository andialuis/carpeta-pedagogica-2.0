# Guia de uso — de un prompt largo a una habilidad

## La idea en una imagen

**Antes (prompt clasico).** Pegas 8.800 caracteres de instrucciones en el chat.
El modelo lee todo, y ademas **escribe desde cero** ~74.000 caracteres de codigo
Python. Cada sesion. Si mañana repites el proceso, vuelve a escribirlo — parecido,
pero no identico. Los resultados no se pueden comparar entre computadoras.

**Ahora (habilidad).** El codigo ya existe, probado. El agente lee una ficha corta,
conversa contigo, y ejecuta un comando. El codigo nunca entra a la conversacion.

## Los tres niveles de revelacion progresiva

El agente no carga todo de golpe. Va abriendo capas solo cuando las necesita:

| Nivel | Que lee | Cuanto pesa | Cuando |
|---|---|---|---|
| **1. Descubrimiento** | Solo el `description:` del YAML | ~490 caracteres | Siempre. Es como leer el lomo de un libro en el estante. |
| **2. Activacion** | El cuerpo de `SKILL.md` | ~4.800 caracteres | Solo si le pides preparar una materia. Abre el libro por el indice. |
| **3. Profundidad** | Un archivo de `referencias/` | ~3.000 c/u | Solo ante una duda concreta. Va al capitulo exacto. |
| **—** | `scripts/*.py` | 74.000 caracteres | **Nunca.** Se ejecutan en la terminal; solo vuelve el resultado. |

La diferencia de fondo no es leer menos. Es que **el agente dejo de escribir codigo
y paso a ejecutarlo.** Eso es lo que hace el resultado reproducible.

## Como se ve una sesion completa

```
Tu:     Quiero preparar los datos de mi materia.

Agente: ¡Hola! Antes de empezar:
        1. ¿Cual es el nombre exacto de la carpeta que deseas organizar?
        2. ¿Sabes si hay algun documento con las ponderaciones de cada evaluacion?
        ⏸ ESPERA

Tu:     La carpeta es "MATERIA SIS-12026". Creo que el silabo tiene los puntajes.

Agente: [lista la carpeta y muestra la tabla]

        | Archivo                        | Tipo  | ¿Clave? | Por que                  |
        | registro_matricula_oficial.xlsx| Excel | SI      | Lista oficial            |
        | notas_parciales.xlsx           | Excel | SI      | Notas de parciales        |
        | asistencia_lunes.csv           | CSV   | SI      | Asistencia por fecha      |
        | registros_logs.csv             | CSV   | SI      | Accesos al aula virtual   |
        | silabo_materia.txt             | Texto | SI      | Declara ponderaciones     |
        | Tema_1_Introduccion.pptx       | PPT   | NO      | Material de clase         |

        ¿Apruebas esta lista? ¿Agrego o quito alguno?
        ⏸ ESPERA

Tu:     Apruebala.

Agente: [ejecuta UN comando en la terminal]
        [te transcribe el resumen de control]

        - 8 estudiantes en la lista oficial → 8 filas en la base ✓
        - 32 columnas conservadas
        - 1 fila no reconocida: "Zoraida Fantasma Inexistente" en asistencia_lunes
        - Conflicto: el silabo dice "Primer Parcial 50 puntos" pero la planilla
          usa s/15 y s/35. Lo reporte, no lo resolvi.
        - Huella: 7c5ab4fd0f5b54eb

        Te toca a ti: revisar la hoja INCIDENCIAS y decidir quien es "Zoraida".
```

Las dos pausas no son cortesia: son el punto donde **tu** decides, y el agente no.

## Uso en Google Antigravity

1. **Abre esta carpeta como workspace** (`File → Open Folder` sobre
   `ORQUESTACION/`). Debe ser la carpeta que contiene `AGENTS.md` y `AGENTES/`.
2. **Pon la carpeta de tu materia dentro del workspace.** El agente solo ve lo que
   esta dentro. Los originales no se modifican, asi que es seguro.
3. **Verifica que Antigravity leyo `AGENTS.md`.** Pregunta en el chat del agente:
   *"¿Que habilidades tengo disponibles en este espacio?"* Deberia nombrar
   `ucb-preparar-datos`.
   - Si no lo hace, agrega el mismo contenido en la configuracion de reglas/contexto
     del workspace, o simplemente empieza tu mensaje con:
     `Lee AGENTES/ucb-preparar-datos/SKILL.md y siguelo.`
4. **Pidelo en lenguaje natural**, desde el Agent Manager o el chat del editor:

   > Quiero preparar los datos de mi materia.

5. **Responde las dos pausas.** No dejes que avance sin tu aprobacion: si el agente
   se salta una pausa, dile *"detente, no aprobe la lista todavia"*.
6. **Revisa el resultado** en `MATERIA...-REV/bases_de_datos/BASE_INTEGRADA.xlsx`.

### Requisito unico

```bash
pip install openpyxl
```

No hace falta pandas ni nada mas. En Windows, usa `python` donde aqui diga
`python3`.

### Si quieres probarlo sin datos reales

```bash
python3 AGENTES/instalar.py
```

Genera una materia inventada con todas las dificultades tipicas (encabezados
combinados, nombres invertidos y abreviados, una fila huerfana, 1.200 registros de
aula virtual) para que veas el flujo completo sin exponer a nadie.

## Que hace cada modulo

Cada archivo `skill_*.py` resuelve **una** dificultad concreta del mundo real:

| Modulo | El problema que resuelve |
|---|---|
| `skill_clasificar` | Reparte los archivos por tipo y saca una huella SHA-256 de cada original, para probar despues que no se toco ninguno. |
| `skill_leer_planillas` | Encabezados repartidos en varias filas y celdas combinadas. Decide donde termina el encabezado por **consistencia de tipos**, sin depender del idioma. |
| `skill_leer_documentos` | Abre `.docx` y `.pptx` como ZIP+XML con biblioteca estandar: cero dependencias extra. |
| `skill_extraer_datos` | Rescata notas escritas dentro de documentos; para las fotos deja una plantilla `PENDIENTE_TRANSCRIPCION` y **no detiene** el proceso. |
| `skill_descubrir_reglas` | Encuentra ponderaciones en el silabo y las compara con la escala de cada columna. Reporta conflictos; **no los resuelve**. |
| `skill_identidad` | El corazon. Reconoce a la misma persona escrita de seis formas distintas, en cascada de mas seguro a mas dudoso, y registra con que metodo la reconocio. |
| `skill_resumir_registros` | Detecta que un archivo de 1.200 filas es un registro de accesos, no una planilla, y lo resume por estudiante. |
| `skill_integrar` | Une todo en una fila por estudiante. Evita las trampas clasicas: confundir la columna "N°" con el codigo, o "Carrera" con el nombre. |
| `skill_reportar` | Escribe las 6 hojas de auditoria y calcula la huella que permite comparar resultados entre computadoras. |
| `organizar.py` | El unico punto de entrada. Llama a los demas en orden. |
