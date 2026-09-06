# Diagnostico — que hacer cuando algo falla

## El programa se detiene

| Mensaje | Causa | Solucion |
|---|---|---|
| `openpyxl : NO INSTALADO` | Falta una dependencia | `pip install openpyxl python-docx` |
| `no se encontro 'BASE_INTEGRADA*.xlsx'` | La Etapa 1 no se corrio, o `--raiz` esta mal | `--raiz` es la carpeta que **contiene** a la de la materia. Si el nombre tiene espacios, va entre comillas. |
| `el archivo no tiene una hoja BASE` | El archivo elegido no salio de la Etapa 1 | Comprueba que estas apuntando al `BASE_INTEGRADA.xlsx` correcto |

## El resultado se ve raro

**`La cuenta cierra: NO`.** Es lo mas grave que puede pasar. Significa que activos +
abandonos no da el total de entrada. No sigas: reporta el numero exacto.

**Aparecen muchos abandonos.** Mira la tabla D del modo `--proponer` antes de
aprobar. Cada propuesta explica que señales coincidieron. Si el curso tuvo un
periodo sin clases, la señal de asistencia puede confundirse: usa
`abandonos_excluidos` para vetar los casos que el docente sabe que siguieron.

**No se convirtio ninguna escala.** Revisa la hoja `REGLAS_EVALUACION` de la
entrada. Si la columna `observacion` trae un aviso, la regla **no se aplica a
proposito**: la Etapa 1 detecto un conflicto que nadie resolvio todavia.

**Una columna de fechas quedo anonimizada.** No deberia pasar: el programa descarta
fechas antes de considerar una columna como nombre. Si ocurre, reporta el nombre de
esa columna y un valor de ejemplo.

**La verificacion avisa de un cambio de sentido.** Es exactamente para lo que
existe. Mira la hoja `VERIFICACION`: dice que dos columnas iban juntas antes de
depurar y van al reves despues. Casi siempre es una conversion de escala mal
aplicada.

**El informe no se genero.** Falta `python-docx`. El Excel si se genero: solo falta
el documento de lectura.

## Windows

Usa `python` en lugar de `python3`, y barras invertidas en las rutas:

```bash
python AGENTES\ucb-procesar-datos\scripts\procesar.py "NOMBRE_CARPETA" --raiz "." --proponer
```

## Volver a ejecutar

Es seguro: la entrada nunca se modifica. Para partir limpio, borra
`BASE_DATOS_DEPURADA.xlsx` y `EQUIVALENCIA_CODIGOS.xlsx` antes de correr de nuevo.
