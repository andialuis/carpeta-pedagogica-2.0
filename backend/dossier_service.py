"""
dossier_service.py
Generador del Dossier Consolidado: CARPETA PEDAGÓGICA INSTITUCIONAL COMPLETA (.docx)
Compila: Manifiesto, Diagnóstico Analítico, Plan Curricular Modular, Plan de Evaluación,
Rúbricas y Matriz de Adaptaciones DUA en un único documento maestro editorial.
"""
import os
import json
import re
import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_UPLOADS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

def build_consolidated_carpeta_docx(subject_name: str) -> str:
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()

    rev_dir = os.path.join(BASE_UPLOADS, f"{clean_subj}-REV")
    if not os.path.exists(rev_dir) and os.path.exists(BASE_UPLOADS):
        clean_lower = clean_subj.lower()
        for entry in os.listdir(BASE_UPLOADS):
            if entry.endswith("-REV"):
                cand_base = entry[:-4].strip()
                cand_lower = cand_base.lower()
                if cand_lower == clean_lower or cand_lower.startswith(clean_lower + " ") or cand_lower.startswith(clean_lower + "-") or clean_lower in cand_lower:
                    clean_subj = cand_base
                    rev_dir = os.path.join(BASE_UPLOADS, entry)
                    break

    db_dir = os.path.join(rev_dir, "bases_de_datos")
    plan_dir = os.path.join(rev_dir, "planificacion")
    docs_dir = os.path.join(rev_dir, "documentos")
    os.makedirs(docs_dir, exist_ok=True)

    # 1. Cargar Manifiesto
    manifest = {}
    man_path = os.path.join(rev_dir, "manifiesto.json")
    if os.path.exists(man_path):
        try:
            with open(man_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            pass

    # 2. Cargar Insights de Analítica
    insights = {}
    ins_path = os.path.join(db_dir, "insights.json")
    if os.path.exists(ins_path):
        try:
            with open(ins_path, "r", encoding="utf-8") as f:
                insights = json.load(f)
        except Exception:
            pass

    # 3. Cargar Plan de Evaluación
    from evaluation_service import get_evaluation_plan, get_students_dua_profile_list
    plan_eval = get_evaluation_plan(clean_subj)
    students_dua = get_students_dua_profile_list(clean_subj)

    # 4. Cargar Borrador de Planificación Modular
    from planning_service import parse_tags_from_text
    borrador_path = os.path.join(plan_dir, "entrada", "borrador_cbl.txt")
    planning_tags = {}
    if os.path.exists(borrador_path):
        try:
            with open(borrador_path, "r", encoding="utf-8") as f:
                planning_tags = parse_tags_from_text(f.read())
        except Exception:
            pass

    # Iniciar Documento Word
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # PORTADA EDITORIAL
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("SISTEMA DE GESTIÓN CURRICULAR & ANALÍTICA DE APRENDIZAJE\nCARPETA PEDAGÓGICA 2.0\n")
    r_inst.bold = True
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph()

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("DOSSIER PEDAGÓGICO CONSOLIDADO")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(f"Planificación Curricular Modular • Evaluación Auténtica • Matriz DUA • Analítica de Aula\nASIGNATURA: {clean_subj.upper()}")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12)
    r_sub.bold = True
    r_sub.font.color.rgb = RGBColor(0xB8, 0x5D, 0x19)

    doc.add_paragraph()

    tbl_meta = doc.add_table(rows=5, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Docente Titular:", manifest.get("teacher") or planning_tags.get("DOCENTE", "Docente Titular")),
        ("Nivel y Régimen:", f"{manifest.get('level', 'Superior / Pregrado')} — {manifest.get('duration', 'Semestral / Modular')} ({manifest.get('year', 2026)})"),
        ("Periodo Académico:", manifest.get("period") or planning_tags.get("PERIODO_MODULO", "Periodo 1 - 2026")),
        ("Modalidad de Aprendizaje:", planning_tags.get("MODALIDAD", "Semipresencial / Aula Invertida")),
        ("Fecha de Consolidación:", datetime.date.today().strftime("%d de %B de %Y"))
    ]
    for idx, (label, val) in enumerate(meta_rows):
        c1, c2 = tbl_meta.rows[idx].cells
        c1.text = label
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        c2.text = str(val)
        c2.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_page_break()

    # SECCIÓN I: MANIFIESTO Y COMPETENCIAS GLOBALES
    h1 = doc.add_heading("I. Caracterización Curricular y Problema del Contexto", level=1)
    h1.runs[0].font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    p_prob = doc.add_paragraph()
    r_p1 = p_prob.add_run("Problema Central del Contexto:\n")
    r_p1.bold = True
    p_prob.add_run(planning_tags.get("PROBLEMA_CONTEXTO", "Desarrollo de pensamiento investigativo crítico frente al riesgo de outsourcing cognitivo y uso acrítico de inteligencia artificial."))

    p_comp = doc.add_paragraph()
    r_p2 = p_comp.add_run("Competencia Global de la Asignatura:\n")
    r_p2.bold = True
    p_comp.add_run(planning_tags.get("COMPETENCIA_GLOBAL", "Formula, diseña y defiende un perfil de investigación riguroso aplicando metodologías científicas pertinentes, con responsabilidad deontológica y sustentación oral socrática."))

    doc.add_paragraph()

    # SECCIÓN II: DIAGNÓSTICO DE ANALÍTICA DEL APRENDIZAJE
    h2 = doc.add_heading("II. Diagnóstico Analítico y Prescripción Pedagógica", level=1)
    h2.runs[0].font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    if insights:
        p_diag = doc.add_paragraph()
        p_diag.add_run(f"Población Estudiantil: {insights.get('total_students', len(students_dua))} estudiantes matriculados.\n")
        p_diag.add_run(f"• Promedio General de Rendimiento: {insights.get('promedio_general', 72.0)}/100 (Mediana: {insights.get('mediana_general', 70.0)}, Desv. Est: {insights.get('desviacion_estandar', 15.0)}).\n")
        p_diag.add_run(f"• Diagnóstico de Asimetría (Fisher g1 = {insights.get('skewness', 0)}): {insights.get('skewness_diagnostico', 'Distribución equilibrada')}.\n")
        p_diag.add_run(f"• Alertas de Outsourcing Cognitivo: {insights.get('outsourcing_count', 0)} estudiantes identificados con alta nota pero nulo esfuerzo de iteración.\n")
        p_diag.add_run(f"• Casos en Riesgo de Rezago: {insights.get('riesgo_abandono', 0)} estudiantes clasificados en riesgo prioritario.\n")
        p_diag.add_run(f"• Zona de Desarrollo Próximo (Vygotsky): {insights.get('necesidad_andamiaje_vygotsky', 'Andamiaje formativo activo')}.")
    else:
        doc.add_paragraph("Diagnóstico preliminar basado en la lista de matrícula institucional. Se recomienda ejecutar el pipeline analítico (/analytics) para enriquecer métricas en tiempo real.")

    doc.add_paragraph()

    # SECCIÓN III: PLANIFICACIÓN MODULAR POR FASES
    h3 = doc.add_heading("III. Planificación Curricular Modular (4 Fases de Hitos)", level=1)
    h3.runs[0].font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    fases_data = [
        ("Fase 1: Planteamiento y Problematización", "FASE_1_SABER", "FASE_1_HACER", "FASE_1_SUDOR_INTELECTUAL", "FASE_1_CRITERIO_EVAL"),
        ("Fase 2: Marco Teórico y Estado del Arte", "FASE_2_SABER", "FASE_2_HACER", "FASE_2_SUDOR_INTELECTUAL", "FASE_2_CRITERIO_EVAL"),
        ("Fase 3: Diseño Metodológico de Campo", "FASE_3_SABER", "FASE_3_HACER", "FASE_3_SUDOR_INTELECTUAL", "FASE_3_CRITERIO_EVAL"),
        ("Fase 4: Integración y Defensa Socrática", "FASE_4_SABER", "FASE_4_HACER", "FASE_4_SUDOR_INTELECTUAL", "FASE_4_CRITERIO_EVAL")
    ]

    for titulo, tag_saber, tag_hacer, tag_sudor, tag_crit in fases_data:
        p_fase = doc.add_paragraph()
        r_f = p_fase.add_run(f"• {titulo}\n")
        r_f.bold = True
        r_f.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)
        p_fase.add_run(f"  - Saberes Conceptuales: {planning_tags.get(tag_saber, 'Fundamentos teóricos pertinentes.')}\n")
        p_fase.add_run(f"  - Desempeño Práctico (Hacer): {planning_tags.get(tag_hacer, 'Actividades guiadas en taller.')}\n")
        p_fase.add_run(f"  - Evidencia de Sudor Intelectual: {planning_tags.get(tag_sudor, 'Bitácora de iteraciones y prompts reflexivos.')}\n")
        p_fase.add_run(f"  - Criterio de Evaluación: {planning_tags.get(tag_crit, 'Rigor y consistencia lógica.')}\n")

    doc.add_page_break()

    # SECCIÓN IV: PLAN DE EVALUACIÓN Y PONDERACIONES
    h4 = doc.add_heading("IV. Plan de Evaluación de los Aprendizajes (Control 100%)", level=1)
    h4.runs[0].font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    etapas = plan_eval.get("plan_base", {}).get("etapas", [])
    tbl_eval = doc.add_table(rows=1, cols=4)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdrs_eval = ["Momento Evaluativo", "Dimensión", "Ponderación", "Instrumentos Asignados"]
    for i, h in enumerate(hdrs_eval):
        c = tbl_eval.rows[0].cells[i]
        c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shd = parse_xml(r'<w:shd {} w:fill="1A3A5C"/>'.format(nsdecls('w')))
        c._tc.get_or_add_tcPr().append(shd)

    for et in etapas:
        row = tbl_eval.add_row().cells
        row[0].text = et.get("nombre", "")
        row[1].text = et.get("dimension", "")
        row[2].text = f"{et.get('ponderacion', 0)}%"
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row[3].text = ", ".join(et.get("instrumentos", []))

    doc.add_paragraph()

    # SECCIÓN V: MATRIZ DE ADAPTACIONES DUA POR ESTUDIANTE
    h5 = doc.add_heading("V. Matriz Institucional DUA (Inclusión & Privacidad por Iniciales)", level=1)
    h5.runs[0].font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    p_dua_intro = doc.add_paragraph()
    p_dua_intro.add_run("Protocolo de Confidencialidad: En cumplimiento con la protección de datos personales de los estudiantes, se reportan únicamente las iniciales unívocas y los principios DUA adaptados.\nMarco de Referencia: CAST 2024 y Síntesis de John Hattie (Efecto d = 1.16).")
    p_dua_intro.runs[0].font.size = Pt(8.5)
    p_dua_intro.runs[0].italic = True

    tbl_dua = doc.add_table(rows=1, cols=5)
    tbl_dua.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_dua = ["Estudiante", "Diagnóstico Aula", "1. Compromiso", "2. Representación", "3. Acción y Expresión"]
    for i, h in enumerate(hdrs_dua):
        c = tbl_dua.rows[0].cells[i]
        c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(8.5)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shd = parse_xml(r'<w:shd {} w:fill="1A3A5C"/>'.format(nsdecls('w')))
        c._tc.get_or_add_tcPr().append(shd)

    for st in students_dua:
        row = tbl_dua.add_row().cells
        row[0].text = f"{st['iniciales']}\n({st['id']})"
        row[0].paragraphs[0].runs[0].font.bold = True
        
        diag = "Regular"
        if st.get("alerta_outsourcing"):
            diag = "⚠ Alerta Outsourcing"
        elif st.get("riesgo_alto"):
            diag = "⚡ Alerta Rezago"
        row[1].text = diag
        
        row[2].text = st.get("principio_1_compromiso", "-")
        row[3].text = st.get("principio_2_representacion", "-")
        row[4].text = st.get("principio_3_accion_expresion", "-")

        for c in row:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(8)

    doc.add_paragraph()

    # SECCIÓN VI: CATÁLOGO DE INSTRUMENTOS UTILIZADOS
    h6 = doc.add_heading("VI. Catálogo de Instrumentos de Recolección y Evaluación", level=1)
    h6.runs[0].font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    from evaluation_service import CATALOGO_INSTRUMENTOS
    for inst in CATALOGO_INSTRUMENTOS:
        p_inst_desc = doc.add_paragraph()
        r_in = p_inst_desc.add_run(f"• {inst['name']} (Formato: .{inst['tipo_archivo'].upper()} | Dimensión: {inst['dimension']})\n")
        r_in.bold = True
        p_inst_desc.add_run(f"  Propósito pedagógico: {inst['descripcion']} Impacto esperado: {inst['impacto']}.")

    # Firmas
    doc.add_paragraph()
    doc.add_paragraph()
    tbl_firmas = doc.add_table(rows=1, cols=2)
    tbl_firmas.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_f1, c_f2 = tbl_firmas.rows[0].cells
    c_f1.text = "_______________________________\nFirma del Docente Titular\nResponsable de Asignatura"
    c_f1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c_f2.text = "_______________________________\nCoordinación Académica / Jefatura\nValidación y Acreditación"
    c_f2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    out_dossier_path = os.path.join(docs_dir, f"CARPETA_PEDAGOGICA_CONSOLIDADA_{clean_subj.replace(' ', '_')}.docx")
    doc.save(out_dossier_path)
    return out_dossier_path
