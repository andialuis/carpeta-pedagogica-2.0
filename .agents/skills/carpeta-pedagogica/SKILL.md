---
name: carpeta-pedagogica
description: >-
  Sistema integral de gestión curricular, analítica de aprendizaje (CBL y DUA),
  pipeline de 4 agentes IA, e interoperabilidad con Moodle, Classroom y Teams
  creado por Luis Alfredo Andia Valverde. Usalo cuando el docente o usuario pida:
  (1) Iniciar la app web o verificar su estado, (2) Ejecutar el pipeline de 4
  agentes en una materia (Etapas 1 a 4), (3) Generar el PDC o Dossier Oficial en
  Word, (4) Exportar planillas de retroalimentación formativa DUA para Moodle,
  Classroom o Teams, (5) Analizar la Zona de Desarrollo Próximo (Vygotsky) o
  Autodeterminación (Deci & Ryan), o (6) Consultar el manual pedagógico y
  términos de uso libre no comercial.
---

# 🎓 Habilidad: Carpeta Pedagógica 2.0 (v1.0 Personal & Educational)

**Creador y Autor Principal:** **Luis Alfredo Andia Valverde** ([`luis.andia.valverde@gmail.com`](mailto:luis.andia.valverde@gmail.com))  
**Licencia:** Creative Commons Atribución-NoComercial 4.0 Internacional (**CC BY-NC 4.0**).  
**Ubicación de la App Web:** `C:\Users\RcRd.03\Desktop\Carpeta Pedagógica 2.0`  

Esta habilidad dota al agente de Antigravity del conocimiento, automatizaciones y scripts ejecutables para gestionar cursos universitarios y escolares bajo los marcos de **Diseño Curricular por Competencias (CBL)**, **Diseño Universal para el Aprendizaje (DUA - CAST 2024)**, **Zona de Desarrollo Próximo (Vygotsky)** y **Autodeterminación (Deci & Ryan)**.

---

## 🛠️ Herramientas y Scripts Ejecutables Incluidos

Los scripts se encuentran en el subdirectorio `scripts/` de esta habilidad:

| Script | Propósito | Comando de Ejecución |
| :--- | :--- | :--- |
| **`launch_app.py`** | Verifica y arranca el backend FastAPI (`:8000`) y frontend Next.js (`:3001`), abriendo la app web en el navegador. | `python scripts/launch_app.py` |
| **`run_pipeline.py`** | Ejecuta el pipeline analítico de 4 etapas (E1 a E4) para una materia específica. | `python scripts/run_pipeline.py "QUIM101"` |
| **`export_lms.py`** | Exporta la retroalimentación formativa DUA adaptada para Moodle, Classroom o Teams. | `python scripts/export_lms.py "QUIM101" --lms moodle` |
| **`export_dossier.py`**| Compila y descarga el **Dossier Oficial Consolidado (.docx)** del curso. | `python scripts/export_dossier.py "QUIM101"` |

---

## 🧭 Procedimientos de Trabajo para el Agente

### Procedimiento 1: Iniciar o Verificar la App Web
Cuando el docente pida abrir la plataforma, verificar si los servidores están listos o consultar el estado del sistema:
1. Ejecuta:
   ```bash
   python <SKILL>/scripts/launch_app.py
   ```
2. Reporta al docente el estado del backend (`http://127.0.0.1:8000`), del frontend (`http://localhost:3001`), el número de materias activas y que el sistema opera en el **Nivel Gratuito de Google AI Studio ($0.00 USD)**.

### Procedimiento 2: Ejecutar el Pipeline de Analítica de una Materia
Cuando el docente proporcione una nueva planilla o pida procesar un curso:
1. Asegúrate de que la carpeta de la materia exista en `uploads/` dentro de `C:\Users\RcRd.03\Desktop\Carpeta Pedagógica 2.0\uploads\`.
2. Ejecuta el pipeline completo:
   ```bash
   python <SKILL>/scripts/run_pipeline.py "NOMBRE_MATERIA"
   ```
3. El pipeline generará en `uploads/NOMBRE_MATERIA-REV/`:
   - `BASE_INTEGRADA.xlsx` (Etapa 1: Ingesta limpia).
   - `llave_nombres.json` y `BASE_LIMPIA_ANONIMIZADA.xlsx` (Etapa 2: Anonimización criptográfica).
   - `insights.json` (Etapa 3: Inferencia estadística, asimetría de Fisher, curtosis, ZDP y Decy-Ryan).

### Procedimiento 3: Diagnóstico ZDP (Vygotsky) y Teoría de Autodeterminación
Cuando el docente pregunte por el estado de sus estudiantes o el diagnóstico cualitativo:
1. Lee `insights.json` de la materia correspondiente.
2. **Diagnóstico ZDP (Vygotsky):**
   - **NUNCA** respondas solo con números agregados. **Identifica nominalmente** a los alumnos usando `llave_nombres.json` o `estudiantes.nombre_real`:
     - **🔴 Andamiaje Urgente:** Lista los estudiantes con prerrequisitos no cubiertos y su estrategia de micro-quizzes de nivelación.
     - **🔵 Potencial Oculto (ZDP Activa):** Lista los estudiantes cuyo sudor intelectual o asistencia supera sus notas escritas, recomendando adaptaciones DUA (Principio 3: Acción y Expresión).
     - **🟡 Confort Digital / Outsourcing:** Lista casos con notas atípicamente altas sin iteración y prescribe la **Guía de Triangulación Socrática** (entrevista dialógica de 5 minutos).
     - **🟢 Maestría:** Lista estudiantes autónomos preparados para mentoría de pares.
3. **Teoría de Autodeterminación (Deci & Ryan):**
   - Explica siempre los 3 ejes: **Autonomía** (flexibilizar consignas si es baja), **Competencia** (micro-metas si es baja) y **Relación** (aprendizaje cooperativo si es baja).

### Procedimiento 4: Exportación Masiva para LMS (Moodle, Classroom, Teams)
Cuando el docente solicite vincular, exportar notas o entregar devoluciones en su plataforma institucional:
1. Para **Moodle LMS**:
   ```bash
   python <SKILL>/scripts/export_lms.py "NOMBRE_MATERIA" --lms moodle
   ```
   *Explícale que el CSV generado se reimporta en Moodle en Calificaciones > Importar > Archivo CSV, mapeando `Número de ID` y `Comentarios de retroalimentación`.*
2. Para **Google Classroom**:
   ```bash
   python <SKILL>/scripts/export_lms.py "NOMBRE_MATERIA" --lms classroom
   ```
3. Para **Microsoft Teams**:
   ```bash
   python <SKILL>/scripts/export_lms.py "NOMBRE_MATERIA" --lms teams
   ```

### Procedimiento 5: Compilación de Documentos Oficiales
- Para compilar el **Dossier Consolidado (.docx)**:
  ```bash
  python <SKILL>/scripts/export_dossier.py "NOMBRE_MATERIA"
  ```

---

## 📚 Documentación de Referencia Adicional
Para consultar especificaciones técnicas detalladas sin saturar el contexto principal:
- [Flujo de Trabajo en 6 Fases](references/flujo_6_pasos.md)
- [Fundamentación Pedagógica Humanista](references/marco_pedagogico.md)
- [Formatos e Interoperabilidad LMS](references/conectores_lms.md)
