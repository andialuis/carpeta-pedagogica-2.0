# Las nueve restricciones de la Etapa 3

Estan en el programa, no solo en el papel. Cuando el docente pida algo y no sepas
si corresponde aqui, la respuesta esta en esta lista.

**R1. ESTA ETAPA ANALIZA, NO LIMPIA.** Si aparecen datos sucios, mal tipados o mal
escalados, se reportan y se vuelve a la etapa anterior. Arreglarlos aqui rompe la
trazabilidad: la Etapa 2 dejo constancia de cada cambio, y una correccion hecha en
el analisis no aparece en ningun registro. Quedarian dos versiones de la misma nota
y nadie sabria cual es la buena.

**R2. NO SE ROMPE EL ANONIMATO.** Los datos vienen con codigo en lugar de nombre y
asi se quedan. El programa no intenta reconstruir identidades ni abre la tabla de
equivalencia: esa la abre el docente, por separado. Todo se refiere al codigo.

**R3. NADA SIN RESPALDO.** Toda afirmacion va con su numero y con cuantos
estudiantes la sostienen. *"No se puede responder con esta informacion"* es una
respuesta valida y valiosa: es preferible a una conclusion inventada.

**R4. NO SE CONFUNDE RELACION CON CAUSA.** El programa puede decir que dos cosas se
mueven juntas. No puede decir que una es la causa de la otra. Puede ser que una
influya en la otra, que las dos dependan de una tercera, o que sea casualidad.

**R5. DESCRIBIR, NO ACUSAR.** Cuando un patron sugiera algo delicado —una nota alta
en una fraccion del tiempo, varios estudiantes que empiezan con segundos de
diferencia— se presenta la evidencia y se dice quien deberia revisarla. La
conclusion sobre una persona la toma el docente, nunca el programa.

**R6. EL PROGRAMA NO LLEVA DATOS ADENTRO.** Ni la hipotesis, ni la sospecha, ni
rutas, ni nombres, ni resultados. Todo entra en cada ejecucion por la linea de
ordenes. Se comprueba con un `grep` sobre `scripts/`, y el instalador lo verifica
por su cuenta en cada corrida de prueba.

**R7. UN SOLO PROGRAMA.** Un unico punto de entrada, `analizar.py`, con cada paso
en su propio modulo con el prefijo `paso_`. El prefijo distingue a estos modulos de
la habilidad completa: la habilidad es el `SKILL.md`, los `paso_` son sus piezas.

**R8. FUNCIONA EN CUALQUIER COMPUTADORA.** Solo openpyxl, python-docx y matplotlib.
Ninguna libreria opcional puede cambiar el resultado: la estadistica esta escrita a
mano con la biblioteca estandar, y las pruebas de azar usan una semilla fija. Dos
docentes con los mismos datos obtienen la misma huella.

**R9. NO SE TOCA LA ENTRADA.** La `BASE_DATOS_DEPURADA` queda intacta. Todo lo que
produce esta etapa son archivos nuevos.

---

## Ante la duda

| La accion... | ¿Es de esta etapa? |
|---|---|
| cambia un valor de la base | **No.** Etapa 1 o 2 |
| mide, compara o explica | **Si** |
| decide la nota oficial | **No.** La pone el docente |
| dibuja un tablero con filtros | **No.** Etapa 4 |
| guarda una imagen que respalda un hallazgo | **Si** |
| afirma que alguien copio | **No.** Se describe la evidencia y decide el docente |
