import io
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
    """Genera documento Word con la Ficha de Autoevaluación y Co-evaluación formativa (d=1.16)."""
    doc = Document()
    
    title = doc.add_heading("FICHA DE AUTOEVALUACIÓN Y CO-EVALUACIÓN FORMATIVA", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph("Herramienta de Agencia Estudiantil y Metacognición (Basada en Karaman 2021, d = 1.16)")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.italic = True
    
    doc.add_heading("Datos Generales", level=1)
    p_meta = doc.add_paragraph()
    p_meta.add_run("Estudiante: ____________________________________________________  Fecha: _____________\n")
    p_meta.add_run("Materia: ________________________________________  Hito/Unidad de Aprendizaje: _________")
    
    doc.add_heading("1. Autoevaluación de Hitos de Competencia (Reflexión Individual)", level=1)
    doc.add_paragraph("Marca con honestidad tu nivel de dominio percibido antes de la entrega o examen sumativo:")
    
    table1 = doc.add_table(rows=5, cols=4)
    table1.style = 'Table Grid'
    headers1 = ["Criterio / Competencia", "Emergente (1)", "En Desarrollo (2)", "Competente (3)"]
    for i, h in enumerate(headers1):
        table1.rows[0].cells[i].text = h
        
    criterios = [
        "1. Comprensión de conceptos y principios fundamentales",
        "2. Habilidad para aplicar la teoría a casos prácticos",
        "3. Identificación y corrección de mis propios errores",
        "4. Capacidad de explicar el procedimiento a un compañero"
    ]
    for row_idx, crit in enumerate(criterios, start=1):
        table1.rows[row_idx].cells[0].text = crit
        table1.rows[row_idx].cells[1].text = "[   ]"
        table1.rows[row_idx].cells[2].text = "[   ]"
        table1.rows[row_idx].cells[3].text = "[   ]"
        
    doc.add_heading("2. Dimensión Afectiva y Autoeficacia (Detección de Riesgo Socioemocional)", level=1)
    doc.add_paragraph("Responde brevemente a las siguientes preguntas de autorregulación:")
    doc.add_paragraph("¿Cuál ha sido el concepto o tarea que mayor frustración o dificultad te ha generado esta semana?")
    doc.add_paragraph("___________________________________________________________________________________________________\n___________________________________________________________________________________________________")
    doc.add_paragraph("En una escala del 1 al 10, ¿cuánta confianza sientes para resolver los desafíos de esta unidad? [ ___ ]")
    
    doc.add_heading("3. Protocolo de Co-evaluación entre Pares (Efecto Grande d=1.16)", level=1)
    doc.add_paragraph("Intercambia tu trabajo con un compañero y completa la siguiente guía constructiva:")
    p_co = doc.add_paragraph()
    p_co.add_run("Compañero evaluador: ___________________________________________________________________\n\n")
    p_co.add_run("• Una fortaleza destacable de tu trabajo es:\n___________________________________________________________________________________________________\n\n")
    p_co.add_run("• Una recomendación concreta para que alcances el nivel Competente es:\n___________________________________________________________________________________________________")
    
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
    """Genera documento Word con la Guía de Triangulación Socrática (Anti-Outsourcing)."""
    doc = Document()
    
    title = doc.add_heading("GUÍA DE TRIANGULACIÓN SOCRÁTICA", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph("Herramienta de Auditoría Cognitiva y Prevención de Outsourcing (Basado en Freire & Vygotsky)")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.italic = True
    
    doc.add_heading("Contexto de la Intervención", level=1)
    doc.add_paragraph("Utilice este instrumento cuando el sistema alerte que una entrega tiene indicios de ser 'demasiado perfecta' sin evidencia de proceso, iteración o esfuerzo (Sudor Intelectual).")
    
    p_meta = doc.add_paragraph()
    p_meta.add_run("Estudiante Entrevistado: _____________________________________  Fecha: _____________\n")
    p_meta.add_run("Tema o Proyecto Entregado: _______________________________________________________")
    
    doc.add_heading("1. Exploración de Autonomía (Deci & Ryan)", level=1)
    doc.add_paragraph("Pregunte al estudiante: 'Cuéntame, ¿qué fue lo que más te interesó al investigar sobre este tema?'")
    doc.add_paragraph("___________________________________________________________________________________________________\n___________________________________________________________________________________________________")
    
    doc.add_heading("2. Triangulación de Competencia (ZDP de Vygotsky)", level=1)
    doc.add_paragraph("Seleccione un párrafo clave o concepto complejo del trabajo entregado por el estudiante. Pregunte:")
    doc.add_paragraph("1. 'Aquí mencionas [Insertar concepto]. ¿Podrías explicármelo con tus propias palabras o con un ejemplo de tu vida diaria?'")
    doc.add_paragraph("2. 'Si cambiáramos [Variable X] en tu proyecto, ¿cómo se vería afectado el resultado final?'")
    doc.add_paragraph("___________________________________________________________________________________________________\n___________________________________________________________________________________________________")
    
    doc.add_heading("3. Diagnóstico del Docente (Hacker del Currículo)", level=1)
    doc.add_paragraph("Con base en el diálogo socrático, determine el nivel real de dominio y la necesidad de andamiaje:")
    
    table1 = doc.add_table(rows=4, cols=2)
    table1.style = 'Table Grid'
    table1.rows[0].cells[0].text = "Indicador Post-Diálogo"
    table1.rows[0].cells[1].text = "Selección"
    table1.rows[1].cells[0].text = "A) Outsourcing Cognitivo Confirmado (No logra sostener la tesis oralmente. Requiere retroceso y andamiaje fuerte)."
    table1.rows[1].cells[1].text = "[   ]"
    table1.rows[2].cells[0].text = "B) Competencia Asistida (Muestra comprensión básica, usó IA como apoyo pero requiere clarificar conceptos)."
    table1.rows[2].cells[1].text = "[   ]"
    table1.rows[3].cells[0].text = "C) Músculo Intelectual Validado (Domina el tema por completo, usó la IA como copiloto eficiente)."
    table1.rows[3].cells[1].text = "[   ]"
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue(), "Guia_Triangulacion_Socratica.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
