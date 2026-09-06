# Interoperabilidad con Plataformas LMS — Carpeta Pedagógica 2.0

Especificaciones de intercambio de datos tabulares formuladas por Luis Alfredo Andia Valverde.

## 1. Moodle LMS (Gradebook Import / Export)
- **Ingesta:** Compatible con el reporte del Calificador de Moodle descargado en CSV o Excel.
- **Exportación masiva:** Genera archivo CSV codificado en UTF-8 con marca de orden de bytes (BOM).
- **Columnas obligatorias:**
  - `Número de ID`: Identificador único del estudiante en la universidad/colegio.
  - `Calificación`: Nota numérica sugerida o ajustada.
  - `Comentarios de retroalimentación`: Observaciones cualitativas personalizadas basadas en el marco DUA (Compromiso, Expresión e Instrumento recomendado).
- **Procedimiento de reimportación:**
  1. En el curso de Moodle: *Calificaciones > Importar > Archivo CSV*.
  2. Subir el archivo descargado desde la app.
  3. Mapear `Número de ID` con el ID del estudiante y `Comentarios de retroalimentación`.
  4. Clic en *Subir calificaciones*.

## 2. Google Classroom
- **Ingesta:** Compatible con el archivo CSV generado al hacer clic en el icono de engranaje ⚙ > *Descargar todas las calificaciones como CSV*.
- **Exportación masiva:** Planilla CSV con nombres, apellidos, correos institucionales y comentarios formativos estructurados para pegado o sincronización con Google Sheets.

## 3. Microsoft Teams (Educación)
- **Ingesta:** Compatible con el libro de trabajo `Grades.xlsx` descargado de la pestaña *Notas / Asignaciones*.
- **Exportación masiva:** Genera un archivo Excel (`.xlsx`) estructurado para sincronización en Teams Assignments.
