# Flujo de Trabajo en 6 Fases — Carpeta Pedagógica 2.0

Diseñado por Luis Alfredo Andia Valverde para ordenar la labor docente en una secuencia lógica y humanista.

## Fase 1: Crear Clase & Ingesta Documental (`/` y `/materias/nueva`)
- Carga de planillas Excel o CSV con selector de origen (Excel Estándar, Moodle, Classroom, Teams).
- Validación *Human-in-the-loop*: la IA sugiere el mapeo de columnas (nombres, notas, asistencia) y el docente autoriza antes de modificar la estructura física.

## Fase 2: Planificación Curricular & PDC (`/planificacion`)
- Formulación de unidades temáticas y criterios por competencias (CBL).
- Generación y edición del Plan de Desarrollo Curricular adaptado a la institución.

## Fase 3: Organizar Expedientes (`/organizar`)
- Supervisión del árbol de directorios en disco local (`uploads/`).
- Comparación entre la versión base cruda y la versión integrada (`-REV`).
- Verificación del manifiesto de materia y checklist de integridad.

## Fase 4: Flujo de Agentes IA (`/agents`)
- **Etapa 1:** Ingesta y consolidación en `BASE_INTEGRADA.xlsx`.
- **Etapa 2:** Anonimización criptográfica soberana (`llave_nombres.json` y `BASE_LIMPIA_ANONIMIZADA.xlsx`).
- **Etapa 3:** Inferencia estadística (asimetría Fisher, curtosis, ZDP Vygotsky, Decy & Ryan) y diagnóstico cualitativo con Gemini (`insights.json`).
- **Etapa 4:** Generación de métricas para el tablero analítico interactivo.

## Fase 5: Tablero de Control (`/analytics`)
- Curva de distribución normal (Gauss) de calificaciones.
- Correlación de notas vs. asistencia/proceso.
- Radar de Autodeterminación (Deci & Ryan) con guía interpretativa para el maestro.
- Diagnóstico ZDP (Vygotsky) con identificación nominal de estudiantes que requieren andamiaje o poseen potencial latente.
- Generador del Diagnóstico Ejecutivo IA para jefaturas y coordinaciones.

## Fase 6: Evaluación Formativa, DUA & Dossier (`/evaluacion`)
- Generador de rúbricas analíticas CBL por niveles descargables en Word (`.docx`).
- Matriz DUA (marco CAST 2024) con botón `✨ Sugerir con IA`.
- Protocolo anti-outsourcing cognitivo: Guía de Triangulación Socrática (entrevista verbal de 5 minutos).
- Descarga en un clic del **Dossier Oficial Consolidado (.docx)**.
