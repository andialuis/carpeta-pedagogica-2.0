# Cuando algo falla o el tablero se ve raro

## El programa no arranca

**`No se encontro RESULTADOS_ANALISIS*.xlsx`**
La Etapa 3 no termino, o la carpeta tiene otro nombre. El nombre que se le pasa al
programa es el de la materia **sin** el `-REV`.

**`falta la hoja HALLAZGOS / ACCIONES / PRIORIDADES`**
El analisis quedo incompleto. Sin esas tres no hay tablero posible: vuelva a la
Etapa 3.

**`Falta la unica libreria obligatoria`**
Ejecute el comando exacto que imprime el mensaje. Es una sola: openpyxl.

## El tablero se ve raro

**«Una pestaña se ve pobre».**
Primero mire la tabla A del modo `--plan`: dice cuanto trajo el analisis. Si el
analisis entrego tres hallazgos, la pestaña tendra tres. El programa no rellena con
adornos a proposito.

**«El equilibrio dice REVISAR».**
El programa mide cuanta pantalla ocupa el grafico y cuanta el texto. Si sobra texto,
la solucion no es borrar informacion: es convertir alguna cifra en barra o en
tarjeta con numero grande. Si sobra grafico, hay adornos que no dicen nada.

**«La cifra destacada no es la que pedi».**
El programa busca lo pedido entre las hojas del analisis. Si no lo encuentra, lo
dice en la propia pantalla y muestra el numero de hallazgos. Pruebe a pedirlo con
las palabras que usa el analisis: mire la hoja INDICADORES.

**«Aparecen nombres de columna raros».**
El programa limpia los prefijos entre corchetes que dejan las etapas anteriores. Si
alguno se le escapa, agregue el reemplazo en `config.json`, en
`limpieza_de_titulos`.

**«El tablero no se guardo».**
Es deliberado: alguna de las cuatro comprobaciones fallo y el programa prefiere no
entregar un tablero que contradiga al informe. El mensaje dice cual fallo.

## Comprobar que se ve bien proyectado

Abralo, ponga el navegador a pantalla completa y alejese tres metros. Deberia poder
leer la cifra grande, los titulos de las tarjetas y las barras. Si no, el problema
no es la pantalla: es que hay demasiado texto y poca cifra.

## Volver a empezar

Esta etapa no toca nada de la entrada. Se puede ejecutar tantas veces como haga
falta: cada corrida sobrescribe su propio tablero.
