# 🎓 Carpeta Pedagógica 2.0 — Versión 1.0 (Personal & Educational Edition)

> **Sistema Humanista de Gestión Curricular, Analítica de Aprendizaje (CBL & DUA) e Interoperabilidad con Plataformas Educativas.**

[![Licencia: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/legalcode.es)
[![Autor: Luis Alfredo Andia Valverde](https://img.shields.io/badge/Autor-Luis%20Alfredo%20Andia%20Valverde-indigo.svg)](mailto:luis.andia.valverde@gmail.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/Frontend-Next.js%2016%20%2B%20Tailwind-black.svg)](https://nextjs.org/)
[![Google Gemini](https://img.shields.io/badge/IA%20Studio-Gemini%20Flash%20(Free%20Tier)-orange.svg)](https://aistudio.google.com/)

---

## 👨‍🏫 Autoría, Créditos & Licencia
* **Creador y Autor Principal:** **Luis Alfredo Andia Valverde**  
* **Correo de Contacto / Soporte:** [`luis.andia.valverde@gmail.com`](mailto:luis.andia.valverde@gmail.com)  
* **Términos de Licenciamiento:** Distribuido bajo licencia **Creative Commons Atribución-NoComercial 4.0 Internacional (CC BY-NC 4.0)**.
  * ✅ **Permitido:** Copiar, compartir, redistribuir, modificar, adaptar y ejecutar el software en cualquier institución educativa o entorno personal.
  * ❌ **Prohibido:** Cobro por suscripción, venta directa, comercialización o explotación lucrativa del software o sus derivados.
  * 📝 **Atribución Requerida:** Toda copia o adaptación debe mantener visible la autoría de **Luis Alfredo Andia Valverde**.

---

## 🌟 Características Principales

### 1. Secuencia Pedagógica en 6 Fases (Flujo de Trabajo Natural)
1. **Paso 1: Crear Clase (`/`):** Ingesta documental de planillas Excel/CSV con selector de origen LMS y validación *Human-in-the-loop*.
2. **Paso 2: Planificar (`/planificacion`):** Plan de Desarrollo Curricular (PDC), unidades didácticas y competencias CBL.
3. **Paso 3: Organizar (`/organizar`):** Gestión física de expedientes, manifiestos y estructura de carpetas `-REV`.
4. **Paso 4: Flujo de Agentes (`/agents`):** Pipeline metodológico de 4 etapas (Limpieza, Anonimización criptográfica, Inferencia estadística con IA y Visualización).
5. **Paso 5: Tablero de Control (`/analytics`):** Distribución gaussiana, radar de autodeterminación (Deci & Ryan), diagnóstico ZDP (Vygotsky) y **Diagnóstico Ejecutivo IA**.
6. **Paso 6: Evaluación (`/evaluacion`):** Rúbricas analíticas en Word (`.docx`), matriz DUA (CAST 2024), protocolo anti-outsourcing cognitivo y compilación del **Dossier Oficial Consolidado (.docx)**.

### 2. Interoperabilidad Nativa con Plataformas LMS
* **🟠 Moodle LMS:** Exporta archivos CSV codificados en UTF-8 con BOM estructurados con `Número de ID`, `Calificación` y `Comentarios de retroalimentación` (sugerencias DUA) para **reimportación directa en el Calificador de Moodle**.
* **🟢 Google Classroom:** Exporta planillas CSV estructuradas con correos institucionales para sincronización masiva de devoluciones formativas.
* **🟣 Microsoft Teams:** Genera libros Excel (`.xlsx`) compatibles con la pestaña *Notas / Asignaciones* de Teams Educación.

### 3. Ética y Privacidad Soberana (Local-First)
* **Sin almacenamiento de contraseñas:** No requiere tokens OAuth institucionales ni contraseñas universitarias que comprometan la seguridad del campus.
* **Anonimización Criptográfica:** Los datos de los estudiantes se procesan con hashes locales en la máquina del usuario antes de cualquier consulta a modelos de IA.
* **Costo Cero ($0.00 USD):** Diseñado para operar bajo la cuota libre (*Free Tier*) de Google AI Studio (Gemini 3.5 Flash-Lite / 3.6 Flash), con salvaguarda determinista local ante congestión.

---

## 🚀 Requisitos e Instalación Rápida

### Requisitos Previos:
* [Python 3.10+](https://www.python.org/downloads/) (con pip)
* [Node.js 18+](https://nodejs.org/) (con npm)

### Puesta en Marcha en 2 Pasos (Windows):
1. **Instalar dependencias (solo la primera vez):**
   Haz doble clic en el archivo:
   ```cmd
   Instalar_Dependencias.bat
   ```
2. **Iniciar la aplicación:**
   Haz doble clic en:
   ```cmd
   Iniciar_Carpeta.bat
   ```
   *Se levantará automáticamente el backend en `http://localhost:8000`, el frontend en `http://localhost:3001` y se abrirá tu navegador predeterminado.*

---

## 📦 ¿Cómo Compartir y Distribuir el Código?

Al tratarse de una versión consolidada para **uso libre no comercial**, existen 3 métodos recomendados para distribuirla a colegas y comunidades académicas:

### Opción 1: Repositorio en GitHub / GitLab (Recomendado para la Comunidad Docente)
1. **Inicializar Git y hacer el primer commit:**
   ```bash
   git init
   git add .
   git commit -m "feat: Lanzamiento Carpeta Pedagógica 2.0 v1.0 (Personal & Educational Edition)"
   ```
2. **Subir a tu cuenta de GitHub:**
   Crea un repositorio público llamado `carpeta-pedagogica-2.0` y conéctalo:
   ```bash
   git remote add origin https://github.com/tu-usuario/carpeta-pedagogica-2.0.git
   git branch -M main
   git push -u origin main
   ```
   *El archivo `.gitignore` incluido ya previene que se suban carpetas pesadas (`node_modules`, `venv`) o claves privadas.*

### Opción 2: Paquete ZIP "Listo para Usar" (Para Colegas sin Git)
1. Comprime toda la carpeta del proyecto en un archivo `Carpeta_Pedagogica_2.0.zip` (asegúrate de que no incluya `node_modules` ni `venv` para que pese menos de 15 MB).
2. Compártelo por Google Drive, OneDrive o memoria USB.
3. El colega solo debe descomprimir y hacer doble clic en `Instalar_Dependencias.bat` y luego en `Iniciar_Carpeta.bat`.

### Opción 3: Registro Académico Permanente con Zenodo / DOI (Para Citación Científica)
Si publicas el código en GitHub, puedes vincularlo con [Zenodo](https://zenodo.org/) (repositorio abierto del CERN). Zenodo asignará un **DOI permanente** (ej. `10.5281/zenodo.XXXXXXX`), permitiendo que otros investigadores y docentes citen formalmente tu software en artículos científicos, ponencias y tesis universitarias.

---

## 🤖 Habilidad Oficial para Google Antigravity (AGY Skill)

El repositorio incluye la habilidad nativa `carpeta-pedagogica` lista para interactuar con agentes de Inteligencia Artificial en **Google Antigravity**:

### ¿Cómo funciona al compartir el código?
1. **Detección Automática (Zero-Config):**
   * Antigravity lee por defecto la carpeta `.agents/skills/` en la raíz de cualquier proyecto que abras.
   * Cualquier docente o colega que clone este repositorio y abra Antigravity tendrá la habilidad **inmediatamente activa**, sin necesidad de configurar nada. Su agente de IA sabrá operar la plataforma, ejecutar el pipeline y generar diagnósticos.
2. **Instalación Global en el Sistema:**
   * Si el usuario desea que la habilidad esté disponible en **cualquier carpeta de su computadora** (incluso fuera de este proyecto), solo debe hacer doble clic en:
     ```cmd
     Instalar_Habilidad_Antigravity.bat
     ```
   * Esto copiará la habilidad a su configuración global de Antigravity (`~/.gemini/config/skills/carpeta-pedagogica`).
3. **Uso Soberano sin IA:**
   * Los scripts en `.agents/skills/carpeta-pedagogica/scripts/` son programas Python 100% estándar (`launch_app.py`, `run_pipeline.py`, `export_lms.py`, `export_dossier.py`). Funcionan desde cualquier consola sin necesidad de tener Antigravity.

---

## 📄 Estructura del Proyecto

```text
Carpeta Pedagógica 2.0/
├── .agents/                          # Habilidad nativa para Google Antigravity
│   └── skills/carpeta-pedagogica/    # Manifiesto SKILL.md, scripts y referencias
│       ├── SKILL.md                  # Especificación formal de la habilidad
│       ├── scripts/                  # Scripts ejecutables autónomos en Python
│       │   ├── launch_app.py         # Diagnóstico y arranque de servicios
│       │   ├── run_pipeline.py       # Ejecución por lotes del pipeline de 4 etapas
│       │   ├── export_lms.py         # Generación de planillas Moodle/Classroom/Teams
│       │   └── export_dossier.py     # Compilación del Dossier Oficial en Word
│       └── references/               # Guías pedagógicas, flujo y conectores LMS
├── backend/                          # Servidor de analítica y APIs (FastAPI)
│   ├── main.py                       # Endpoints, conectores LMS y pipeline
│   ├── ai_service.py                 # Conexión con Google Gemini API
│   ├── instruments.py                # Generador de Word (.docx) y rúbricas
│   └── requirements.txt              # Librerías Python
├── frontend/                         # Interfaz de usuario (Next.js 16 + Tailwind)
│   ├── src/app/                      # Páginas del flujo de 6 pasos
│   │   ├── page.tsx                  # Paso 1: Crear Clase e Ingesta compacta
│   │   ├── planificacion/            # Paso 2: Plan Curricular & PDC
│   │   ├── organizar/                # Paso 3: Expedientes REV y archivos
│   │   ├── agents/                   # Paso 4: Pipeline de 4 etapas
│   │   ├── analytics/                # Paso 5: Tablero Gauss, ZDP y Deci & Ryan
│   │   ├── evaluacion/               # Paso 6: Rúbricas CBL y Matriz DUA
│   │   ├── perfil/                   # Perfil docente del autor
│   │   ├── administracion/           # Monitor, Backup ZIP y Centro LMS
│   │   └── documentacion/            # Manual de uso y marco didáctico
│   └── package.json                  # Dependencias Node.js
├── uploads/                          # Expedientes locales soberanos de materias
├── Iniciar_Carpeta.bat               # Script de arranque en un clic
├── Instalar_Dependencias.bat         # Script instalador de librerías
├── Instalar_Habilidad_Antigravity.bat # Instalador de habilidad global AGY
├── LICENSE                           # Licencia CC BY-NC 4.0 (Luis Alfredo Andia Valverde)
├── .gitignore                        # Reglas de exclusión para Git
└── README.md                         # Documentación general del repositorio
```

---

## 📬 Contacto y Soporte
Para consultas pedagógicas, adaptaciones institucionales o retroalimentación formativa:
* **Luis Alfredo Andia Valverde**
* 📧 Email: [`luis.andia.valverde@gmail.com`](mailto:luis.andia.valverde@gmail.com)
* Licencia: Creative Commons Atribución-NoComercial 4.0 Internacional (CC BY-NC 4.0).
