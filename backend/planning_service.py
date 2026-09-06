"""
planning_service.py
Gestor central de Modelos de Planificación Globales y Procesamiento de Planes por Asignatura.
"""
import os
import json
import re
import docx
from docx import Document
from typing import Dict, Any, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_FILE = os.path.join(DATA_DIR, "planning_models.json")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
BASE_UPLOADS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# Megaprompt Maestro para Modelo CBL Modular (INV101 y Educación Superior)
PROMPT_CBL_MODULAR = """PARTE 1: CONSTITUCIÓN DEL ASISTENTE DE DISEÑO CURRICULAR POR COMPETENCIAS (CBL)
Eres el Consejo Académico de Educación Superior, integrado por:
- BRUNER: Arquitecto cognitivo, experto en andamiaje y transferencia conceptual profunda.
- WIGGINS: Auditor de diseño inverso (UbD), asegura evidencias auténticas de desempeño.
- PAPERT: Pionero digital, promueve el uso de IA como copiloto crítico (anti-muleta).
- FREINET: Coach de investigación en el terreno, vinculación con problemáticas reales.

ASIGNATURA / MÓDULO: {{MATERIA}} (Código: {{CODIGO_MODULO}})
DOCENTE: {{DOCENTE}}
PERIODO: {{PERIODO_MODULO}} | DURACIÓN: {{DURACION_HORAS}} | MODALIDAD: {{MODALIDAD}}
PROBLEMA CENTRAL DE LA ASIGNATURA: {{PROBLEMA_CONTEXTO}}
ESTUDIANTES CON ADECUACIÓN CURRICULAR (AC / DUA): {{ESTUDIANTES_AC}}
DATOS DE DIAGNÓSTICO DEL AULA: {{DATOS_DIAGNOSTICO}}

DIRECTIVA DE SALIDA (OBLIGATORIA):
Debes generar la propuesta curricular utilizando ÚNICA Y EXCLUSIVAMENTE este formato de etiquetas delimitadas. No inventes otras etiquetas.
Cada sección debe ser rigurosa, profunda y adaptada a la educación superior y formación científica:

[INICIO:CODIGO_MODULO] {{CODIGO_MODULO}} [FIN:CODIGO_MODULO]
[INICIO:NOMBRE_MODULO] {{MATERIA}} [FIN:NOMBRE_MODULO]
[INICIO:DOCENTE] {{DOCENTE}} [FIN:DOCENTE]
[INICIO:DURACION_HORAS] {{DURACION_HORAS}} [FIN:DURACION_HORAS]
[INICIO:PERIODO_MODULO] {{PERIODO_MODULO}} [FIN:PERIODO_MODULO]
[INICIO:MODALIDAD] {{MODALIDAD}} [FIN:MODALIDAD]
[INICIO:PROBLEMA_CONTEXTO] [Descripción del problema del contexto real a abordar] [FIN:PROBLEMA_CONTEXTO]
[INICIO:COMPETENCIA_GLOBAL] [Redacción de la competencia en formato verbo de desempeño + objeto + finalidad + condición de calidad] [FIN:COMPETENCIA_GLOBAL]

(FASE 1 - SEMANA 1)
[INICIO:FASE_1_TITULO] [Título de la Fase 1] [FIN:FASE_1_TITULO]
[INICIO:FASE_1_SABER] [Saberes conceptuales y teóricos] [FIN:FASE_1_SABER]
[INICIO:FASE_1_HACER] [Procedimientos, técnicas y actividades prácticas] [FIN:FASE_1_HACER]
[INICIO:FASE_1_SER] [Valores éticos, responsabilidad epistémica y trabajo colaborativo] [FIN:FASE_1_SER]
[INICIO:FASE_1_SUDOR_INTELECTUAL] [Evidencia del proceso de pensamiento propio: bitácora, iteraciones, diálogo reflexivo] [FIN:FASE_1_SUDOR_INTELECTUAL]
[INICIO:FASE_1_CRITERIO_EVAL] [Criterios de evaluación y nivel de dominio esperado] [FIN:FASE_1_CRITERIO_EVAL]

(FASE 2 - SEMANA 2)
[INICIO:FASE_2_TITULO] [Título de la Fase 2] [FIN:FASE_2_TITULO]
[INICIO:FASE_2_SABER] [Saberes conceptuales] [FIN:FASE_2_SABER]
[INICIO:FASE_2_HACER] [Hacer metodológico] [FIN:FASE_2_HACER]
[INICIO:FASE_2_SER] [Ser y actuar con ética] [FIN:FASE_2_SER]
[INICIO:FASE_2_SUDOR_INTELECTUAL] [Esfuerzo reflexivo y resolución de problemas] [FIN:FASE_2_SUDOR_INTELECTUAL]
[INICIO:FASE_2_CRITERIO_EVAL] [Criterio de evaluación] [FIN:FASE_2_CRITERIO_EVAL]

(FASE 3 - SEMANA 3)
[INICIO:FASE_3_TITULO] [Título de la Fase 3] [FIN:FASE_3_TITULO]
[INICIO:FASE_3_SABER] [Saberes conceptuales avanzados] [FIN:FASE_3_SABER]
[INICIO:FASE_3_HACER] [Análisis de datos, redacción crítica o contrastación empírica] [FIN:FASE_3_HACER]
[INICIO:FASE_3_SER] [Pensamiento crítico ante sesgos y alucinaciones de IA] [FIN:FASE_3_SER]
[INICIO:FASE_3_SUDOR_INTELECTUAL] [Músculo intelectual y autoría auténtica] [FIN:FASE_3_SUDOR_INTELECTUAL]
[INICIO:FASE_3_CRITERIO_EVAL] [Criterio de evaluación] [FIN:FASE_3_CRITERIO_EVAL]

(FASE 4 - SEMANA 4)
[INICIO:FASE_4_TITULO] [Título de la Fase 4: Integración y Comunicación] [FIN:FASE_4_TITULO]
[INICIO:FASE_4_SABER] [Síntesis conceptual y metateoría] [FIN:FASE_4_SABER]
[INICIO:FASE_4_HACER] [Defensa oral, presentación científica y divulgación] [FIN:FASE_4_HACER]
[INICIO:FASE_4_SER] [Compromiso con el impacto social del conocimiento] [FIN:FASE_4_SER]
[INICIO:FASE_4_SUDOR_INTELECTUAL] [Defensa argumentada del proceso de construcción] [FIN:FASE_4_SUDOR_INTELECTUAL]
[INICIO:FASE_4_CRITERIO_EVAL] [Criterio de evaluación de maestría] [FIN:FASE_4_CRITERIO_EVAL]

[INICIO:ADAPTACIONES_DUA_INCLUSION] [Formatos múltiples de representación, expresión y andamiaje para estudiantes con AC o ritmos diferenciados] [FIN:ADAPTACIONES_DUA_INCLUSION]
[INICIO:ESTRATEGIA_ANTI_OUTSOURCING] [Estrategia de Triangulación Socrática y re-evaluación oral para estudiantes con trabajos sospechosamente perfectos] [FIN:ESTRATEGIA_ANTI_OUTSOURCING]
[INICIO:PRODUCTO_FINAL_MODULAR] [Perfil o artículo de investigación / informe técnico auténtico] [FIN:PRODUCTO_FINAL_MODULAR]
"""

# Google Apps Script para el Modelo CBL Modular
APPS_SCRIPT_CBL = """/**
 * MOTOR DE INYECCIÓN MODULAR CBL (Google Apps Script)
 * Procesa borradores estructurados y los inyecta en la Plantilla CBL Modular.
 */
function procesarCBL_Modular() {
  const ID_CARPETA_ENTRADA = "{{ID_CARPETA_ENTRADA}}";
  const ID_CARPETA_SALIDA  = "{{ID_CARPETA_SALIDA}}";
  const ID_PLANTILLA_DOC   = "{{ID_PLANTILLA_DOC}}";

  const carpetaEntrada = DriveApp.getFolderById(ID_CARPETA_ENTRADA);
  const carpetaSalida  = DriveApp.getFolderById(ID_CARPETA_SALIDA);
  const plantilla      = DriveApp.getFileById(ID_PLANTILLA_DOC);

  const archivos = carpetaEntrada.getFilesByType(MimeType.GOOGLE_DOCS);
  while (archivos.hasNext()) {
    let archivoBorrador = archivos.next();
    let nombreOrig = archivoBorrador.getName();
    if (nombreOrig.endsWith("_PROCESADO") || nombreOrig.startsWith("PLAN_")) continue;

    let docOrigen = DocumentApp.openById(archivoBorrador.getId());
    let texto = docOrigen.getBody().getText();
    let mapa = mapearEtiquetas(texto);

    let codigo = mapa["CODIGO_MODULO"] || "MOD";
    let docente = mapa["DOCENTE"] ? mapa["DOCENTE"].split(" ")[0] : "Docente";
    let nombreFinal = `PLAN_${codigo}_${docente}_${Utilities.formatDate(new Date(), "GMT-4", "yyyyMMdd")}`;

    let nuevoDoc = plantilla.makeCopy(nombreFinal, carpetaSalida);
    let docFinal = DocumentApp.openById(nuevoDoc.getId());
    let cuerpo = docFinal.getBody();

    Object.keys(mapa).forEach(tag => {
      let valor = mapa[tag];
      if (valor) {
        cuerpo.replaceText(`\\[\\[${tag}\\]\\]`, valor);
        cuerpo.replaceText(`\\[${tag}\\]`, valor);
      }
    });

    docFinal.saveAndClose();
    archivoBorrador.setName(nombreOrig + "_PROCESADO");
  }
}

function mapearEtiquetas(texto) {
  let mapa = {};
  let regex = /\\[INICIO:\\s*([^\\]]+?)\\s*\\]([\\s\\S]*?)\\[FIN:\\s*\\1\\s*\\]/gi;
  let match;
  while ((match = regex.exec(texto)) !== null) {
    mapa[match[1].trim().toUpperCase()] = match[2].trim();
  }
  return mapa;
}
"""

# Modelos Iniciales Preconfigurados
DEFAULT_MODELS = [
    {
        "id": "cbl_modular_inv101",
        "name": "Planificación por Competencias Modular (CBL - INV101)",
        "description": "Modelo de Educación Superior y Formación Científica estructurado en 4 fases de hitos con dimensiones Saber, Hacer, Ser, Sudor Intelectual y DUA.",
        "system": "superior",
        "drive_config": {
            "input_folder": "https://drive.google.com/drive/folders/1g2QRr1X-Zp2oeSeXDlu-mqZYcYKpxHnW",
            "output_folder": "https://drive.google.com/drive/folders/1jPfFlrbsy8_Mi3XaL8GaGdzHJa_Vun9p",
            "template_id": "Plantilla_CBL_Modular.docx"
        },
        "prompt_template": PROMPT_CBL_MODULAR,
        "script_export": APPS_SCRIPT_CBL,
        "tags_schema": [
            "CODIGO_MODULO", "NOMBRE_MODULO", "DOCENTE", "DURACION_HORAS", "PERIODO_MODULO", "MODALIDAD",
            "PROBLEMA_CONTEXTO", "COMPETENCIA_GLOBAL",
            "FASE_1_TITULO", "FASE_1_SABER", "FASE_1_HACER", "FASE_1_SER", "FASE_1_SUDOR_INTELECTUAL", "FASE_1_CRITERIO_EVAL",
            "FASE_2_TITULO", "FASE_2_SABER", "FASE_2_HACER", "FASE_2_SER", "FASE_2_SUDOR_INTELECTUAL", "FASE_2_CRITERIO_EVAL",
            "FASE_3_TITULO", "FASE_3_SABER", "FASE_3_HACER", "FASE_3_SER", "FASE_3_SUDOR_INTELECTUAL", "FASE_3_CRITERIO_EVAL",
            "FASE_4_TITULO", "FASE_4_SABER", "FASE_4_HACER", "FASE_4_SER", "FASE_4_SUDOR_INTELECTUAL", "FASE_4_CRITERIO_EVAL",
            "ADAPTACIONES_DUA_INCLUSION", "ESTRATEGIA_ANTI_OUTSOURCING", "PRODUCTO_FINAL_MODULAR"
        ]
    },
    {
        "id": "pdc_minedu_2026",
        "name": "Plan de Desarrollo Curricular (PDC Minedu 2026)",
        "description": "Modelo oficial con 4 momentos metodológicos (Práctica, Teoría, Valoración, Producción) y Consejo de Expertos (Dewey, Bruner, Malaguzzi, Wiggins, Papert, Freinet).",
        "system": "regular",
        "drive_config": {
            "input_folder": "https://drive.google.com/drive/folders/1g2QRr1X-Zp2oeSeXDlu-mqZYcYKpxHnW",
            "output_folder": "https://drive.google.com/drive/folders/1jPfFlrbsy8_Mi3XaL8GaGdzHJa_Vun9p",
            "template_id": "1Fzz1XdxdVljRCmSKq_oULj-HcjW9gC9LP3ZhXCCadPo"
        },
        "prompt_template": "PLAN DE DESARROLLO CURRICULAR (PDC) - ENFOQUE MINEDU 2026 & CONSEJO DE EXPERTOS...",
        "script_export": "// procesarPDC_V14 de Google Apps Script",
        "tags_schema": ["NUM_PDC", "MAESTRO", "NIVEL", "AÑO_DE_ESCOLARIDAD", "AREA", "TRIMESTRE", "MES", "1_OBJETIVO", "1_SEMANA_1"]
    }
]

def init_planning_data():
    """Asegura que el directorio data y el archivo de modelos existan."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MODELS_FILE):
        with open(MODELS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_MODELS, f, ensure_ascii=False, indent=2)

def get_planning_models() -> List[Dict[str, Any]]:
    init_planning_data()
    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_MODELS

def get_planning_model(model_id: str) -> Optional[Dict[str, Any]]:
    models = get_planning_models()
    for m in models:
        if m["id"] == model_id:
            return m
    return models[0] if models else None

def save_planning_model(model_data: Dict[str, Any]) -> Dict[str, Any]:
    init_planning_data()
    models = get_planning_models()
    model_id = model_data.get("id")
    if not model_id:
        model_id = "model_" + re.sub(r'[^a-zA-Z0-9_]', '_', model_data.get("name", "custom").lower())
        model_data["id"] = model_id

    found = False
    for i, m in enumerate(models):
        if m["id"] == model_id:
            models[i] = {**m, **model_data}
            found = True
            break
    if not found:
        models.append(model_data)

    with open(MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)
    return model_data

def ensure_subject_planning_dirs(subject_name: str) -> Dict[str, str]:
    """Crea y garantiza la estructura de carpetas locales para la planificación de la materia."""
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()
    rev_name = f"{clean_subj}-REV"
    if not os.path.exists(os.path.join(BASE_UPLOADS, rev_name)) and os.path.exists(BASE_UPLOADS):
        clean_lower = clean_subj.lower()
        for entry in os.listdir(BASE_UPLOADS):
            if entry.endswith("-REV"):
                cand_base = entry[:-4].strip()
                cand_lower = cand_base.lower()
                if cand_lower == clean_lower or cand_lower.startswith(clean_lower + " ") or cand_lower.startswith(clean_lower + "-") or clean_lower in cand_lower:
                    clean_subj = cand_base
                    rev_name = entry
                    break
    subj_plan_dir = os.path.join(BASE_UPLOADS, rev_name, "planificacion")
    
    in_dir = os.path.join(subj_plan_dir, "entrada")
    out_dir = os.path.join(subj_plan_dir, "salida")
    tpl_dir = os.path.join(subj_plan_dir, "plantilla")
    
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tpl_dir, exist_ok=True)

    # Copiar plantilla base si no existe
    dest_tpl = os.path.join(tpl_dir, "Plantilla_CBL_Modular_INV101.docx")
    src_tpl = os.path.join(TEMPLATES_DIR, "Plantilla_CBL_Modular.docx")
    if not os.path.exists(dest_tpl) and os.path.exists(src_tpl):
        import shutil
        shutil.copyfile(src_tpl, dest_tpl)

    return {
        "entrada": in_dir,
        "salida": out_dir,
        "plantilla": tpl_dir,
        "plantilla_file": dest_tpl
    }

def parse_tags_from_text(text: str) -> Dict[str, str]:
    """Extrae las etiquetas [INICIO:TAG]...[FIN:TAG] generadas por el modelo de IA."""
    tags_map = {}
    pattern = re.compile(r'\[INICIO:\s*([^\]]+?)\s*\]([\s\S]*?)\[FIN:\s*\1\s*\]', re.IGNORECASE)
    for match in pattern.finditer(text):
        tag_key = match.group(1).strip().upper()
        content = match.group(2).strip()
        tags_map[tag_key] = content
    return tags_map

def inject_tags_into_docx(template_path: str, tags_map: Dict[str, str], output_path: str) -> str:
    """Inyecta los valores en las etiquetas [[TAG]] y [TAG] dentro del documento Word."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")

    doc = Document(template_path)

    def _replace_in_paragraph(paragraph):
        text = paragraph.text
        if not text or "[" not in text:
            return
        modified = text
        for tag, val in tags_map.items():
            modified = modified.replace(f"[[{tag}]]", val)
            modified = modified.replace(f"[{tag}]", val)
        if modified != text:
            # Preservar estilos asignando el texto completo
            paragraph.text = modified

    # 1. Párrafos generales
    for p in doc.paragraphs:
        _replace_in_paragraph(p)

    # 2. Tablas y celdas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    _replace_in_paragraph(p)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path

def generate_cbl_plan_draft(subject_name: str, params: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """Genera el borrador del plan con Gemini 2.5 Flash o motor determinista."""
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    dirs = ensure_subject_planning_dirs(clean_subj)

    code = params.get("codigo_modulo", "INV101")
    docente = params.get("docente", "Lic. / Dr. Docente Titular")
    periodo = params.get("periodo", "Módulo 1 - 2026")
    horas = params.get("duracion_horas", "80 horas académicas")
    modalidad = params.get("modalidad", "Semipresencial / Aula Invertida")
    problema = params.get("problema_contexto", "Riesgo de outsourcing cognitivo y uso acrítico de IA en formulación de investigaciones.")
    estudiantes_ac = params.get("estudiantes_ac", "Ninguno registrado (Adaptaciones DUA generales aplicadas)")

    # Inyección de variables en el prompt
    prompt = PROMPT_CBL_MODULAR
    prompt = prompt.replace("{{MATERIA}}", clean_subj)
    prompt = prompt.replace("{{CODIGO_MODULO}}", code)
    prompt = prompt.replace("{{DOCENTE}}", docente)
    prompt = prompt.replace("{{PERIODO_MODULO}}", periodo)
    prompt = prompt.replace("{{DURACION_HORAS}}", horas)
    prompt = prompt.replace("{{MODALIDAD}}", modalidad)
    prompt = prompt.replace("{{PROBLEMA_CONTEXTO}}", problema)
    prompt = prompt.replace("{{ESTUDIANTES_AC}}", estudiantes_ac)

    # Extraer diagnóstico real desde insights.json si existe
    insights_path = os.path.join(BASE_UPLOADS, f"{clean_subj}-REV", "bases_de_datos", "insights.json")
    diagnostico_real = f"Asignatura: {clean_subj}."
    if os.path.exists(insights_path):
        try:
            with open(insights_path, "r", encoding="utf-8") as f:
                ins = json.load(f)
                prom = ins.get("promedio_general", 72.0)
                outsourcing = ins.get("outsourcing_count", 0)
                riesgo = ins.get("riesgo_abandono", 0)
                zdp = ins.get("necesidad_andamiaje_vygotsky", "")
                diagnostico_real += f" Promedio del grupo: {prom}/100. Alertas de outsourcing cognitivo: {outsourcing} estudiantes. Casos en riesgo: {riesgo}. ZDP Vygotsky: {zdp}."
        except Exception:
            diagnostico_real += " Diagnóstico: Grupo heterogéneo con necesidad de andamiaje epistemológico."
    else:
        diagnostico_real += " Diagnóstico: Grupo en consolidación de competencias metodológicas."

    prompt = prompt.replace("{{DATOS_DIAGNOSTICO}}", diagnostico_real)

    draft_text = ""
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    motor = gemini_model
    fallback = False

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model=gemini_model,
                contents=prompt
            )
            draft_text = (resp.text or "").strip()
        except Exception as e:
            fallback = True
            print(f"[Planning AI Fallback] Error con {gemini_model}: {e}")

    if not draft_text:
        fallback = True
        motor = "motor_determinista_cbl"
        # Generación determinista estructurada con todas las etiquetas
        draft_text = f"""[INICIO:CODIGO_MODULO] {code} [FIN:CODIGO_MODULO]
[INICIO:NOMBRE_MODULO] {clean_subj} [FIN:NOMBRE_MODULO]
[INICIO:DOCENTE] {docente} [FIN:DOCENTE]
[INICIO:DURACION_HORAS] {horas} [FIN:DURACION_HORAS]
[INICIO:PERIODO_MODULO] {periodo} [FIN:PERIODO_MODULO]
[INICIO:MODALIDAD] {modalidad} [FIN:MODALIDAD]
[INICIO:PROBLEMA_CONTEXTO] {problema} [FIN:PROBLEMA_CONTEXTO]
[INICIO:COMPETENCIA_GLOBAL] Formular problemas de investigación y diseñar proyectos científicos aplicando el rigor metodológico, pensamiento crítico y ética epistémica para dar respuesta a necesidades sociales. [FIN:COMPETENCIA_GLOBAL]

[INICIO:FASE_1_TITULO] Epistemología y Pregunta de Investigación [FIN:FASE_1_TITULO]
[INICIO:FASE_1_SABER] Paradigmas de investigación (cuantitativo, cualitativo y mixto). Estructura del objeto de estudio. [FIN:FASE_1_SABER]
[INICIO:FASE_1_HACER] Delimitación temática y formulación del problema científico mediante mapas conceptuales. [FIN:FASE_1_HACER]
[INICIO:FASE_1_SER] Honestidad intelectual, curiosidad científica y ética en el uso de fuentes bibliográficas. [FIN:FASE_1_SER]
[INICIO:FASE_1_SUDOR_INTELECTUAL] Bitácora de iteración de ideas y contraste entre 5 formulaciones preliminares del problema. [FIN:FASE_1_SUDOR_INTELECTUAL]
[INICIO:FASE_1_CRITERIO_EVAL] Formulación de pregunta de investigación con variables observables y justificación sólida. [FIN:FASE_1_CRITERIO_EVAL]

[INICIO:FASE_2_TITULO] Estado del Arte y Marco Teórico Crítico [FIN:FASE_2_TITULO]
[INICIO:FASE_2_SABER] Búsqueda sistemática en bases indexadas (Scielo, Scopus, Redalyc). Normas de citación APA 7ma. [FIN:FASE_2_SABER]
[INICIO:FASE_2_HACER] Elaboración de matriz de antecedentes y síntesis analítica de 10 fuentes primarias. [FIN:FASE_2_HACER]
[INICIO:FASE_2_SER] Rigor analítico frente a la desinformación y discernimiento crítico ante síntesis de IA. [FIN:FASE_2_SER]
[INICIO:FASE_2_SUDOR_INTELECTUAL] Matriz comparativa de autores construida activamente sin automatizaciones pasivas. [FIN:FASE_2_SUDOR_INTELECTUAL]
[INICIO:FASE_2_CRITERIO_EVAL] Síntesis teórica articulada con postura crítica propia del autor. [FIN:FASE_2_CRITERIO_EVAL]

[INICIO:FASE_3_TITULO] Diseño Metodológico e Instrumentos de Campo [FIN:FASE_3_TITULO]
[INICIO:FASE_3_SABER] Tipos y diseños de investigación, muestreo y técnicas de recolección de información. [FIN:FASE_3_SABER]
[INICIO:FASE_3_HACER] Construcción y validación por juicio de expertos de una guía de entrevista o cuestionario. [FIN:FASE_3_HACER]
[INICIO:FASE_3_SER] Respeto al consentimiento informado y confidencialidad en el tratamiento de datos. [FIN:FASE_3_SER]
[INICIO:FASE_3_SUDOR_INTELECTUAL] Prueba piloto del instrumento de recolección y diario de campo metodológico. [FIN:FASE_3_SUDOR_INTELECTUAL]
[INICIO:FASE_3_CRITERIO_EVAL] Coherencia interna entre objetivos, variables/categorías y técnicas de recolección. [FIN:FASE_3_CRITERIO_EVAL]

[INICIO:FASE_4_TITULO] Integración y Defensa del Perfil de Investigación [FIN:FASE_4_TITULO]
[INICIO:FASE_4_SABER] Estructura formal del informe de perfil de investigación y comunicación científica. [FIN:FASE_4_SABER]
[INICIO:FASE_4_HACER] Redacción final del perfil y sustentación oral socrática ante tribunal de pares. [FIN:FASE_4_HACER]
[INICIO:FASE_4_SER] Compromiso deontológico y responsabilidad social del investigador novel. [FIN:FASE_4_SER]
[INICIO:FASE_4_SUDOR_INTELECTUAL] Defensa verbal individual del documento validando autoría y comprensión profunda. [FIN:FASE_4_SUDOR_INTELECTUAL]
[INICIO:FASE_4_CRITERIO_EVAL] Perfil completo y sustentación oral rigurosa con dominio conceptual de las decisiones tomadas. [FIN:FASE_4_CRITERIO_EVAL]

[INICIO:ADAPTACIONES_DUA_INCLUSION] {estudiantes_ac}. Múltiples medios de representación (diagramas metodológicos, grabaciones) y evaluación flexible por hitos. [FIN:ADAPTACIONES_DUA_INCLUSION]
[INICIO:ESTRATEGIA_ANTI_OUTSOURCING] Triangulación Socrática obligatoria mediante coloquio oral individual de 10 minutos para defender el proceso de diseño metodológico. [FIN:ESTRATEGIA_ANTI_OUTSOURCING]
[INICIO:PRODUCTO_FINAL_MODULAR] Perfil de Investigación Científica defendido oralmente con evidencia de proceso. [FIN:PRODUCTO_FINAL_MODULAR]
"""

    # Guardar borrador en entrada
    borrador_path = os.path.join(dirs["entrada"], "borrador_cbl.txt")
    with open(borrador_path, "w", encoding="utf-8") as f:
        f.write(draft_text)

    # Guardar estado en JSON
    json_path = os.path.join(dirs["entrada"], "plan_info.json")
    info = {
        "subject_name": clean_subj,
        "model_id": "cbl_modular_inv101",
        "params": params,
        "motor_utilizado": motor,
        "fallback": fallback,
        "draft_text": draft_text
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    return info

def process_cbl_plan_to_output(subject_name: str) -> Dict[str, Any]:
    """Toma el borrador de la carpeta entrada, mapea las etiquetas e inyecta en la plantilla en la carpeta salida."""
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    dirs = ensure_subject_planning_dirs(clean_subj)

    borrador_path = os.path.join(dirs["entrada"], "borrador_cbl.txt")
    if not os.path.exists(borrador_path):
        raise FileNotFoundError("No se ha generado ningún borrador aún en la carpeta de entrada.")

    with open(borrador_path, "r", encoding="utf-8") as f:
        text = f.read()

    tags_map = parse_tags_from_text(text)
    tpl_path = dirs["plantilla_file"]
    out_file = os.path.join(dirs["salida"], f"PLAN_MODULAR_{clean_subj.replace(' ', '_')}.docx")

    inject_tags_into_docx(tpl_path, tags_map, out_file)

    return {
        "success": True,
        "message": "Plan Oficial por Competencias Modular generado con éxito en la carpeta de salida.",
        "tags_count": len(tags_map),
        "output_file": out_file,
        "relative_output_path": os.path.relpath(out_file, BASE_UPLOADS).replace('\\', '/')
    }
