# Las seis restricciones de la Etapa 1

No son consejos: son el limite entre Preparar y Procesar. Cada una esta hecha
cumplir por el programa, no por la buena voluntad del agente.

## R1 — Esta etapa solo prepara, no limpia

Prohibido: corregir ortografia, rellenar celdas vacias, convertir escalas,
calcular o promediar notas, separar a quien abandono, ocultar nombres.

**Ante la duda:** si la accion *transforma* un valor, no es de esta etapa; si lo
*describe* o lo *conserva*, si.

Por que importa: la Etapa 2 diagnostica la calidad de los datos. Si aqui rellenas
un vacio con cero, la Etapa 2 ya no puede distinguir "no rindio" de "no figura", y
el diagnostico queda falseado.

*Como se cumple:* el programa copia los valores tal como vienen; ni siquiera
reinterpreta fechas ni numeros.

## R2 — Los originales no se tocan

La carpeta del docente es de solo lectura. Todo ocurre en `NOMBRE_CARPETA-REV/`.

*Como se cumple:* solo se usa `shutil.copy2`. Al terminar, el programa recalcula
el SHA-256 de cada archivo de entrada y lo compara con el del inicio; el resumen
informa `Archivos originales sin modificar: SI`.

## R3 — El programa no lleva datos adentro

Ni nombres de carpeta, ni rutas, ni estudiantes, ni notas escritos en el codigo.
Todo entra en tiempo de ejecucion.

*Como se cumple:* la carpeta llega por argumento, la configuracion por
`config.json`, y las transcripciones de imagenes van a archivos `.xlsx` aparte,
nunca al codigo. Para demostrarlo, busca en el codigo un apellido de tu curso:

```bash
grep -ril "APELLIDO_DE_UN_ESTUDIANTE" AGENTES/ucb-preparar-datos/scripts/
```

No debe devolver nada.

## R4 — Un solo punto de entrada

Un unico comando ejecuta todo el flujo: `organizar.py`. El docente nunca corre
varios scripts en orden.

*Nota de diseño:* la logica esta repartida en modulos `skill_*.py` (uno por tarea:
clasificar, leer planillas, identidad, integrar, reglas, registros, reportar) en
lugar de un solo archivo gigante. El requisito real — **un comando, tareas
separadas y reutilizables** — se cumple; 1.900 lineas en un solo archivo serian
imposibles de mantener y de reutilizar en la Etapa 2.

## R5 — Que funcione en cualquier computadora

*Como se cumple:* la unica dependencia es **openpyxl**. Todo lo demas es
biblioteca estandar de Python — incluida la lectura de `.docx` y `.pptx`, que se
abren como ZIP+XML. No se usa pandas.

Consecuencia deliberada: ninguna libreria opcional cambia el resultado. Si
`pytesseract` esta instalado o no, la base sale igual (las imagenes manuscritas
siempre generan una plantilla para revision humana).

## R6 — Nadie queda fuera en silencio

Ni una fila ni una columna se pierde. Lo que no se puede resolver va al informe,
nunca a la basura.

*Como se cumple:* filas huerfanas, colisiones, ambiguedades, formatos ilegibles y
archivos no aprobados generan todos una entrada en `INCIDENCIAS` con el contenido
completo de la fila de origen.
