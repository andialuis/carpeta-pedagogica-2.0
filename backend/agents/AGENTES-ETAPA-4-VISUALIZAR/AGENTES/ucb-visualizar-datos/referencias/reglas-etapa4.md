# Las nueve restricciones de la Etapa 4

**R1. ESTA ETAPA MUESTRA, NO ANALIZA.** No se calcula ni una cifra nueva, no se sacan
conclusiones propias y no se reordena a nadie con un criterio del programa. Si falta
un numero para armar algo, no se deduce: se dice que hay que pedirselo a la Etapa 3.

**R2. EL TABLERO Y EL INFORME DICEN LO MISMO.** Si una cifra no coincide, el programa
se detiene y avisa. Un tablero que contradice al informe delante de una reunion es
peor que no tener tablero: a partir de ahi nadie cree a ninguno de los dos.

**R3. NO SE ROMPE EL ANONIMATO.** Solo codigos, nunca nombres ni correos. Y la tabla
de equivalencia no entra en el HTML, ni siquiera oculta en el codigo: este archivo se
comparte y se proyecta.

**R4. DESCRIBIR, NO ACUSAR.** Si el analisis trae un caso delicado, se muestra con su
codigo y sus cifras, etiquetado como algo que requiere revision. La conclusion sobre
una persona la toma el docente.

**R5. NO SE INVENTA PARA LLENAR.** El tablero muestra exactamente lo que produjo el
analisis. Si una pestaña queda corta, se escribe cuanto trajo el analisis en vez de
rellenar con graficos decorativos.

**R6. EL PROGRAMA NO LLEVA DATOS ADENTRO.** Ni la metrica que se pidio destacar, ni
rutas, ni cifras, ni nombres. Todo entra en cada ejecucion. Se comprueba con un
`grep` sobre `scripts/`, y el instalador lo verifica por su cuenta.

**R7. UN SOLO PROGRAMA.** Un unico punto de entrada, `visualizar.py`, con cada paso en
su propio modulo con el prefijo `paso_`.

**R8. FUNCIONA EN CUALQUIER COMPUTADORA.** La unica libreria es openpyxl, para leer el
Excel. El HTML lo escribe el propio programa y los graficos son SVG generado a mano.
Nada se pide a internet: en una sala con mal wifi, un tablero que depende de la red
se abre en blanco justo cuando se lo esta presentando.

**R9. NO SE TOCA LA ENTRADA.** El Excel del analisis, el informe y la base depurada
quedan intactos. Lo que se produce es un archivo nuevo.

---

## Ante la duda

| La accion... | ¿Es de esta etapa? |
|---|---|
| produce una cifra que no estaba | **No.** Etapa 3 |
| cambia como se ve una cifra que ya estaba | **Si** |
| reordena la lista de estudiantes | **No.** El orden sale de PRIORIDADES |
| agrega o reescribe una accion | **No.** Las escribe la Etapa 3 |
| mejora la legibilidad proyectada | **Si** |
| agrega un grafico que no respalda nada | **No.** R5 |
