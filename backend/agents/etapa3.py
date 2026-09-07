"""
etapa3.py - Analizar Datos con IA (Gemini) y Enfoque Humano
Genera INFORME_COMPLETO_E3.docx e insights.json para cualquier materia.
"""
import os
import sys
import pandas as pd
import json
import statistics
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run():
    print("Iniciando Etapa 3: Análisis con IA y Enfoque Humano...")
    subject_name = sys.argv[1] if len(sys.argv) > 1 else "INV101 - Introduccion a la Investigacion"
    
    agents_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(agents_dir)
    root_dir = os.path.dirname(backend_dir)
    target_dir = os.path.join(root_dir, "uploads", f"{subject_name}-REV", "bases_de_datos")
    
    input_file = os.path.join(target_dir, "BASE_LIMPIA_ANONIMIZADA.xlsx")
    if not os.path.exists(input_file):
        # Intentar BASE_INTEGRADA si la anonimizada aún no se corrió
        input_file = os.path.join(target_dir, "BASE_INTEGRADA.xlsx")
    
    json_output = os.path.join(target_dir, "insights.json")
    docx_output = os.path.join(target_dir, "INFORME_COMPLETO_E3.docx")
    
    if not os.path.exists(input_file):
        print(f"Error: No se encontró {input_file}. Ejecuta la Etapa 1 o 2 primero.")
        sys.exit(1)
        
    print(f"Cargando datos desde {input_file} para materia: {subject_name}")
    df = pd.read_excel(input_file)
    
    # Cargar llave de nombres si existe
    llave_path = os.path.join(target_dir, "llave_nombres.json")
    llave = {}
    if os.path.exists(llave_path):
        try:
            with open(llave_path, "r", encoding="utf-8") as f:
                llave = json.load(f)
        except Exception:
            pass

    # Identificar columna de ID o Nombre
    id_col = None
    for c in ["Estudiante_ID", "Nombre", "ID", "Codigo", "Alumno"]:
        if c in df.columns:
            id_col = c
            break
    if not id_col:
        id_col = df.columns[0]
        
    # Identificar columna principal de rendimiento
    perf_col = None
    for c in ["Promedio_Ponderado", "Promedio", "Nota Final", "Nota_Final", "Puntaje_Total", "Calificacion"]:
        if c in df.columns:
            perf_col = c
            break
    if not perf_col:
        num_cols = df.select_dtypes(include='number').columns.tolist()
        perf_col = num_cols[-1] if num_cols else df.columns[-1]

    # Identificar columna de iteraciones / esfuerzo
    iter_col = None
    for c in ["Iteraciones_Prompt_Total", "Iteraciones", "Prompts", "Total_Eventos_Moodle", "Horas_Estudio"]:
        if c in df.columns:
            iter_col = c
            break

    # Extraer estadísticas descriptivas
    desc_stats = df.describe()

    # Verificar API Key de Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(backend_dir, ".env"))
        api_key = os.environ.get("GEMINI_API_KEY")

    insights = None
    informe_texto = ""
    error_gemini_msg = None

    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            datos_estudiantes = df.head(30).to_csv(index=False)
            prompt = f"""Eres un experto pedagógico en Analítica de Aprendizaje con Enfoque Humano (Deci & Ryan, Vygotsky, Freire).
Materia: {subject_name}
Datos de la clase:
{datos_estudiantes}

Escribe un informe analítico estructurado en formato JSON estricto con las siguientes claves:
{{
  "promedio_general": 75.0,
  "desviacion_estandar": 12.0,
  "riesgo_abandono": 2,
  "cobertura_cbl": "CBL Activo",
  "alerta_outsourcing_cognitivo": true,
  "outsourcing_count": 2,
  "potencial_oculto_count": 3,
  "necesidad_andamiaje_vygotsky": "Descripción analítica de la ZDP.",
  "alertas": ["Alerta 1", "Alerta 2"],
  "deci_ryan_clase": {{"autonomia": 7.0, "competencia": 6.8, "relacion": 7.2}},
  "hipotesis_gemini": "Párrafo interpretativo profundo sobre el grupo.",
  "estudiantes": [
    {{
      "id": "Est_001",
      "promedio": 85.0,
      "nivel_cbl": "Competente",
      "riesgo_abandono": "Bajo",
      "autonomia_deci_ryan": 8,
      "competencia_deci_ryan": 8,
      "relacion_deci_ryan": 7,
      "alerta_outsourcing_cognitivo": false,
      "requiere_triangulacion": false,
      "zdp_vygotsky": "En consolidación",
      "estrategia_hacker_curriculo": "Estrategia pedagógica",
      "recomendacion": "Recomendación"
    }}
  ]
}}"""
            gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
            print(f"Consultando a {gemini_model} con Structured Outputs...")
            response = client.models.generate_content(
                model=gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                ),
            )
            raw_text = response.text.strip()
            insights = json.loads(raw_text)

            # Normalizar si Gemini devolvió un array [ {...} ] en lugar de un diccionario { ... }
            if isinstance(insights, list):
                if len(insights) > 0 and isinstance(insights[0], dict):
                    if "estudiantes" in insights[0]:
                        insights = insights[0]
                    else:
                        insights = {"estudiantes": insights}
                else:
                    insights = {"estudiantes": []}

            if isinstance(insights, dict) and insights.get("estudiantes"):
                insights["motor_ia"] = {
                    "modo": "gemini",
                    "modelo": gemini_model,
                    "mensaje": f"Análisis cualitativo y pedagógico generado exitosamente con {gemini_model}.",
                    "fallback_activado": False,
                    "error_motivo": None
                }
                informe_texto = insights.get("hipotesis_gemini", "")
        except Exception as e:
            error_gemini_msg = str(e)
            print(f"[IA ADVERTENCIA] Falló consulta a Gemini ({e}). Activando motor determinista local de contingencia.")
            insights = None
    else:
        error_gemini_msg = "API_KEY_NO_CONFIGURADA"
        print("[IA ADVERTENCIA] GEMINI_API_KEY no detectada. Activando motor determinista local de contingencia.")

    # Motor Analítico Determinista / Robusto (si no hay Gemini o falló)
    if not insights or not insights.get("estudiantes"):
        print("Ejecutando motor analítico con Enfoque Humano...")
        estudiantes_list = []
        scores = []
        outsourcing_count = 0
        risk_count = 0
        hidden_count = 0

        for i, row in df.iterrows():
            est_id = str(row[id_col])
            nombre_real = llave.get(est_id, est_id)
            
            try:
                val = float(row[perf_col]) if perf_col in row and pd.notnull(row[perf_col]) else 70.0
            except Exception:
                val = 70.0
            scores.append(val)
            
            # Obtener iteraciones si existen
            iters = 0
            if iter_col and iter_col in row and pd.notnull(row[iter_col]):
                try:
                    iters = int(float(row[iter_col]))
                except Exception:
                    iters = 0

            # Detección de Outsourcing Cognitivo
            is_outsourcing = (val >= 90 and iters <= 5 and iter_col is not None)
            is_risk = (val < 51)
            is_hidden = (55 <= val <= 75 and iters >= 20)

            if is_outsourcing:
                outsourcing_count += 1
                nivel_cbl = "Avanzado (no verificado)"
                riesgo_ab = "Bajo (aparente)"
                aut = 2
                comp = 2
                rel = 3
                zdp = "Zona de Confort Digital: Riesgo de outsourcing cognitivo."
                estrat = "Triangulación Socrática obligatoria. Re-evaluación oral del proceso."
            elif is_risk:
                risk_count += 1
                nivel_cbl = "Inicial / En Riesgo"
                riesgo_ab = "Alto"
                aut = 3
                comp = 3
                rel = 4
                zdp = "Prerrequisitos pendientes: Requiere andamiaje intensivo."
                estrat = "Entrevista motivacional y articulación de apoyo socioeducativo."
            elif is_hidden:
                hidden_count += 1
                nivel_cbl = "Competente"
                riesgo_ab = "Bajo"
                aut = 7
                comp = 6
                rel = 8
                zdp = "ZDP activa: Potencial real supera las calificaciones cuantitativas."
                estrat = "Andamiaje en expresión académica y rúbricas alternativas (DUA)."
            elif val >= 80:
                nivel_cbl = "Avanzado"
                riesgo_ab = "Bajo"
                aut = 9
                comp = 9
                rel = 8
                zdp = "Maestría: Listo para proyectos de investigación autónomos."
                estrat = "Asignar rol de mentor de pares y desafíos avanzados."
            else:
                nivel_cbl = "Competente"
                riesgo_ab = "Bajo"
                aut = 6
                comp = 6
                rel = 6
                zdp = "Progresión sostenida dentro de los parámetros esperados."
                estrat = "Seguimiento formativo regular."

            estudiantes_list.append({
                "id": est_id,
                "nombre_real": nombre_real,
                "promedio": round(val, 1),
                "nivel_cbl": nivel_cbl,
                "riesgo_abandono": riesgo_ab,
                "autonomia_deci_ryan": aut,
                "competencia_deci_ryan": comp,
                "relacion_deci_ryan": rel,
                "alerta_outsourcing_cognitivo": is_outsourcing,
                "requiere_triangulacion": is_outsourcing,
                "zdp_vygotsky": zdp,
                "estrategia_hacker_curriculo": estrat,
                "recomendacion": f"Plan formativo personalizado para {nombre_real}."
            })

        n = len(scores) if scores else 1
        prom = round(sum(scores)/n, 1) if scores else 70.0
        mediana = round(float(statistics.median(scores)), 1) if scores else 70.0
        desv = round(statistics.stdev(scores), 1) if len(scores) > 1 else 0.0

        # Estadísticos de distribución (Asimetría y Curtosis)
        s_scores = pd.Series(scores)
        skew_val = round(float(s_scores.skew()), 2) if len(s_scores) > 2 else 0.0
        kurt_val = round(float(s_scores.kurt()), 2) if len(s_scores) > 3 else 0.0

        if skew_val < -0.5:
            skew_diag = "Asimetría Negativa: Concentración en notas altas (sesgo a la izquierda)."
        elif skew_val > 0.5:
            skew_diag = "Asimetría Positiva: Concentración en notas bajas (sesgo a la derecha)."
        else:
            skew_diag = "Distribución Cuasi-Simétrica: Calificaciones balanceadas."

        if kurt_val > 1.0:
            kurt_diag = "Leptocúrtica: Alta concentración de estudiantes en torno a la media."
        elif kurt_val < -1.0:
            kurt_diag = "Platicúrtica: Distribución aplanada y polarizada (alta dispersión)."
        else:
            kurt_diag = "Mesocúrtica: Dispersión moderada equivalente a normalidad."

        # Correlaciones de Rangos de Spearman (No paramétricas, robustas para muestras pequeñas)
        def compute_spearman(col_x, col_y):
            try:
                valid = df[[col_x, col_y]].dropna()
                if len(valid) < 3:
                    return 0.0
                vx = list(valid[col_x])
                vy = list(valid[col_y])
                def get_ranks(arr):
                    s_idx = sorted(range(len(arr)), key=lambda k: arr[k])
                    r = [0] * len(arr)
                    for rank_num, idx in enumerate(s_idx, 1):
                        r[idx] = rank_num
                    return r
                rx = get_ranks(vx)
                ry = get_ranks(vy)
                n = len(rx)
                d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
                rho = 1.0 - (6.0 * d_sq) / (n * (n ** 2 - 1))
                return round(float(rho), 2)
            except Exception:
                return 0.0

        asist_col = None
        for c in ["Total_Asistidas", "Porcentaje_%", "Asistencia", "Porcentaje_Asistencia"]:
            if c in df.columns:
                asist_col = c
                break

        spearman_asist_nota = compute_spearman(asist_col, perf_col) if asist_col and perf_col else 0.0
        spearman_proceso_nota = compute_spearman(iter_col, perf_col) if iter_col and perf_col else 0.0

        gauss_data = [{"rango": f"{r}-{r+9}", "estudiantes": sum(1 for p in scores if r <= p < r+10)} for r in range(0, 101, 10)]
        
        scatter_data = []
        for e in estudiantes_list:
            row_match = df[df[id_col].astype(str) == e["id"]]
            it_val = 15
            if not row_match.empty and iter_col and iter_col in row_match.columns:
                try:
                    it_val = int(row_match[iter_col].values[0])
                except Exception:
                    pass
            scatter_data.append({
                "id": e["id"],
                "promedio": e["promedio"],
                "iteraciones": it_val,
                "riesgo": e["riesgo_abandono"],
                "alerta_outsourcing": e["alerta_outsourcing_cognitivo"]
            })

        deci_ryan_class = {
            "autonomia": round(sum(e["autonomia_deci_ryan"] for e in estudiantes_list) / n, 1),
            "competencia": round(sum(e["competencia_deci_ryan"] for e in estudiantes_list) / n, 1),
            "relacion": round(sum(e["relacion_deci_ryan"] for e in estudiantes_list) / n, 1),
        }

        insights = {
            "subject": subject_name,
            "generated_at": pd.Timestamp.now().isoformat(),
            "total_students": n,
            "promedio_general": prom,
            "mediana_general": mediana,
            "desviacion_estandar": desv,
            "skewness": skew_val,
            "skewness_diagnostico": skew_diag,
            "kurtosis": kurt_val,
            "kurtosis_diagnostico": kurt_diag,
            "spearman_asistencia_nota": spearman_asist_nota,
            "spearman_proceso_nota": spearman_proceso_nota,
            "riesgo_abandono": risk_count,
            "cobertura_cbl": "Análisis Multidimensional Activo",
            "alerta_outsourcing_cognitivo": (outsourcing_count > 0),
            "outsourcing_count": outsourcing_count,
            "potencial_oculto_count": hidden_count,
            "necesidad_andamiaje_vygotsky": f"{risk_count} estudiantes requieren andamiaje urgente; {hidden_count} con potencial oculto detectado.",
            "alertas": [
                f"{outsourcing_count} estudiantes con alerta de Outsourcing Cognitivo (requieren Triangulación Socrática)." if outsourcing_count > 0 else "Sin anomalías de Outsourcing Cognitivo detectadas.",
                f"{risk_count} estudiantes clasificados en riesgo de rezago o abandono." if risk_count > 0 else "Nivel de retención óptimo en la clase.",
                f"{hidden_count} estudiantes con alto proceso pero notas moderadas (Potencial Oculto)." if hidden_count > 0 else "Procesos y notas alineados en el grupo.",
                f"Diagnóstico de Forma: {skew_diag} (Asimetría g1 = {skew_val})."
            ],
            "deci_ryan_clase": deci_ryan_class,
            "gauss_distribucion": gauss_data,
            "scatter_rendimiento_proceso": scatter_data,
            "estudiantes": estudiantes_list,
            "hipotesis_gemini": f"El grupo de {subject_name} presenta un promedio de {prom:.1f}/100 (Mediana: {mediana:.1f}) con desviación estándar de {desv:.1f}. Asimetría de Fisher: {skew_val} ({skew_diag}). Se identifican {risk_count} casos en riesgo y {outsourcing_count} alertas de outsourcing cognitivo.",
            "motor_ia": {
                "modo": "local_heuristico",
                "modelo": "motor_determinista_no_parametrico",
                "mensaje": (
                    "Medida de Contingencia Pedagógica: La clave de API de Gemini no está configurada aún en el sistema. "
                    if error_gemini_msg == "API_KEY_NO_CONFIGURADA" else
                    f"Medida de Contingencia Pedagógica: La API de Gemini reportó una incidencia ({error_gemini_msg}). "
                ) + "Se ejecutó el motor analítico determinista local con cálculo matemático puro (Spearman ρ, Asimetría Fisher g1, Curtosis g2 y ZDP Vygotsky) para garantizar la continuidad pedagógica sin pérdida de datos.",
                "fallback_activado": True,
                "error_motivo": error_gemini_msg
            }
        }
        informe_texto = insights["hipotesis_gemini"]

    # Generar gráficos Matplotlib
    fig1_path = os.path.join(target_dir, "fig1_notas.png")
    try:
        plt.figure(figsize=(8, 4))
        plt.hist([e["promedio"] for e in insights["estudiantes"]], bins=10, color='#1A3A5C', edgecolor='white')
        plt.title(f'Distribución de Rendimiento - {subject_name}')
        plt.xlabel('Calificación')
        plt.ylabel('N° Estudiantes')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(fig1_path, dpi=150)
        plt.close()
    except Exception as e:
        print(f"Error generando gráfico: {e}")

    # Construir INFORME_COMPLETO_E3.docx
    print("Construyendo INFORME_COMPLETO_E3.docx...")
    doc = Document()
    doc.add_heading(f"Informe Profesional de Analítica Educativa", 0)
    doc.add_heading(f"Materia: {subject_name}", 1)
    
    doc.add_heading("1. Resumen Ejecutivo y Diagnóstico", 2)
    doc.add_paragraph(informe_texto.strip())
    
    doc.add_heading("2. Indicadores Clave de la Clase (KPIs)", 2)
    kpis = [
        ("Promedio General", f"{insights.get('promedio_general', 0)} / 100"),
        ("Estudiantes en Riesgo", f"{insights.get('riesgo_abandono', 0)} / {len(insights.get('estudiantes', []))}"),
        ("Alertas de Outsourcing Cognitivo", f"{insights.get('outsourcing_count', 0)}"),
        ("Casos con Potencial Oculto", f"{insights.get('potencial_oculto_count', 0)}"),
    ]
    t = doc.add_table(rows=1, cols=2)
    t.style = 'Table Grid'
    t.rows[0].cells[0].text = "Indicador"
    t.rows[0].cells[1].text = "Valor"
    for k, v in kpis:
        r = t.add_row()
        r.cells[0].text = k
        r.cells[1].text = str(v)

    if os.path.exists(fig1_path):
        doc.add_heading("3. Distribución Estadística del Rendimiento", 2)
        doc.add_picture(fig1_path, width=Inches(6.0))

    doc.add_heading("4. Rigor Matemático y Análisis de Distribución", 2)
    doc.add_paragraph("Evaluación estadística avanzada para verificar supuestos de normalidad, asimetría de notas y correlaciones no paramétricas:")
    
    stat_metrics = [
        ("Media Aritmética (x̄)", f"{insights.get('promedio_general', 0)} / 100"),
        ("Mediana Muestral", f"{insights.get('mediana_general', 0)} / 100"),
        ("Desviación Estándar Muestral (s)", f"{insights.get('desviacion_estandar', 0)}"),
        ("Coeficiente de Asimetría (g1 - Fisher-Pearson)", f"{insights.get('skewness', 0)} ({insights.get('skewness_diagnostico', '')})"),
        ("Curtosis Muestral (g2 - Fisher)", f"{insights.get('kurtosis', 0)} ({insights.get('kurtosis_diagnostico', '')})"),
        ("Correlación de Spearman Asistencia-Rendimiento (ρ)", f"{insights.get('spearman_asistencia_nota', 0)} (No paramétrica)"),
        ("Correlación de Spearman Sudor Intelectual-Rendimiento (ρ)", f"{insights.get('spearman_proceso_nota', 0)} (Medición de Proceso)"),
    ]
    t_stat = doc.add_table(rows=1, cols=2)
    t_stat.style = 'Table Grid'
    t_stat.rows[0].cells[0].text = "Parámetro / Prueba Estadística"
    t_stat.rows[0].cells[1].text = "Resultado y Diagnóstico"
    for param, res in stat_metrics:
        r = t_stat.add_row()
        r.cells[0].text = param
        r.cells[1].text = str(res)

    doc.add_heading("5. Alertas Pedagógicas y Enfoque Humano", 2)
    for a in insights.get("alertas", []):
        doc.add_paragraph(f"• {a}")

    doc.add_heading("6. Marco Teórico Aplicado", 2)
    doc.add_paragraph(f"• Autodeterminación (Deci & Ryan): Autonomía={insights.get('deci_ryan_clase',{}).get('autonomia',7)}/10, Competencia={insights.get('deci_ryan_clase',{}).get('competencia',7)}/10, Relación={insights.get('deci_ryan_clase',{}).get('relacion',7)}/10.")
    doc.add_paragraph(f"• Zona de Desarrollo Próximo (Vygotsky): {insights.get('necesidad_andamiaje_vygotsky', 'Evaluación continua')}")
    doc.add_paragraph("• Pedagogía Crítica (Freire): Triangulación Socrática implementada para validar autoría y desarrollo de músculo intelectual propio.")

    doc.save(docx_output)
    print(f"Documento guardado: {docx_output}")

    # Guardar insights.json
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(insights, f, ensure_ascii=False, indent=4)
    print(f"JSON guardado: {json_output}")
    print("Etapa 3 completada con éxito.")

if __name__ == "__main__":
    run()
