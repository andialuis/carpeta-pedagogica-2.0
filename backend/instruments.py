import io
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    """Aplica color de fondo hexadecimal a una celda de tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    """Establece márgenes internos de celda en dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def generate_rubrica_cbl():
    """Genera plantilla Excel de Rúbrica de Hitos de Aprendizaje (CBL)."""
    data = {
        "ID_Estudiante": [f"Estudiante_{i:03d}" for i in range(1, 11)],
        "Nombre_Estudiante": ["Almendra Valdivia", "Carlos Rojas", "Diana Morales", "Esteban Lopez", "Fernanda Perez", 
                              "Gabriel Soto", "Helena Rios", "Ignacio Vega", "Javier Castro", "Lucia Mendez"],
        "Hito_1_Comprension_Teorica": ["Competente", "En Desarrollo", "Avanzado", "Emergente", "Competente", 
                                       "Emergente", "Competente", "Avanzado", "En Desarrollo", "Competente"],
        "Hito_2_Aplicacion_Practica": ["En Desarrollo", "En Desarrollo", "Competente", "Emergente", "Competente", 
                                       "Emergente", "En Desarrollo", "Avanzado", "Emergente", "Competente"],
        "Hito_3_Resolucion_Problemas": ["Competente", "Emergente", "Avanzado", "Emergente", "En Desarrollo", 
                                        "Emergente", "Competente", "Competente", "En Desarrollo", "Avanzado"],
        "Nivel_Proficiencia_Global": ["Competente", "En Desarrollo", "Avanzado", "Emergente", "Competente", 
                                      "Emergente", "En Desarrollo", "Avanzado", "En Desarrollo", "Competente"],
        "Observaciones_CBL": [
            "Demuestra maestría en laboratorio.", "Requiere andamiaje en transferencia matemática.", 
            "Excelente capacidad autónoma.", "Alerta crítica: brecha en prerrequisitos básicos.", 
            "Buen progreso.", "Dificultad de base.", "Progreso sostenido.", 
            "Liderazgo en equipo.", "Falta consolidar conceptos clave.", "Desempeño óptimo."
        ]
    }
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Matriz_Competencias_CBL")
    output.seek(0)
    return output.getvalue(), "Plantilla_Rubrica_CBL_Hitos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def generate_micro_quizzes():
    """Genera plantilla Excel para registro de Micro-quizzes tempranos (Semana 1-2)."""
    data = {
        "ID_Estudiante": [f"Estudiante_{i:03d}" for i in range(1, 11)],
        "Nombre_Estudiante": ["Almendra Valdivia", "Carlos Rojas", "Diana Morales", "Esteban Lopez", "Fernanda Perez", 
                              "Gabriel Soto", "Helena Rios", "Ignacio Vega", "Javier Castro", "Lucia Mendez"],
        "Diagnostico_Entrada_10pts": [9, 6, 10, 4, 8, 3, 7, 10, 5, 8],
        "MicroQuiz_Semana1_10pts": [8, 5, 9, 3, 8, 4, 7, 9, 6, 9],
        "MicroQuiz_Semana2_10pts": [9, 6, 10, 4, 7, 2, 8, 10, 5, 8],
        "Interaccion_Plataforma_Minutos": [120, 45, 180, 20, 110, 15, 85, 160, 50, 130],
        "Asistencia_Activa_Semana1_2": ["100%", "75%", "100%", "50%", "100%", "25%", "100%", "100%", "75%", "100%"],
        "Alerta_Temprana_Semana1": ["Sin Riesgo", "Riesgo Moderado", "Sin Riesgo", "Riesgo Crítico", "Sin Riesgo", 
                                    "Riesgo Crítico", "Sin Riesgo", "Sin Riesgo", "Riesgo Moderado", "Sin Riesgo"]
    }
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="MicroQuizzes_Semana1_2")
    output.seek(0)
    return output.getvalue(), "Plantilla_MicroQuizzes_Semana1_2.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def generate_ficha_socioeducativa():
    """Genera plantilla Excel con factores sociodemográficos y situacionales."""
    data = {
        "ID_Estudiante": [f"Estudiante_{i:03d}" for i in range(1, 11)],
        "Nombre_Estudiante": ["Almendra Valdivia", "Carlos Rojas", "Diana Morales", "Esteban Lopez", "Fernanda Perez", 
                              "Gabriel Soto", "Helena Rios", "Ignacio Vega", "Javier Castro", "Lucia Mendez"],
        "Edad": [19, 21, 20, 23, 19, 24, 20, 19, 22, 20],
        "Situacion_Laboral": ["No trabaja", "Medio tiempo", "No trabaja", "Tiempo completo", "No trabaja", 
                              "Tiempo completo", "No trabaja", "No trabaja", "Medio tiempo", "No trabaja"],
        "Convivencia": ["Con padres", "Solo/Compartido", "Con padres", "Con dependientes", "Con padres", 
                        "Con dependientes", "Con padres", "Con padres", "Solo/Compartido", "Con padres"],
        "Nivel_Educativo_Tutores": ["Universitario", "Secundaria", "Posgrado", "Primaria", "Universitario", 
                                    "Secundaria", "Universitario", "Posgrado", "Secundaria", "Universitario"],
        "Disponibilidad_Conectividad": ["Alta", "Media", "Alta", "Baja", "Alta", "Baja", "Alta", "Alta", "Media", "Alta"],
        "Riesgo_Vulnerabilidad_Inicial": ["Bajo", "Medio", "Bajo", "Alto", "Bajo", "Alto", "Bajo", "Bajo", "Medio", "Bajo"]
    }
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Variables_Sociodemograficas")
    output.seek(0)
    return output.getvalue(), "Ficha_Socioeducativa_Contexto.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def generate_ficha_autorregulacion():
    """Genera documento Word formal con la Ficha de Autoevaluación y Co-evaluación formativa (ISO 21001 / Karaman d=1.16)."""
    doc = Document()
    
    # Configuración de márgenes estándar
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        # Encabezado institucional de calidad
        header = section.header
        p_head = header.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_h = p_head.add_run("FICHA DE AUTOEVALUACIÓN Y CO-EVALUACIÓN • INST-CP2-AUTOEVAL-V1.0 • ISO 21001")
        r_h.font.name = "Arial"
        r_h.font.size = Pt(7.5)
        r_h.font.color.rgb = RGBColor(100, 116, 139)

        # Pie de página institucional
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_f = p_foot.add_run("Carpeta Pedagógica 2.0 • Evaluación Formativa, Agencia Estudiantil & Metacognición (d = 1.16)")
        r_f.font.name = "Arial"
        r_f.font.size = Pt(7.5)
        r_f.font.color.rgb = RGBColor(100, 116, 139)

    # Colores institucionales
    C_NAVY = RGBColor(26, 58, 92)       # #1A3A5C
    C_SLATE = RGBColor(30, 41, 59)      # #1E293B
    C_AMBER = RGBColor(180, 83, 9)      # #B45309
    C_DARK = RGBColor(15, 23, 42)       # #0F172A
    C_MUTED = RGBColor(100, 116, 139)   # #64748B

    # Portada / Título Principal
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("SISTEMA DE GESTIÓN DE LA CALIDAD EDUCATIVA • ISO 21001:2018\n")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(8.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = C_AMBER

    r_title = p_inst.add_run("FICHA INSTITUCIONAL DE AUTOEVALUACIÓN Y CO-EVALUACIÓN FORMATIVA")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = C_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Herramienta de Agencia Estudiantil, Autorregulación y Metacognición • Evidencia de Impacto Karaman (d = 1.16)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(8.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = C_MUTED

    # Tabla de Control Documental ISO 21001
    t_iso = doc.add_table(rows=3, cols=2)
    t_iso.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_iso.autofit = False

    iso_meta = [
        ("Código Institucional:", "INST-CP2-AUTOEVAL-V1.0 (Vigencia Semestre 2026)"),
        ("Marco Teórico / Impacto:", "Metacognición Guiada (Flavell) • Teoría de Autodeterminación (Deci & Ryan) • d=1.16"),
        ("Norma de Calidad Aplicable:", "ISO 21001:2018 Cláusula 9.1 (Seguimiento, Medición, Análisis y Evaluación)")
    ]
    for idx, (lbl, val) in enumerate(iso_meta):
        c0, c1 = t_iso.cell(idx, 0), t_iso.cell(idx, 1)
        set_cell_margins(c0, 50, 50, 100, 100)
        set_cell_margins(c1, 50, 50, 100, 100)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(lbl)
        r0.font.name = "Arial"
        r0.font.size = Pt(8)
        r0.font.bold = True
        r0.font.color.rgb = C_SLATE

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.name = "Arial"
        r1.font.size = Pt(8)
        r1.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # Tabla de Datos de Identificación
    t_id = doc.add_table(rows=2, cols=2)
    t_id.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_id.autofit = False

    id_data = [
        ("Estudiante Titular: _____________________________________", "Fecha de Aplicación: ____ / ____ / 2026"),
        ("Asignatura / Módulo: ___________________________________", "Hito o Fase Curricular: [ Hito 1 ] [ Hito 2 ] [ Hito 3 ] [ Hito 4 ]")
    ]
    for r_i, r_data in enumerate(id_data):
        for c_i, text in enumerate(r_data):
            cell = t_id.cell(r_i, c_i)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.color.rgb = C_SLATE

    doc.add_paragraph() # Espacio

    # 1. Autoevaluación en Escala Likert de 5 Niveles
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("1. AUTOEVALUACIÓN DE COMPETENCIAS Y METACOGNICIÓN (REFLEXIÓN INDIVIDUAL)")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(10.5)
    r_h1.font.bold = True
    r_h1.font.color.rgb = C_SLATE

    p_desc1 = doc.add_paragraph()
    r_desc1 = p_desc1.add_run("Evalúa con rigurosidad tu nivel de dominio real antes de la entrega formal. Escala: 1 = Inicial, 2 = Básico, 3 = En Desarrollo, 4 = Competente, 5 = Sobresaliente.")
    r_desc1.font.name = "Arial"
    r_desc1.font.size = Pt(8)
    r_desc1.font.italic = True
    r_desc1.font.color.rgb = C_MUTED

    t_eval = doc.add_table(rows=6, cols=6)
    t_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_eval.autofit = False

    eval_headers = ["Dimensión de Aprendizaje", "1 (Ini)", "2 (Bás)", "3 (Des)", "4 (Com)", "5 (Sob)"]
    for c_i, h_txt in enumerate(eval_headers):
        c = t_eval.cell(0, c_i)
        set_cell_background(c, "1A3A5C")
        set_cell_margins(c, 80, 80, 60, 60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i > 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h_txt)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    criterios_5 = [
        "1. Comprensión conceptual profunda de los principios teóricos del módulo.",
        "2. Aplicación procedimental y resolución metódica de casos prácticos auténticos.",
        "3. Autorregulación, persistencia frente al error y gestión autónoma del tiempo.",
        "4. Detección deliberada y corrección activa de mis propios fallos metodológicos.",
        "5. Capacidad argumentativa y sustentación dialógica de mis conclusiones ante otros."
    ]

    for r_i, crit in enumerate(criterios_5, start=1):
        row_c = t_eval.rows[r_i].cells
        bg = "FFFFFF" if r_i % 2 != 0 else "F8FAFC"
        set_cell_background(row_c[0], bg)
        set_cell_margins(row_c[0], 70, 70, 80, 80)
        p0 = row_c[0].paragraphs[0]
        r0 = p0.add_run(crit)
        r0.font.name = "Arial"
        r0.font.size = Pt(8)
        r0.font.color.rgb = C_DARK

        for col_i in range(1, 6):
            cell_box = row_c[col_i]
            set_cell_background(cell_box, bg)
            set_cell_margins(cell_box, 70, 70, 60, 60)
            p_b = cell_box.paragraphs[0]
            p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_box = p_b.add_run("[   ]")
            r_box.font.name = "Arial"
            r_box.font.size = Pt(8)
            r_box.font.color.rgb = C_MUTED

    doc.add_paragraph() # Espacio

    # 2. Dimensión Afectiva y Autoeficacia
    h2 = doc.add_paragraph()
    r_h2 = h2.add_run("2. DIMENSIÓN SOCIOEMOCIONAL Y AUTOEFICACIA (BANDURA & DECI/RYAN)")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(10.5)
    r_h2.font.bold = True
    r_h2.font.color.rgb = C_SLATE

    t_afec = doc.add_table(rows=2, cols=2)
    t_afec.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_afec.autofit = False

    set_cell_background(t_afec.cell(0, 0), "F1F5F9")
    set_cell_background(t_afec.cell(0, 1), "FFFFFF")
    set_cell_margins(t_afec.cell(0, 0), 80, 80, 100, 100)
    set_cell_margins(t_afec.cell(0, 1), 80, 80, 100, 100)
    p_af1 = t_afec.cell(0, 0).paragraphs[0]
    r_af1 = p_af1.add_run("Obstáculo o Nudo Crítico:\n¿Qué concepto o fase te generó mayor esfuerzo o frustración?")
    r_af1.font.name = "Arial"
    r_af1.font.size = Pt(8)
    r_af1.font.bold = True
    r_af1.font.color.rgb = C_SLATE

    p_af2 = t_afec.cell(0, 1).paragraphs[0]
    r_af2 = p_af2.add_run("_________________________________________________________________\n_________________________________________________________________")
    r_af2.font.name = "Arial"
    r_af2.font.size = Pt(8)
    r_af2.font.color.rgb = C_MUTED

    set_cell_background(t_afec.cell(1, 0), "F1F5F9")
    set_cell_background(t_afec.cell(1, 1), "FFFFFF")
    set_cell_margins(t_afec.cell(1, 0), 80, 80, 100, 100)
    set_cell_margins(t_afec.cell(1, 1), 80, 80, 100, 100)
    p_af3 = t_afec.cell(1, 0).paragraphs[0]
    r_af3 = p_af3.add_run("Autoeficacia Percibida (1 al 10):\n¿Cuánta confianza sientes para transferir esto a la práctica?")
    r_af3.font.name = "Arial"
    r_af3.font.size = Pt(8)
    r_af3.font.bold = True
    r_af3.font.color.rgb = C_SLATE

    p_af4 = t_afec.cell(1, 1).paragraphs[0]
    r_af4 = p_af4.add_run("Nivel de Seguridad: [ _____ / 10 ]  •  Estrategia que emplearé: _________________________")
    r_af4.font.name = "Arial"
    r_af4.font.size = Pt(8)
    r_af4.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # 3. Protocolo de Co-evaluación entre Pares (Efecto Grande d = 1.16)
    h3 = doc.add_paragraph()
    r_h3 = h3.add_run("3. PROTOCOLO INSTITUCIONAL DE CO-EVALUACIÓN ENTRE PARES (d = 1.16)")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(10.5)
    r_h3.font.bold = True
    r_h3.font.color.rgb = C_SLATE

    t_co = doc.add_table(rows=3, cols=2)
    t_co.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_co.autofit = False

    co_labels = [
        "Compañero Evaluador Asignado:",
        "Fortaleza Evidente (¿Qué logró con excelencia?):",
        "Oportunidad de Mejora y Andamiaje Recomendado:"
    ]
    co_lines = [
        "Nombre: ________________________________________________ Fecha: ____ / ____ / 2026",
        "• ___________________________________________________________________________________\n• ___________________________________________________________________________________",
        "• ___________________________________________________________________________________\n• Veredicto sugerido: [ ] Emergente  [ ] En Desarrollo  [ ] Competente  [ ] Sobresaliente"
    ]

    for idx in range(3):
        c_lbl = t_co.cell(idx, 0)
        c_val = t_co.cell(idx, 1)
        set_cell_margins(c_lbl, 70, 70, 100, 100)
        set_cell_margins(c_val, 70, 70, 100, 100)
        set_cell_background(c_lbl, "F1F5F9")
        set_cell_background(c_val, "FFFFFF")

        p_l = c_lbl.paragraphs[0]
        r_l = p_l.add_run(co_labels[idx])
        r_l.font.name = "Arial"
        r_l.font.size = Pt(8)
        r_l.font.bold = True
        r_l.font.color.rgb = C_SLATE

        p_v = c_val.paragraphs[0]
        r_v = p_v.add_run(co_lines[idx])
        r_v.font.name = "Arial"
        r_v.font.size = Pt(8)
        r_v.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # 4. Plan de Acción y Compromiso de Mejora Personal
    h4 = doc.add_paragraph()
    r_h4 = h4.add_run("4. PLAN DE ACCIÓN Y COMPROMISO DE MEJORA DEL ESTUDIANTE")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(10.5)
    r_h4.font.bold = True
    r_h4.font.color.rgb = C_SLATE

    t_plan = doc.add_table(rows=2, cols=2)
    t_plan.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_plan.autofit = False

    set_cell_background(t_plan.cell(0, 0), "FEF3C7")
    set_cell_background(t_plan.cell(0, 1), "FEF3C7")
    set_cell_margins(t_plan.cell(0, 0), 80, 80, 100, 100)
    set_cell_margins(t_plan.cell(0, 1), 80, 80, 100, 100)

    p_p1 = t_plan.cell(0, 0).paragraphs[0]
    r_p1 = p_p1.add_run("Mi Compromiso de Aprendizaje para la Siguiente Fase:\n___________________________________________________\n___________________________________________________")
    r_p1.font.name = "Arial"
    r_p1.font.size = Pt(8)
    r_p1.font.color.rgb = C_SLATE

    p_p2 = t_plan.cell(0, 1).paragraphs[0]
    r_p2 = p_p2.add_run("Apoyo Solicitado al Docente / Tutoría Académica:\n___________________________________________________\n___________________________________________________")
    r_p2.font.name = "Arial"
    r_p2.font.size = Pt(8)
    r_p2.font.color.rgb = C_SLATE

    # Firmas
    set_cell_background(t_plan.cell(1, 0), "FAFAFA")
    set_cell_background(t_plan.cell(1, 1), "FAFAFA")
    set_cell_margins(t_plan.cell(1, 0), 200, 60, 60, 60)
    set_cell_margins(t_plan.cell(1, 1), 200, 60, 60, 60)

    pf1 = t_plan.cell(1, 0).paragraphs[0]
    pf1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf1 = pf1.add_run("_____________________________________\nFirma de Compromiso del Estudiante")
    rf1.font.name = "Arial"
    rf1.font.size = Pt(7.5)
    rf1.font.color.rgb = C_MUTED

    pf2 = t_plan.cell(1, 1).paragraphs[0]
    pf2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf2 = pf2.add_run("_____________________________________\nVºBº / Retroalimentación Docente Titular")
    rf2.font.name = "Arial"
    rf2.font.size = Pt(7.5)
    rf2.font.color.rgb = C_MUTED

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue(), "Ficha_Autoevaluacion_Coevaluacion_d116.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def generate_registro_sudor_intelectual():
    """Genera plantilla Excel para registro de Sudor Intelectual (Métricas Cualitativas de Proceso)."""
    data = {
        "ID_Estudiante": [f"Estudiante_{i:03d}" for i in range(1, 11)],
        "Nombre_Estudiante": ["Almendra Valdivia", "Carlos Rojas", "Diana Morales", "Esteban Lopez", "Fernanda Perez", 
                              "Gabriel Soto", "Helena Rios", "Ignacio Vega", "Javier Castro", "Lucia Mendez"],
        "Iteraciones_Prompt": [3, 1, 5, 1, 4, 2, 3, 6, 1, 3],
        "Calidad_Prompt_CBL": ["Competente", "Emergente", "Avanzado", "Emergente", "Competente", 
                               "Emergente", "Competente", "Avanzado", "Emergente", "Competente"],
        "Participacion_Dialogo_Clase": ["Alta", "Baja", "Alta", "Nula", "Media", "Media", "Alta", "Alta", "Baja", "Alta"],
        "Formato_Expresion_Elegido_DUA": ["Ensayo", "Video", "Podcast", "Infografía", "Ensayo", "Mapa Mental", "Video", "Ensayo", "Infografía", "Podcast"],
        "Observaciones_Autonomia": [
            "Usa la IA para clarificar, no para resolver.", "Copia y pega directo del chatbot.",
            "Refina prompts con pensamiento crítico.", "Dependencia total del texto base.",
            "Buen manejo de fuentes externas.", "Dificultad para estructurar ideas.",
            "Muestra gran creatividad y apropiación.", "Cuestiona las respuestas de la IA.",
            "Uso pasivo de la tecnología.", "Alto compromiso en el foro."
        ]
    }
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Métricas_Sudor_Intelectual")
    output.seek(0)
    return output.getvalue(), "Registro_Sudor_Intelectual_y_DUA.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def generate_triangulacion_socratica():
    """Genera documento Word formal con la Guía de Triangulación Socrática y Auditoría Cognitiva (ISO 21001)."""
    doc = Document()
    
    # Configuración de márgenes estándar (0.8 in)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        # Encabezado institucional de calidad
        header = section.header
        p_head = header.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_h = p_head.add_run("GUÍA DE TRIANGULACIÓN SOCRÁTICA Y AUDITORÍA COGNITIVA • INST-CP2-SOCRATICA-V1.0 • ISO 21001")
        r_h.font.name = "Arial"
        r_h.font.size = Pt(7.5)
        r_h.font.color.rgb = RGBColor(100, 116, 139)

        # Pie de página institucional
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_f = p_foot.add_run("Carpeta Pedagógica 2.0 • Protocolo Anti-Outsourcing, Rigor Epistémico & ZDP • INST-CP2-SOCRATICA-V1.0")
        r_f.font.name = "Arial"
        r_f.font.size = Pt(7.5)
        r_f.font.color.rgb = RGBColor(100, 116, 139)

    # Colores institucionales
    C_NAVY = RGBColor(26, 58, 92)       # #1A3A5C
    C_SLATE = RGBColor(30, 41, 59)      # #1E293B
    C_AMBER = RGBColor(180, 83, 9)      # #B45309
    C_DARK = RGBColor(15, 23, 42)       # #0F172A
    C_MUTED = RGBColor(100, 116, 139)   # #64748B

    # Portada / Título Principal
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("SISTEMA DE GESTIÓN DE LA CALIDAD EDUCATIVA • AUDITORÍA ACADÉMICA\n")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(8.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = C_AMBER

    r_title = p_inst.add_run("GUÍA OFICIAL DE TRIANGULACIÓN SOCRÁTICA (ANTI-OUTSOURCING)")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = C_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Protocolo de Auditoría Cognitiva, Validación de Autoría Auténtica y Andamiaje ZDP (Vygotsky & Freire)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(8.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = C_MUTED

    # Tabla de Control Documental ISO 21001
    t_iso = doc.add_table(rows=3, cols=2)
    t_iso.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_iso.autofit = False

    iso_meta = [
        ("Código Institucional:", "INST-CP2-SOCRATICA-V1.0 (Vigencia Semestre 2026)"),
        ("Marco Epistémico / Didáctico:", "Pedagogía Crítica (Freire) • Zona de Desarrollo Próximo (Vygotsky) • Agencia (Deci & Ryan)"),
        ("Criterios de Activación:", "Entregas con perfección atípica, alertas analíticas de IA o discrepancia con el desempeño en aula")
    ]
    for idx, (lbl, val) in enumerate(iso_meta):
        c0, c1 = t_iso.cell(idx, 0), t_iso.cell(idx, 1)
        set_cell_margins(c0, 50, 50, 100, 100)
        set_cell_margins(c1, 50, 50, 100, 100)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(lbl)
        r0.font.name = "Arial"
        r0.font.size = Pt(8)
        r0.font.bold = True
        r0.font.color.rgb = C_SLATE

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.name = "Arial"
        r1.font.size = Pt(8)
        r1.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # Tabla de Datos de la Sesión de Triangulación
    t_id = doc.add_table(rows=3, cols=2)
    t_id.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_id.autofit = False

    id_data = [
        ("Estudiante Auditado: ___________________________________", "Docente Evaluador: ___________________________________"),
        ("Asignatura / Módulo: __________________________________", "Fecha de Aplicación: ____ / ____ / 2026"),
        ("Evidencia o Tarea Auditada: _____________________________", "Modalidad: [ Presencial ] [ Virtual / Sincrónica ]")
    ]
    for r_i, r_data in enumerate(id_data):
        for c_i, text in enumerate(r_data):
            cell = t_id.cell(r_i, c_i)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.color.rgb = C_SLATE

    doc.add_paragraph() # Espacio

    # 1. Protocolo de Diálogo Socrático en 4 Fases
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("1. PROTOCOLO DE DIÁLOGO SOCRÁTICO EN 4 FASES DIALÉCTICAS")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(10.5)
    r_h1.font.bold = True
    r_h1.font.color.rgb = C_SLATE

    t_fases = doc.add_table(rows=4, cols=2)
    t_fases.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_fases.autofit = False

    fases_data = [
        ("Fase 1: Apertura Dialógica & Motivación (Deci & Ryan)", 
         "Pregunta: 'Cuéntame, ¿qué aspecto específico de este problema llamó más tu atención y cómo decidiste abordarlo?'\nRegistro de respuesta del estudiante:\n__________________________________________________________________________________"),
        ("Fase 2: Deconstrucción Metodológica ('Sudor Intelectual')", 
         "Pregunta: 'Explícame paso a paso el hilo conductor de tus decisiones. ¿Cuáles fueron las versiones o borradores previos?'\nRegistro de respuesta del estudiante:\n__________________________________________________________________________________"),
        ("Fase 3: Variación Paramétrica & Estrés Conceptual", 
         "Pregunta: 'Si cambiáramos la variable X o modificáramos el supuesto Y de tu trabajo, ¿cómo respondería tu modelo?'\nRegistro de respuesta del estudiante:\n__________________________________________________________________________________"),
        ("Fase 4: Transferencia Epistémica & Interacción con IA", 
         "Pregunta: '¿En qué momentos consultaste herramientas generativas, qué prompts empleaste y cómo validaste sus respuestas?'\nRegistro de respuesta del estudiante:\n__________________________________________________________________________________")
    ]

    for f_idx, (f_title, f_body) in enumerate(fases_data):
        c_lbl = t_fases.cell(f_idx, 0)
        c_val = t_fases.cell(f_idx, 1)
        set_cell_margins(c_lbl, 80, 80, 100, 100)
        set_cell_margins(c_val, 80, 80, 100, 100)
        set_cell_background(c_lbl, "F1F5F9")
        set_cell_background(c_val, "FFFFFF")

        p_l = c_lbl.paragraphs[0]
        r_l = p_l.add_run(f_title)
        r_l.font.name = "Arial"
        r_l.font.size = Pt(8)
        r_l.font.bold = True
        r_l.font.color.rgb = C_SLATE

        p_v = c_val.paragraphs[0]
        r_v = p_v.add_run(f_body)
        r_v.font.name = "Arial"
        r_v.font.size = Pt(8)
        r_v.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # 2. Rúbrica Oficial de Evaluación Oral Socrática (4 Niveles)
    h2 = doc.add_paragraph()
    r_h2 = h2.add_run("2. RÚBRICA INSTITUCIONAL DE EVALUACIÓN ORAL SOCRÁTICA (4 NIVELES DE DOMINIO)")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(10.5)
    r_h2.font.bold = True
    r_h2.font.color.rgb = C_SLATE

    t_rub = doc.add_table(rows=5, cols=3)
    t_rub.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_rub.autofit = False

    rub_headers = ["Nivel de Dominio", "Descriptores Cualitativos del Desempeño Oral", "Veredicto"]
    for c_i, h_txt in enumerate(rub_headers):
        c = t_rub.cell(0, c_i)
        set_cell_background(c, "1A3A5C")
        set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_txt)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    niveles = [
        ("Nivel 1: Desconocimiento / Delegación Total (0-40%)", 
         "No logra explicar la estructura ni conceptos del documento. Evidencia delegación cognitiva total a herramientas externas sin apropiación personal.", "[   ]"),
        ("Nivel 2: Comprensión Fragmentaria (41-65%)", 
         "Reproduce definiciones memorizadas pero colapsa ante variaciones paramétricas o preguntas de causalidad. Requiere andamiaje reconstructivo.", "[   ]"),
        ("Nivel 3: Dominio Guiado / Competente (66-85%)", 
         "Explica con coherencia el proceso, reconoce los aportes de herramientas IA y justifica sus elecciones metodológicas con base teórica sólida.", "[   ]"),
        ("Nivel 4: Músculo Intelectual Consolidado (86-100%)", 
         "Defensa argumentada impecable, responde con solvencia ante contraejemplos complejos, refuta alternativas y propone aplicaciones creativas originales.", "[   ]")
    ]

    for r_i, (n_title, n_desc, n_check) in enumerate(niveles, start=1):
        row_c = t_rub.rows[r_i].cells
        bg = "FFFFFF" if r_i % 2 != 0 else "F8FAFC"
        for cell in row_c:
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 80, 80)

        p0 = row_c[0].paragraphs[0]
        r0 = p0.add_run(n_title)
        r0.font.name = "Arial"
        r0.font.size = Pt(8)
        r0.font.bold = True
        r0.font.color.rgb = C_SLATE

        p1 = row_c[1].paragraphs[0]
        r1 = p1.add_run(n_desc)
        r1.font.name = "Arial"
        r1.font.size = Pt(8)
        r1.font.color.rgb = C_DARK

        p2 = row_c[2].paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(n_check)
        r2.font.name = "Arial"
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_MUTED

    doc.add_paragraph() # Espacio

    # 3. Acta de Dictamen y Prescripción Pedagógica
    h3 = doc.add_paragraph()
    r_h3 = h3.add_run("3. ACTA FORMAL DE DICTAMEN INSTITUCIONAL DE AUTORÍA ACADÉMICA")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(10.5)
    r_h3.font.bold = True
    r_h3.font.color.rgb = C_SLATE

    t_acta = doc.add_table(rows=2, cols=2)
    t_acta.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_acta.autofit = False

    set_cell_background(t_acta.cell(0, 0), "FEF3C7")
    set_cell_background(t_acta.cell(0, 1), "FEF3C7")
    set_cell_margins(t_acta.cell(0, 0), 80, 80, 100, 100)
    set_cell_margins(t_acta.cell(0, 1), 80, 80, 100, 100)

    p_ac1 = t_acta.cell(0, 0).paragraphs[0]
    r_ac1 = p_ac1.add_run(
        "Dictamen Oficial del Evaluador:\n"
        "[   ] APROBADO: Autoría auténtica validada. Calificación ratificada.\n"
        "[   ] OBSERVADO: Plazo de 5 días para re-elaborar bajo andamiaje.\n"
        "[   ] OUTSOURCING REITERADO: Remisión a Comisión Académica."
    )
    r_ac1.font.name = "Arial"
    r_ac1.font.size = Pt(8)
    r_ac1.font.color.rgb = C_SLATE

    p_ac2 = t_acta.cell(0, 1).paragraphs[0]
    r_ac2 = p_ac2.add_run(
        "Prescripción de Andamiaje Pedagógico (ZDP):\n"
        "Acción requerida: ___________________________________________\n"
        "Fecha límite de subsanación: ____ / ____ / 2026\n"
        "Tutor asignado: _____________________________________________"
    )
    r_ac2.font.name = "Arial"
    r_ac2.font.size = Pt(8)
    r_ac2.font.color.rgb = C_SLATE

    # Firmas
    set_cell_background(t_acta.cell(1, 0), "FAFAFA")
    set_cell_background(t_acta.cell(1, 1), "FAFAFA")
    set_cell_margins(t_acta.cell(1, 0), 200, 60, 60, 60)
    set_cell_margins(t_acta.cell(1, 1), 200, 60, 60, 60)

    pf1 = t_acta.cell(1, 0).paragraphs[0]
    pf1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf1 = pf1.add_run("_____________________________________\nFirma del Docente Evaluador")
    rf1.font.name = "Arial"
    rf1.font.size = Pt(7.5)
    rf1.font.color.rgb = C_MUTED

    pf2 = t_acta.cell(1, 1).paragraphs[0]
    pf2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf2 = pf2.add_run("_____________________________________\nFirma de Conocimiento del Estudiante")
    rf2.font.name = "Arial"
    rf2.font.size = Pt(7.5)
    rf2.font.color.rgb = C_MUTED

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue(), "Guia_Triangulacion_Socratica.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

