"""
generate_cbl_template.py
Genera la Plantilla Oficial de Planificación por Competencias Modular (CBL)
con marcadores unívocos [[TAG]] para inyección automática.
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Aplica color de fondo hexadecimal a una celda de tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Establece márgenes internos de una celda en dxa (1 pt = 20 dxa)."""
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

def create_cbl_template(output_path: str):
    doc = Document()
    
    # Configuración de márgenes (1 pulgada)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colores Atelier
    C_SLATE = RGBColor(30, 41, 59)      # #1E293B
    C_AMBER = RGBColor(180, 83, 9)      # #B45309
    C_DARK = RGBColor(15, 23, 42)       # #0F172A
    C_MUTED = RGBColor(100, 116, 139)   # #64748B
    
    # Encabezado Principal
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = title_p.add_run("SISTEMA DE GESTIÓN CURRICULAR • EDUCACIÓN SUPERIOR Y FORMACIÓN CIENTÍFICA\n")
    r_sub.font.size = Pt(8.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = C_AMBER
    
    r_title = title_p.add_run("PLAN DE APRENDIZAJE MODULAR POR COMPETENCIAS (CBL)")
    r_title.font.size = Pt(16)
    r_title.font.bold = True
    r_title.font.color.rgb = C_DARK
    
    doc.add_paragraph() # Espacio
    
    # 1. Tabla de Datos Generales
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("1. DATOS GENERALES DEL MÓDULO")
    r_h1.font.size = Pt(11)
    r_h1.font.bold = True
    r_h1.font.color.rgb = C_SLATE
    
    t_gen = doc.add_table(rows=3, cols=4)
    t_gen.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_gen.autofit = False

    datos_gen = [
        [("Código:", True), ("[[CODIGO_MODULO]]", False), ("Asignatura / Módulo:", True), ("[[NOMBRE_MODULO]]", False)],
        [("Docente Titular:", True), ("[[DOCENTE]]", False), ("Carga Horaria:", True), ("[[DURACION_HORAS]]", False)],
        [("Periodo / Módulo:", True), ("[[PERIODO_MODULO]]", False), ("Modalidad:", True), ("[[MODALIDAD]]", False)]
    ]

    for row_idx, row_data in enumerate(datos_gen):
        for col_idx, (text, is_label) in enumerate(row_data):
            cell = t_gen.cell(row_idx, col_idx)
            set_cell_margins(cell, 100, 100, 120, 120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if is_label:
                r.font.bold = True
                r.font.color.rgb = C_SLATE
                set_cell_background(cell, "F1F5F9")
            else:
                r.font.color.rgb = C_DARK
                set_cell_background(cell, "FFFFFF")

    doc.add_paragraph() # Espacio

    # 2. Competencia Global y Problema del Contexto
    h2 = doc.add_paragraph()
    r_h2 = h2.add_run("2. COMPETENCIA GLOBAL Y PROBLEMATIZACIÓN DEL CONTEXTO")
    r_h2.font.size = Pt(11)
    r_h2.font.bold = True
    r_h2.font.color.rgb = C_SLATE
    
    t_comp = doc.add_table(rows=2, cols=2)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_comp.autofit = False
    
    c_labels = ["Problema del Contexto:", "Competencia Global del Módulo:"]
    c_tags = ["[[PROBLEMA_CONTEXTO]]", "[[COMPETENCIA_GLOBAL]]"]
    
    for idx in range(2):
        cell_lbl = t_comp.cell(idx, 0)
        cell_val = t_comp.cell(idx, 1)
        set_cell_margins(cell_lbl, 120, 120, 150, 150)
        set_cell_margins(cell_val, 120, 120, 150, 150)
        set_cell_background(cell_lbl, "F8FAFC")
        set_cell_background(cell_val, "FFFFFF")
        
        p_l = cell_lbl.paragraphs[0]
        r_l = p_l.add_run(c_labels[idx])
        r_l.font.bold = True
        r_l.font.size = Pt(9.5)
        r_l.font.color.rgb = C_SLATE
        
        p_v = cell_val.paragraphs[0]
        r_v = p_v.add_run(c_tags[idx])
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # 3. Matriz de Fases y Desarrollo Curricular Semanal (Hitos 1 a 4)
    h3 = doc.add_paragraph()
    r_h3 = h3.add_run("3. DESARROLLO MODULAR POR FASES Y HITOS DE APRENDIZAJE")
    r_h3.font.size = Pt(11)
    r_h3.font.bold = True
    r_h3.font.color.rgb = C_SLATE
    
    t_fases = doc.add_table(rows=5, cols=6)
    t_fases.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_fases.autofit = False
    
    # Encabezados de la tabla de fases
    headers = [
        "Fase / Semana", 
        "Saber (Conceptual)", 
        "Hacer (Procedimental)", 
        "Ser y Convivir (Actitudinal)", 
        "Sudor Intelectual (Evidencia)", 
        "Criterio de Evaluación"
    ]
    for col_idx, h_text in enumerate(headers):
        cell = t_fases.cell(0, col_idx)
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 120, 120, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for sem in range(1, 5):
        row_cells = t_fases.rows[sem].cells
        bg_col = "FFFFFF" if sem % 2 != 0 else "F8FAFC"
        
        tags_row = [
            f"Semana {sem}:\n[[FASE_{sem}_TITULO]]",
            f"[[FASE_{sem}_SABER]]",
            f"[[FASE_{sem}_HACER]]",
            f"[[FASE_{sem}_SER]]",
            f"[[FASE_{sem}_SUDOR_INTELECTUAL]]",
            f"[[FASE_{sem}_CRITERIO_EVAL]]"
        ]
        
        for col_idx, tag_text in enumerate(tags_row):
            cell = row_cells[col_idx]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, 100, 100, 100, 100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(tag_text)
            r.font.size = Pt(8.5)
            r.font.color.rgb = C_DARK
            if col_idx == 0:
                r.font.bold = True

    doc.add_paragraph() # Espacio

    # 4. Inclusión DUA y Triangulación Anti-Outsourcing
    h4 = doc.add_paragraph()
    r_h4 = h4.add_run("4. ENFOQUE HUMANO: INCLUSIÓN (DUA) Y RIGOR EPISTÉMICO")
    r_h4.font.size = Pt(11)
    r_h4.font.bold = True
    r_h4.font.color.rgb = C_SLATE
    
    t_dua = doc.add_table(rows=2, cols=2)
    t_dua.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dua.autofit = False
    
    dua_labels = [
        "Diseño Universal para el Aprendizaje (DUA) y Adecuaciones:",
        "Estrategia Anti-Outsourcing y Triangulación Socrática:"
    ]
    dua_tags = [
        "[[ADAPTACIONES_DUA_INCLUSION]]",
        "[[ESTRATEGIA_ANTI_OUTSOURCING]]"
    ]
    
    for idx in range(2):
        cell_lbl = t_dua.cell(idx, 0)
        cell_val = t_dua.cell(idx, 1)
        set_cell_margins(cell_lbl, 120, 120, 150, 150)
        set_cell_margins(cell_val, 120, 120, 150, 150)
        set_cell_background(cell_lbl, "F1F5F9")
        set_cell_background(cell_val, "FFFFFF")
        
        p_l = cell_lbl.paragraphs[0]
        r_l = p_l.add_run(dua_labels[idx])
        r_l.font.bold = True
        r_l.font.size = Pt(9.5)
        r_l.font.color.rgb = C_SLATE
        
        p_v = cell_val.paragraphs[0]
        r_v = p_v.add_run(dua_tags[idx])
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = C_DARK

    doc.add_paragraph() # Espacio

    # 5. Producto Final Integrador
    h5 = doc.add_paragraph()
    r_h5 = h5.add_run("5. PRODUCTO FINAL INTEGRADOR DEL MÓDULO")
    r_h5.font.size = Pt(11)
    r_h5.font.bold = True
    r_h5.font.color.rgb = C_SLATE
    
    t_prod = doc.add_table(rows=1, cols=2)
    t_prod.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_prod.autofit = False
    
    c_p_lbl = t_prod.cell(0, 0)
    c_p_val = t_prod.cell(0, 1)
    set_cell_margins(c_p_lbl, 120, 120, 150, 150)
    set_cell_margins(c_p_val, 120, 120, 150, 150)
    set_cell_background(c_p_lbl, "FEF3C7") # Ámbar suave
    set_cell_background(c_p_val, "FFFFFF")
    
    p_pl = c_p_lbl.paragraphs[0]
    r_pl = p_pl.add_run("Evidencia Auténtica Integradora:")
    r_pl.font.bold = True
    r_pl.font.size = Pt(9.5)
    r_pl.font.color.rgb = C_AMBER
    
    p_pv = c_p_val.paragraphs[0]
    r_pv = p_pv.add_run("[[PRODUCTO_FINAL_MODULAR]]")
    r_pv.font.size = Pt(9.5)
    r_pv.font.color.rgb = C_DARK

    # Pie de página editorial
    doc.add_paragraph()
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_foot = p_foot.add_run("Generado automáticamente por el Motor de Planificación Modular • Carpeta Pedagógica 2.0")
    r_foot.font.size = Pt(7.5)
    r_foot.font.italic = True
    r_foot.font.color.rgb = C_MUTED
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"Plantilla CBL guardada con éxito en: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    t_dir = os.path.join(os.path.dirname(__file__), "templates")
    out = os.path.join(t_dir, "Plantilla_CBL_Modular.docx")
    create_cbl_template(out)
