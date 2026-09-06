"""
evaluation_service.py
Gestión de Planes de Evaluación por Asignatura, Adaptaciones Curriculares (AC),
Intervenciones por Alertas de Analítica y Detección Proactiva de Instrumentos Faltantes.
"""
import os
import json
import re
from typing import Dict, Any, List, Optional

BASE_UPLOADS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

CATALOGO_INSTRUMENTOS = [
    {
        "id": "ficha_autorregulacion",
        "alias": "self_peer_assessment",
        "name": "Ficha de Autoevaluación y Co-evaluación Formativa",
        "tipo_archivo": "docx",
        "impacto": "Efecto Hattie d = 1.16",
        "descripcion": "Instrumento estructurado para que el estudiante evalúe su propio proceso, activando la metacognición y dimensión afectiva.",
        "dimension": "Metacognición / Ser"
    },
    {
        "id": "rubrica_cbl",
        "name": "Matriz de Hitos y Rúbrica CBL",
        "tipo_archivo": "xlsx",
        "impacto": "Aprendizaje Basado en Competencias",
        "descripcion": "Rúbrica analítica de 4 niveles (Emergente, En Desarrollo, Competente, Avanzado) para evaluar hitos y transferibilidad.",
        "dimension": "Saber / Hacer"
    },
    {
        "id": "registro_sudor",
        "name": "Registro de Sudor Intelectual y DUA",
        "tipo_archivo": "xlsx",
        "impacto": "Anti-Outsourcing & Inclusión DUA",
        "descripcion": "Plantilla para registrar iteraciones de prompts, calidad del diálogo y canales múltiples de expresión del estudiante.",
        "dimension": "Proceso / Esfuerzo"
    },
    {
        "id": "triangulacion",
        "name": "Guía de Triangulación Socrática",
        "tipo_archivo": "docx",
        "impacto": "Rigor Epistémico & Defensa Oral",
        "descripcion": "Protocolo de entrevista docente para contrastar trabajos sospechosamente perfectos y evaluar el músculo intelectual real.",
        "dimension": "Verificación de Autoría"
    },
    {
        "id": "micro_quizzes",
        "name": "Batería de Micro-quizzes Tempranos",
        "tipo_archivo": "xlsx",
        "impacto": "Alerta Temprana en Semanas 1-2",
        "descripcion": "Evaluaciones de bajo riesgo para detectar lagunas en prerrequisitos antes del primer examen formal.",
        "dimension": "Diagnóstica"
    },
    {
        "id": "ficha_socioeducativa",
        "name": "Ficha Socioeducativa de Contexto",
        "tipo_archivo": "xlsx",
        "impacto": "Equidad & Factores Situacionales",
        "descripcion": "Relevamiento de conectividad, carga laboral y convivencia para fundamentar adaptaciones curriculares contextualizadas.",
        "dimension": "Contexto Familiar"
    }
]

def get_subject_dirs(subject_name: str) -> Dict[str, str]:
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
    raw_dir = os.path.join(BASE_UPLOADS, clean_subj)
    db_dir = os.path.join(rev_dir, "bases_de_datos")
    os.makedirs(db_dir, exist_ok=True)
    return {
        "clean_subj": clean_subj,
        "raw_dir": raw_dir,
        "rev_dir": rev_dir,
        "db_dir": db_dir,
        "plan_file": os.path.join(rev_dir, "plan_evaluacion.json"),
        "insights_file": os.path.join(db_dir, "insights.json"),
        "llave_file": os.path.join(db_dir, "llave_nombres.json")
    }

def check_missing_instruments(subject_name: str) -> List[Dict[str, Any]]:
    """Inspecciona las bases de datos de la materia para detectar qué instrumentos faltan."""
    dirs = get_subject_dirs(subject_name)
    raw_dir = dirs["raw_dir"]
    rev_db_dir = dirs["db_dir"]

    # Buscar archivos existentes en crudo y procesado
    existing_files = []
    for d in [raw_dir, rev_db_dir]:
        if os.path.exists(d):
            existing_files.extend([f.lower() for f in os.listdir(d)])

    missing = []
    
    # 1. Sudor Intelectual / DUA
    has_sudor = any("sudor" in f or "iteracion" in f for f in existing_files)
    if not has_sudor:
        missing.append({
            "instrument_id": "registro_sudor",
            "name": "Registro de Sudor Intelectual y DUA",
            "tipo_archivo": "xlsx",
            "motivo": "Sin datos de iteración de prompts ni modos de expresión. Esencial para detectar Outsourcing Cognitivo y aplicar DUA.",
            "accion_sugerida": "Descargar plantilla de Registro de Sudor e integrarla en el aula."
        })

    # 2. Socioeducativo
    has_socio = any("socio" in f or "contexto" in f for f in existing_files)
    if not has_socio:
        missing.append({
            "instrument_id": "ficha_socioeducativa",
            "name": "Ficha Socioeducativa de Contexto",
            "tipo_archivo": "xlsx",
            "motivo": "No se registran variables de conectividad ni situación laboral para fundamentar adaptaciones curriculares.",
            "accion_sugerida": "Descargar Ficha Socioeducativa para personalizar el apoyo estudiantil."
        })

    # 3. Micro-quizzes
    has_micro = any("micro" in f or "quiz" in f for f in existing_files)
    if not has_micro:
        missing.append({
            "instrument_id": "micro_quizzes",
            "name": "Micro-quizzes Tempranos (Semana 1-2)",
            "tipo_archivo": "xlsx",
            "motivo": "Falta información de diagnóstico temprano para activar andamiaje antes de las evaluaciones sumativas.",
            "accion_sugerida": "Descargar plantilla de Micro-quizzes."
        })

    return missing

def get_evaluation_plan(subject_name: str) -> Dict[str, Any]:
    """Obtiene el Plan de Evaluación de la materia con sus adaptaciones y sugerencias proactivas."""
    dirs = get_subject_dirs(subject_name)
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()

    # Cargar insights previos si existen
    insights = {}
    if os.path.exists(dirs["insights_file"]):
        try:
            with open(dirs["insights_file"], "r", encoding="utf-8") as f:
                insights = json.load(f)
        except Exception:
            pass

    # Cargar llave de nombres si existe
    llave = {}
    if os.path.exists(dirs["llave_file"]):
        try:
            with open(dirs["llave_file"], "r", encoding="utf-8") as f:
                llave = json.load(f)
        except Exception:
            pass

    # Detectar alertas automáticas de los estudiantes
    alertas_intervencion = []
    for e in insights.get("estudiantes", []):
        est_id = e.get("id")
        nombre_display = llave.get(est_id, est_id)
        # Iniciales para privacidad
        partes = nombre_display.split(" ")
        iniciales = "".join([p[0].upper() + "." for p in partes if p])

        if e.get("alerta_outsourcing_cognitivo") or e.get("requiere_triangulacion"):
            alertas_intervencion.append({
                "estudiante_id": est_id,
                "iniciales": iniciales,
                "alerta": "Alerta de Outsourcing Cognitivo (Uso pasivo de IA)",
                "instrumento_obligatorio": "triangulacion",
                "instrumento_nombre": "Guía de Triangulación Socrática",
                "medida_pedagogica": "Re-evaluación oral socrática individual para constatar comprensión profunda y dominio conceptual."
            })
        elif e.get("riesgo_abandono") == "Alto":
            alertas_intervencion.append({
                "estudiante_id": est_id,
                "iniciales": iniciales,
                "alerta": "Riesgo Crítico de Rezago / Prerrequisitos Pendientes",
                "instrumento_obligatorio": "micro_quizzes",
                "instrumento_nombre": "Micro-quizzes de Andamiaje",
                "medida_pedagogica": "Plan de nivelación con retroalimentación inmediata (Hattie d=1.16) y flexibilización de tiempos."
            })

    # Si ya existe un plan guardado, lo leemos
    if os.path.exists(dirs["plan_file"]):
        try:
            with open(dirs["plan_file"], "r", encoding="utf-8") as f:
                saved_plan = json.load(f)
                # Actualizar las alertas calculadas y los instrumentos faltantes en vivo
                saved_plan["alertas_intervencion"] = alertas_intervencion
                saved_plan["instrumentos_faltantes"] = check_missing_instruments(subject_name)
                return saved_plan
        except Exception:
            pass

    # Plan Base por Defecto (Modelo por Competencias - CBL Modular)
    plan_default = {
        "subject_name": clean_subj,
        "periodo": "1er Trimestre / Módulo 1",
        "modelo_evaluativo": "cbl_superior",
        "plan_base": {
            "etapas": [
                {
                    "id": "etapa_diagnostica",
                    "nombre": "Evaluación Diagnóstica Inicial",
                    "dimension": "Diagnóstico",
                    "ponderacion": 10,
                    "instrumentos": ["micro_quizzes"],
                    "criterio": "Verificación de prerrequisitos metodológicos y conceptuales básicos."
                },
                {
                    "id": "etapa_formativa",
                    "nombre": "Evaluación Formativa e Hitos de Proceso",
                    "dimension": "Hacer & Proceso (Sudor Intelectual)",
                    "ponderacion": 40,
                    "instrumentos": ["rubrica_cbl", "registro_sudor"],
                    "criterio": "Avance en matriz de antecedentes, fichas de lectura y bitácoras de iteración reflexiva."
                },
                {
                    "id": "etapa_sumativa",
                    "nombre": "Evaluación Sumativa / Desempeño Auténtico",
                    "dimension": "Producto & Transferencia",
                    "ponderacion": 40,
                    "instrumentos": ["triangulacion"],
                    "criterio": "Defensa del perfil de investigación y demostración de autoría propia."
                },
                {
                    "id": "etapa_autoevaluacion",
                    "nombre": "Metacognición y Autoevaluación Guiada",
                    "dimension": "Ser & Autorregulación (Hattie d=1.16)",
                    "ponderacion": 10,
                    "instrumentos": ["ficha_autorregulacion"],
                    "criterio": "Reflexión crítica sobre el propio proceso de aprendizaje, dificultades y superación."
                }
            ]
        },
        "adaptaciones_curriculares_ac": [
            {
                "id": "ac_01",
                "estudiante_iniciales": "E. L.",
                "diagnostico_necesidad": "Ritmo de procesamiento diferenciado y preferencia por canales visuales (DUA)",
                "ajustes_ponderacion": {
                    "etapa_formativa": 50,
                    "etapa_sumativa": 30
                },
                "instrumentos_diferenciados": ["rubrica_cbl", "registro_sudor"],
                "observaciones": "Se autoriza entrega mediante mapas conceptuales hipervinculados y evaluación en dos sesiones."
            }
        ],
        "alertas_intervencion": alertas_intervencion,
        "instrumentos_faltantes": check_missing_instruments(subject_name)
    }

    return plan_default

def save_evaluation_plan(subject_name: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """Guarda el Plan de Evaluación completo de la materia."""
    dirs = get_subject_dirs(subject_name)
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()
    plan_data["subject_name"] = clean_subj

    with open(dirs["plan_file"], "w", encoding="utf-8") as f:
        json.dump(plan_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "message": f"Plan de Evaluación guardado exitosamente para {clean_subj}.",
        "plan": plan_data
    }

def get_students_dua_profile_list(subject_name: str) -> List[Dict[str, Any]]:
    """Genera la lista personalizada de perfiles DUA para cada estudiante matriculado en la materia."""
    dirs = get_subject_dirs(subject_name)
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()

    # 1. Cargar plan de evaluacion para perfiles guardados
    plan = get_evaluation_plan(clean_subj)
    saved_profiles = plan.get("dua_estudiantes", {})

    # 2. Cargar metricas de analitica de insights.json si existen
    scatter_map = {}
    if os.path.exists(dirs["insights_file"]):
        try:
            with open(dirs["insights_file"], "r", encoding="utf-8") as f:
                ins = json.load(f)
                for sc in ins.get("scatter_rendimiento_proceso", []):
                    scatter_map[sc.get("id")] = sc
        except Exception:
            pass

    # 3. Verificar qué instrumentos existen a nivel de curso
    raw_dir = os.path.join(BASE_UPLOADS, clean_subj)
    rev_db_dir = dirs["db_dir"]
    course_files = []
    for d in [raw_dir, rev_db_dir]:
        if os.path.exists(d):
            course_files.extend([f.lower() for f in os.listdir(d)])

    has_course_sudor = any("sudor" in f or "iteracion" in f for f in course_files)
    has_course_socio = any("socio" in f or "contexto" in f for f in course_files)
    has_course_auto = any("autorregulacion" in f or "autoevaluacion" in f for f in course_files)
    has_course_quiz = any("micro" in f or "quiz" in f for f in course_files)

    # 4. Obtener lista de estudiantes
    students_raw = []
    if os.path.exists(dirs["llave_file"]):
        try:
            with open(dirs["llave_file"], "r", encoding="utf-8") as f:
                llave = json.load(f)
                for st_id, name in llave.items():
                    students_raw.append({"id": st_id, "name": name})
        except Exception:
            pass

    if not students_raw:
        mat_paths = [
            os.path.join(raw_dir, "LISTA_OFICIAL_matricula.xlsx"),
            os.path.join(dirs["rev_dir"], "bases_de_datos", "LISTA_OFICIAL_matricula.xlsx")
        ]
        for mp in mat_paths:
            if os.path.exists(mp):
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(mp)
                    ws = wb.active
                    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
                        if row and len(row) > 1 and row[1]:
                            students_raw.append({"id": f"Est_{idx:03d}", "name": str(row[1])})
                    if students_raw:
                        break
                except Exception:
                    pass

    if not students_raw:
        for idx in range(1, 11):
            students_raw.append({"id": f"Est_{idx:03d}", "name": f"Estudiante {idx:02d}"})

    # 5. Construir perfiles DUA
    results = []
    for st in students_raw:
        st_id = st["id"]
        full_name = st["name"]
        
        name_parts = [p.strip() for p in full_name.split() if p.strip()]
        iniciales = ". ".join([p[0].upper() for p in name_parts]) + "." if name_parts else f"{st_id}"
        
        sc_info = scatter_map.get(st_id, {})
        promedio = sc_info.get("promedio", 70.0)
        iteraciones = sc_info.get("iteraciones", 15)
        alerta_outsourcing = sc_info.get("alerta_outsourcing", False)
        riesgo_alto = sc_info.get("riesgo") in ["Alto", "Alto (Crítico)"]
        
        inst_faltantes = []
        if not has_course_socio:
            inst_faltantes.append({
                "id": "ficha_socioeducativa",
                "name": "Ficha Socioeducativa de Contexto",
                "motivo": "Sin datos de contexto sociocultural, conectividad o situación laboral para fundamentar adecuaciones DUA."
            })
        if not has_course_sudor or (iteraciones == 0 and not alerta_outsourcing):
            inst_faltantes.append({
                "id": "registro_sudor",
                "name": "Registro de Sudor Intelectual y DUA",
                "motivo": "Sin evidencia de iteración o esfuerzo reflexivo en el desarrollo de actividades."
            })
        if alerta_outsourcing:
            inst_faltantes.append({
                "id": "triangulacion",
                "name": "Guía de Triangulación Socrática",
                "motivo": "Alerta de outsourcing cognitivo detectada: requiere coloquio oral socrático para validar autoría."
            })
        if riesgo_alto and not has_course_quiz:
            inst_faltantes.append({
                "id": "micro_quizzes",
                "name": "Micro-quizzes Tempranos",
                "motivo": "Estudiante en riesgo: requiere diagnósticos de baja escala para andamiaje temprano."
            })

        saved = saved_profiles.get(st_id, {})
        def_compromiso = "Elección autónoma de subtema investigativo" if not alerta_outsourcing else "Coloquio socrático dialógico con docente"
        def_representacion = "Organizadores gráficos e infografías estructuradas" if riesgo_alto else "Lecturas académicas con guías de andamiaje"
        def_expresion = "Defensa oral socrática individual" if alerta_outsourcing else "Portafolio digital de evidencias"
        
        dua_profile = {
            "id": st_id,
            "iniciales": iniciales,
            "nombre_referencial": full_name,
            "promedio": promedio,
            "iteraciones": iteraciones,
            "alerta_outsourcing": alerta_outsourcing,
            "riesgo_alto": riesgo_alto,
            "estado_datos": "completo" if len(inst_faltantes) == 0 else "requiere_instrumentos",
            "instrumentos_faltantes": inst_faltantes,
            "principio_1_compromiso": saved.get("principio_1_compromiso", def_compromiso),
            "principio_2_representacion": saved.get("principio_2_representacion", def_representacion),
            "principio_3_accion_expresion": saved.get("principio_3_accion_expresion", def_expresion),
            "instrumento_clave": saved.get("instrumento_clave", "triangulacion" if alerta_outsourcing else "registro_sudor" if has_course_sudor else "rubrica_cbl"),
            "ponderacion_personalizada": saved.get("ponderacion_personalizada", None),
            "tiempo_extendido": saved.get("tiempo_extendido", False),
            "evaluacion_fragmentada": saved.get("evaluacion_fragmentada", riesgo_alto),
            "observaciones": saved.get("observaciones", "Perfil DUA ajustado según evidencias de aula.")
        }
        results.append(dua_profile)

    return results

def save_student_dua_profile(subject_name: str, student_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Guarda o actualiza la personalización DUA de un estudiante específico en el Plan de Evaluación."""
    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()
        
    plan = get_evaluation_plan(clean_subj)
    if "dua_estudiantes" not in plan:
        plan["dua_estudiantes"] = {}
        
    plan["dua_estudiantes"][student_id] = profile_data
    save_evaluation_plan(clean_subj, plan)
    
    return {
        "success": True,
        "message": f"Perfil DUA para {student_id} guardado correctamente.",
        "profile": profile_data
    }

def generate_dua_matrix_docx(subject_name: str) -> str:
    """Genera y guarda el documento formal en Word de la Matriz Institucional de Adaptaciones DUA."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    import datetime

    clean_subj = re.sub(r'[<>:"/\\|?*]', '', subject_name).strip()
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()

    students = get_students_dua_profile_list(clean_subj)
    doc = Document()

    # Configuración de márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Título Principal
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("CARPETA PEDAGÓGICA 2.0 • MATRIZ INSTITUCIONAL DUA")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    # Subtítulo
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run(f"Plan de Adaptaciones Curriculares y Evaluación Auténtica - Asignatura: {clean_subj}")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10)
    r_sub.italic = True
    r_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    p_meta = doc.add_paragraph()
    p_meta.add_run(f"Fecha de emisión: {datetime.date.today().strftime('%d/%m/%Y')}  |  Estudiantes registrados: {len(students)}\nMarco de Referencia: Diseño Universal para el Aprendizaje (CAST 2024) y Efecto Hattie (d = 1.16)")
    p_meta.runs[0].font.size = Pt(9)
    p_meta.runs[0].font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    # Tabla de Adaptaciones
    table = doc.add_table(rows=1, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [
        "Estudiante\n(Iniciales)",
        "Diagnóstico /\nAlerta Aula",
        "Principio 1:\nCompromiso (Afectivo)",
        "Principio 2:\nRepresentación (Reconocimiento)",
        "Principio 3:\nAcción y Expresión",
        "Instrumento &\nAjuste Evaluativo"
    ]

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shading = parse_xml(r'<w:shd {} w:fill="1A3A5C"/>'.format(nsdecls('w')))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

    for st in students:
        row_cells = table.add_row().cells
        
        # 1. Iniciales
        row_cells[0].text = f"{st['iniciales']}\n({st['id']})"
        row_cells[0].paragraphs[0].runs[0].font.bold = True
        
        # 2. Diagnóstico / Alerta
        diag = "Desempeño regular"
        if st.get("alerta_outsourcing"):
            diag = "⚠ Alerta: Outsourcing Cognitivo (Uso no reflexivo de IA)"
        elif st.get("riesgo_alto"):
            diag = "⚡ Alerta: Riesgo Severo de Rezago"
        elif st.get("iteraciones", 0) > 30:
            diag = "★ Alto Esfuerzo / Sudor Intelectual"
        row_cells[1].text = diag
        
        # 3. Principio 1
        row_cells[2].text = st.get("principio_1_compromiso", "-")
        
        # 4. Principio 2
        row_cells[3].text = st.get("principio_2_representacion", "-")
        
        # 5. Principio 3
        row_cells[4].text = st.get("principio_3_accion_expresion", "-")
        
        # 6. Instrumento y Ajuste
        ajuste = f"Inst: {st.get('instrumento_clave', 'rubrica_cbl')}"
        if st.get("tiempo_extendido"):
            ajuste += "\n• Tiempo extendido (+25%)"
        if st.get("evaluacion_fragmentada"):
            ajuste += "\n• Entrega por hitos"
        row_cells[5].text = ajuste

        # Estilo de celdas
        for c in row_cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(8.5)

    # Carpeta de salida
    docs_dir = os.path.join(BASE_UPLOADS, f"{clean_subj}-REV", "documentos")
    os.makedirs(docs_dir, exist_ok=True)
    out_docx_path = os.path.join(docs_dir, f"MATRIZ_ADAPTACIONES_DUA_{clean_subj.replace(' ', '_')}.docx")
    doc.save(out_docx_path)
    return out_docx_path
