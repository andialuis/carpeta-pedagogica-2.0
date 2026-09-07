from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import json
import anyio
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

from database import init_db, get_db
from ai_service import analyze_spreadsheet_structure

app = FastAPI(
    title="Carpeta Pedagógica 2.0 API",
    description="API para el sistema de administración documental y analítica de aprendizaje",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/agents/list")
def list_agents():
    """Devuelve la lista de agentes/módulos disponibles migrados."""
    return {
        "modules": [
            {"id": "e1", "name": "Etapa 1: Preparar Datos", "description": "Limpia y clasifica los datos crudos.", "products": "BASE_INTEGRADA.xlsx"},
            {"id": "e2", "name": "Etapa 2: Procesar Datos", "description": "Anonimiza e imputa datos vacíos (Crea diccionario de nombres).", "products": "BASE_LIMPIA_ANONIMIZADA.xlsx, llave_nombres.json"},
            {"id": "e3", "name": "Etapa 3: Analizar Datos", "description": "Genera indicadores e hipótesis usando Gemini.", "products": "INFORME_COMPLETO_E3.docx, insights.json"},
            {"id": "e4", "name": "Etapa 4: Visualizar Datos", "description": "Construye los tableros analíticos interactivos.", "products": "Dashboard Interactivo Web (Next.js)"}
        ]
    }

from pydantic import BaseModel
from typing import Optional, List

class SubjectCreateRequest(BaseModel):
    name: str
    code: Optional[str] = None
    system: str = "superior" # regular, superior, tecnico, otro
    level: Optional[str] = "pregrado" # kinder, primaria, secundaria, pregrado, postgrado, tecnico_medio, tecnico_superior
    duration: str = "semestral" # mensual, bimestral, trimestral, semestral, anual, modular
    year: int = 2025
    period: Optional[str] = "1"
    teacher: Optional[str] = "Docente Titular"
    description: Optional[str] = ""
    create_sample_data: Optional[bool] = True

import re

def sanitize_folder_name(name: str) -> str:
    """Sanitiza el nombre de carpeta para prevenir Path Traversal y caracteres prohibidos en Windows."""
    # Quitar secuencias peligrosas
    clean = name.replace("..", "").replace("/", " ").replace("\\", " ")
    # Quitar caracteres prohibidos en Windows: < > : " / \ | ? *
    clean = re.sub(r'[<>:"/\\|?*]', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean if clean else "Materia_Sin_Nombre"

@app.post("/api/subjects/create")
async def create_subject(req: SubjectCreateRequest):
    """Crea una nueva materia con su estructura de carpetas, metadatos y dataset inicial."""
    import json
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    # Formatear y sanitizar nombre de carpeta
    raw_name = req.name.strip()
    if req.code and req.code.strip():
        folder_name = sanitize_folder_name(f"{req.code.strip()} - {raw_name}")
    else:
        folder_name = sanitize_folder_name(raw_name)
        
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    raw_dir = os.path.join(base_dir, folder_name)
    rev_dir = os.path.join(base_dir, f"{folder_name}-REV")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(os.path.join(rev_dir, "bases_de_datos"), exist_ok=True)
    os.makedirs(os.path.join(rev_dir, "documentos"), exist_ok=True)
    os.makedirs(os.path.join(rev_dir, "imagenes"), exist_ok=True)
    os.makedirs(os.path.join(rev_dir, "presentaciones"), exist_ok=True)
    
    # Crear manifiesto con metadatos
    manifest = {
        "subject_name": folder_name,
        "name": req.name,
        "code": req.code,
        "system": req.system,
        "level": req.level,
        "duration": req.duration,
        "year": req.year,
        "period": req.period,
        "teacher": req.teacher,
        "description": req.description,
        "created_at": os.path.getctime(raw_dir) if os.path.exists(raw_dir) else 0,
        "status": "configurada"
    }
    with open(os.path.join(rev_dir, "manifiesto.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    # Inicializar automáticamente las carpetas de planificación y plan de evaluación por defecto
    try:
        from planning_service import ensure_subject_planning_dirs
        from evaluation_service import get_evaluation_plan
        ensure_subject_planning_dirs(folder_name)
        get_evaluation_plan(folder_name)
    except Exception as e:
        print(f"Advertencia inicializando planificación/evaluación para {folder_name}: {e}")

    # Crear datos iniciales si se solicitó
    if req.create_sample_data:
        # 1. Lista de matricula
        wb_mat = openpyxl.Workbook()
        ws_mat = wb_mat.active
        ws_mat.title = "Matricula"
        ws_mat.append(["#", "Nombre Completo", "Cédula/ID", "Edad", "Sexo", "Email_Institucional", "Semestre_Actual"])
        
        sample_names = [
            "Ana Maria Gomez", "Carlos Eduardo Rios", "Sofia Fernandez", "Diego Armando Perez",
            "Valentina Morales", "Luis Fernando Castro", "Camila Andrea Vega", "Mateo Silva",
            "Lucia Mendoza", "Sebastian Ruiz", "Isabella Navarro", "Gabriel Vargas"
        ]
        for idx, name in enumerate(sample_names, 1):
            ws_mat.append([idx, name, f"CI-{100000+idx*421}", 20 + (idx % 5), "F" if idx % 2 == 1 else "M", f"est{idx:03d}@inst.edu", req.period or "1"])
            
        for cell in ws_mat[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1A3A5C")
        wb_mat.save(os.path.join(raw_dir, "LISTA_OFICIAL_matricula.xlsx"))
        
        # 2. Notas
        wb_not = openpyxl.Workbook()
        ws_not = wb_not.active
        ws_not.title = "Notas"
        ws_not.append(["#", "Nombre", "Evaluacion_1", "Evaluacion_2", "Proyecto_Final", "Promedio_Ponderado"])
        import random
        for idx, name in enumerate(sample_names, 1):
            n1 = random.randint(55, 98)
            n2 = random.randint(50, 95)
            n3 = random.randint(60, 100)
            prom = round(n1*0.3 + n2*0.3 + n3*0.4, 1)
            ws_not.append([idx, name, n1, n2, n3, prom])
        for cell in ws_not[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1A3A5C")
        wb_not.save(os.path.join(raw_dir, "notas_evaluaciones.xlsx"))
        
        # 3. Asistencia
        wb_as = openpyxl.Workbook()
        ws_as = wb_as.active
        ws_as.title = "Asistencia"
        ws_as.append(["#", "Nombre", "Sesion_1", "Sesion_2", "Sesion_3", "Sesion_4", "Total_Asistidas", "Porcentaje_%"])
        for idx, name in enumerate(sample_names, 1):
            s1, s2, s3, s4 = 1, 1, 1 if idx % 4 != 0 else 0, 1
            tot = s1 + s2 + s3 + s4
            ws_as.append([idx, name, s1, s2, s3, s4, tot, round(tot/4*100, 1)])
        for cell in ws_as[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1A3A5C")
        wb_as.save(os.path.join(raw_dir, "asistencia.xlsx"))
        
        # 4. Registro Sudor Intelectual
        wb_sud = openpyxl.Workbook()
        ws_sud = wb_sud.active
        ws_sud.title = "Sudor Intelectual"
        ws_sud.append(["#", "Nombre", "Iteraciones_Prompt_Total", "Calidad_Dialogo_Aula (1-5)", "Autonomia_Percibida (1-5)", "Uso_IA_Como_Copiloto_vs_Muleta"])
        for idx, name in enumerate(sample_names, 1):
            it = random.randint(10, 45) if idx % 3 != 0 else random.randint(1, 4)
            ws_sud.append([idx, name, it, random.randint(3, 5), random.randint(3, 5), "Copiloto" if it > 8 else "Muleta"])
        for cell in ws_sud[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1A3A5C")
        wb_sud.save(os.path.join(raw_dir, "registro_sudor_intelectual.xlsx"))
        
    return {
        "success": True,
        "message": f"Materia '{folder_name}' creada exitosamente.",
        "subject_name": folder_name,
        "metadata": manifest
    }

def resolve_subject_folder(subject_name: str) -> tuple:
    """Resuelve el nombre canónico y la ruta absoluta de la carpeta REV de una materia.
    Soporta nombres completos, códigos cortos (INV101) o nombres con/sin -REV."""
    clean = sanitize_folder_name(subject_name)
    if clean.endswith("-REV"):
        clean = clean[:-4].strip()
        
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    
    if os.path.exists(base_dir):
        clean_lower = clean.lower()
        candidates = []
        for entry in os.listdir(base_dir):
            if entry.endswith("-REV"):
                cand_base = entry[:-4].strip()
                cand_lower = cand_base.lower()
                if cand_lower == clean_lower or cand_lower.startswith(clean_lower + " ") or cand_lower.startswith(clean_lower + "-") or clean_lower in cand_lower:
                    rev_path = os.path.join(base_dir, entry)
                    has_data = os.path.exists(os.path.join(rev_path, "bases_de_datos", "insights.json")) or os.path.exists(os.path.join(rev_path, "manifiesto.json"))
                    candidates.append((has_data, len(cand_base), cand_base, rev_path))
        if candidates:
            # Priorizar carpetas con datos reales y nombres más completos
            candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
            return candidates[0][2], candidates[0][3]

    direct_rev = os.path.join(base_dir, f"{clean}-REV")
    return clean, direct_rev

@app.get("/api/subjects/summary/{subject_name}")
def get_subject_summary_endpoint(subject_name: str):
    """Retorna el resumen pedagógico del curso (diagnóstico, planificación, evaluación, DUA y dossier)."""
    canonical_name, rev_dir = resolve_subject_folder(subject_name)
    
    man_path = os.path.join(rev_dir, "manifiesto.json")
    manifest = {}
    if os.path.exists(man_path):
        try:
            with open(man_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            pass
            
    has_insights = os.path.exists(os.path.join(rev_dir, "bases_de_datos", "insights.json"))
    
    plan_salida = os.path.join(rev_dir, "planificacion", "salida")
    has_plan_doc = os.path.exists(plan_salida) and len([f for f in os.listdir(plan_salida) if f.endswith(".docx")]) > 0
    has_plan_draft = os.path.exists(os.path.join(rev_dir, "planificacion", "entrada", "borrador_cbl.txt"))
    
    has_eval_plan = os.path.exists(os.path.join(rev_dir, "plan_evaluacion.json"))
    dua_count = 0
    if has_eval_plan:
        try:
            with open(os.path.join(rev_dir, "plan_evaluacion.json"), "r", encoding="utf-8") as f:
                p = json.load(f)
                dua_count = len(p.get("dua_estudiantes", {}))
        except Exception:
            pass
            
    docs_dir = os.path.join(rev_dir, "documentos")
    has_dossier = os.path.exists(docs_dir) and any("CARPETA_PEDAGOGICA" in f for f in os.listdir(docs_dir))
    
    return {
        "subject_name": canonical_name,
        "manifest": manifest,
        "diagnostico_status": "completado" if has_insights else "pendiente",
        "planificacion_status": "documento_oficial" if has_plan_doc else "borrador" if has_plan_draft else "pendiente",
        "evaluacion_status": "activo" if has_eval_plan else "pendiente",
        "dua_customized_count": dua_count,
        "dossier_disponible": has_dossier
    }

@app.post("/api/agents/run/{module_id}")
async def run_agent(module_id: str, subject_name: str = None, db = Depends(get_db)):
    """Ejecuta el script del agente IA asociado al módulo para cualquier materia."""
    import subprocess
    import json
    from models import AgentHistory
    from drive_service import upload_to_drive
    
    if not subject_name:
        raise HTTPException(status_code=400, detail="Se requiere el parámetro 'subject_name'")
        
    subject_name = sanitize_folder_name(subject_name)
    agents_map = {
        "e1": "etapa1.py",
        "e2": "etapa2.py",
        "e3": "etapa3.py",
        "e4": "etapa4.py"
    }
    script_name = agents_map.get(module_id)
    if not script_name:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
        
    full_script_path = os.path.join(os.path.dirname(__file__), "agents", script_name)
    if not os.path.exists(full_script_path):
        raise HTTPException(status_code=404, detail=f"Script {script_name} no encontrado en agents")
        
    # Ejecutar el script pasando el subject_name como argumento CLI de forma no bloqueante
    try:
        python_exe = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            python_exe = "python"
            
        def _exec_process():
            return subprocess.run(
                [python_exe, full_script_path, subject_name],
                capture_output=True,
                text=True,
                cwd=os.path.join(os.path.dirname(__file__), "agents")
            )

        result = await anyio.to_thread.run_sync(_exec_process)
        script_output = result.stdout + ("\nSTDERR: " + result.stderr if result.stderr and result.returncode != 0 else "")
        if result.returncode != 0:
            print(f"Error ejecutando agente {module_id}:", result.stderr)
    except Exception as e:
        print("Error ejecutando agente:", e)
        raise HTTPException(status_code=500, detail=f"Falló la ejecución del script: {e}")
        
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    stage_products = {
        "e1": "BASE_INTEGRADA.xlsx",
        "e2": "BASE_LIMPIA_ANONIMIZADA.xlsx",
        "e3": "INFORME_COMPLETO_E3.docx",
        "e4": "insights.json"
    }
    product_filename = stage_products.get(module_id, "BASE_INTEGRADA.xlsx")
    generated_file_path = os.path.join(base_dir, f"{subject_name}-REV", "bases_de_datos", product_filename)
    
    drive_link = "#"
    try:
        if os.path.exists(generated_file_path):
            drive_result = upload_to_drive(generated_file_path, convert_to_google_format=True)
            drive_link = drive_result.get('webViewLink', '#')
    except Exception as e:
        drive_link = f"Error: {str(e)}"
    
    history = AgentHistory(
        module_id=module_id,
        subject_name=subject_name,
        details=f"Ejecutado agente {script_name} para {subject_name}",
        files_generated=json.dumps([{"name": product_filename, "link": drive_link}])
    )
    db.add(history)
    db.commit()
    
    return {"message": "Finalizado", "script_executed": script_name, "output": script_output}

@app.get("/api/agents/history/{subject_name}")
def get_agent_history(subject_name: str, db = Depends(get_db)):
    from models import AgentHistory
    clean_subj = sanitize_folder_name(subject_name)
    records = db.query(AgentHistory).filter(AgentHistory.subject_name == clean_subj).order_by(AgentHistory.executed_at.desc()).all()
    return {"history": records}

from planning_service import (
    get_planning_models,
    get_planning_model,
    save_planning_model,
    ensure_subject_planning_dirs,
    generate_cbl_plan_draft,
    process_cbl_plan_to_output
)
from evaluation_service import (
    CATALOGO_INSTRUMENTOS,
    get_evaluation_plan,
    save_evaluation_plan,
    check_missing_instruments,
    get_students_dua_profile_list,
    save_student_dua_profile,
    generate_dua_matrix_docx
)

# --- ENDPOINTS DE PLANIFICACIÓN (MODELOS GLOBALES & INV101) ---

@app.get("/api/planning/models")
def list_planning_models():
    """Retorna los modelos globales de planificación disponibles."""
    return {"models": get_planning_models()}

@app.post("/api/planning/models")
def create_or_update_planning_model(model_data: dict):
    """Crea o actualiza un modelo global de planificación."""
    saved = save_planning_model(model_data)
    return {"success": True, "model": saved}

@app.get("/api/planning/subject/{subject_name}")
def get_subject_planning_details(subject_name: str):
    """Retorna la información de planificación para la materia (carpetas, modelo, borrador)."""
    clean_subj = sanitize_folder_name(subject_name)
    dirs = ensure_subject_planning_dirs(clean_subj)
    
    # Determinar modelo sugerido
    model_id = "cbl_modular_inv101" if "INV" in clean_subj.upper() or "QUIM" in clean_subj.upper() else "pdc_minedu_2026"
    model = get_planning_model(model_id)
    
    borrador_path = os.path.join(dirs["entrada"], "borrador_cbl.txt")
    borrador_text = ""
    if os.path.exists(borrador_path):
        try:
            with open(borrador_path, "r", encoding="utf-8") as f:
                borrador_text = f.read()
        except Exception:
            pass
            
    out_files = []
    if os.path.exists(dirs["salida"]):
        out_files = os.listdir(dirs["salida"])
        
    return {
        "subject_name": clean_subj,
        "model": model,
        "dirs": {
            "entrada": dirs["entrada"],
            "salida": dirs["salida"],
            "plantilla": dirs["plantilla"]
        },
        "has_draft": bool(borrador_text),
        "draft_text": borrador_text,
        "output_files": out_files
    }

class PlanGenerateRequest(BaseModel):
    codigo_modulo: Optional[str] = "INV101"
    docente: Optional[str] = "Docente Titular"
    periodo: Optional[str] = "Módulo 1 - 2026"
    duracion_horas: Optional[str] = "80 horas académicas"
    modalidad: Optional[str] = "Semipresencial / Aula Invertida"
    problema_contexto: Optional[str] = ""
    estudiantes_ac: Optional[str] = ""

@app.post("/api/planning/subject/{subject_name}/generate")
async def generate_plan_for_subject(subject_name: str, req: PlanGenerateRequest):
    """Genera el borrador del plan con IA o motor determinista."""
    clean_subj = sanitize_folder_name(subject_name)
    api_key = os.environ.get("GEMINI_API_KEY")
    
    def _run_gen():
        return generate_cbl_plan_draft(clean_subj, req.dict(), api_key)
        
    res = await anyio.to_thread.run_sync(_run_gen)
    return res

@app.post("/api/planning/subject/{subject_name}/process")
async def process_plan_for_subject(subject_name: str):
    """Toma el borrador de entrada y lo inyecta en la plantilla Word en la carpeta de salida."""
    clean_subj = sanitize_folder_name(subject_name)
    
    def _run_proc():
        return process_cbl_plan_to_output(clean_subj)
        
    res = await anyio.to_thread.run_sync(_run_proc)
    return res

@app.get("/api/planning/subject/{subject_name}/download-final")
def download_final_plan(subject_name: str):
    """Descarga el documento final procesado en Word."""
    from fastapi.responses import FileResponse
    clean_subj = sanitize_folder_name(subject_name)
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()
    base_dir = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.join(base_dir, "uploads", f"{clean_subj}-REV", "planificacion", "salida")
    
    cand_name = f"PLAN_MODULAR_{clean_subj.replace(' ', '_')}.docx"
    file_path = os.path.join(out_dir, cand_name)
    
    if not os.path.exists(file_path):
        # Buscar cualquier docx en la carpeta de salida
        if os.path.exists(out_dir):
            files = [f for f in os.listdir(out_dir) if f.endswith(".docx")]
            if files:
                file_path = os.path.join(out_dir, files[0])
                
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="No se ha procesado el documento final aún. Haz clic en 'Procesar Documento Final'.")
        
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/api/planning/subject/{subject_name}/drive-script")
def get_subject_drive_script(subject_name: str):
    """Retorna el código de Google Apps Script preconfigurado con las carpetas de la materia."""
    import datetime
    clean_subj = sanitize_folder_name(subject_name)
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()
    
    script_cbl = f"""/**
 * MOTOR DE INYECCIÓN MODULAR CBL (Google Apps Script)
 * Asignatura: {clean_subj}
 * Fecha de generación: {datetime.date.today().strftime('%d/%m/%Y')}
 */
function procesarCBL_{re.sub(r'[^a-zA-Z0-9]', '_', clean_subj)}() {{
  const ID_CARPETA_ENTRADA = "{{{{ID_CARPETA_ENTRADA}}}}"; // Reemplazar con ID de carpeta Drive entrada
  const ID_CARPETA_SALIDA  = "{{{{ID_CARPETA_SALIDA}}}}";  // Reemplazar con ID de carpeta Drive salida
  const ID_PLANTILLA_DOC   = "{{{{ID_PLANTILLA_DOC}}}}";   // Reemplazar con ID de Plantilla_CBL_Modular en Drive

  const carpetaEntrada = DriveApp.getFolderById(ID_CARPETA_ENTRADA);
  const carpetaSalida  = DriveApp.getFolderById(ID_CARPETA_SALIDA);
  const plantilla      = DriveApp.getFileById(ID_PLANTILLA_DOC);

  const archivos = carpetaEntrada.getFilesByType(MimeType.GOOGLE_DOCS);
  while (archivos.hasNext()) {{
    let archivoBorrador = archivos.next();
    let nombreOrig = archivoBorrador.getName();
    if (nombreOrig.endsWith("_PROCESADO") || nombreOrig.startsWith("PLAN_")) continue;

    let docOrigen = DocumentApp.openById(archivoBorrador.getId());
    let texto = docOrigen.getBody().getText();
    let mapa = mapearEtiquetas(texto);

    let nombreFinal = `PLAN_MODULAR_{clean_subj.replace(' ', '_')}_${{Utilities.formatDate(new Date(), "GMT-4", "yyyyMMdd")}}`;
    let nuevoDoc = plantilla.makeCopy(nombreFinal, carpetaSalida);
    let docFinal = DocumentApp.openById(nuevoDoc.getId());
    let cuerpo = docFinal.getBody();

    Object.keys(mapa).forEach(tag => {{
      let valor = mapa[tag];
      if (valor) {{
        cuerpo.replaceText(`\\\\[\\\\[${{tag}}\\\\]\\\\]`, valor);
        cuerpo.replaceText(`\\\\[${{tag}}\\\\]`, valor);
      }}
    }});

    docFinal.saveAndClose();
    archivoBorrador.setName(nombreOrig + "_PROCESADO");
  }}
}}

function mapearEtiquetas(texto) {{
  let mapa = {{}};
  let regex = /\\[INICIO:\\s*([^\\]]+?)\\s*\\]([\\s\\S]*?)\\[FIN:\\s*\\1\\s*\\]/gi;
  let match;
  while ((match = regex.exec(texto)) !== null) {{
    mapa[match[1].trim().toUpperCase()] = match[2].trim();
  }}
  return mapa;
}}
"""
    return {
        "subject_name": clean_subj,
        "script": script_cbl,
        "instructions": "1. Abre Google Drive y crea una carpeta de entrada y una de salida. 2. Abre script.google.com y crea un nuevo proyecto. 3. Pega este código y reemplaza los 3 IDs. 4. Presiona Ejecutar."
    }

# --- ENDPOINTS DE EVALUACIÓN MULTINIVEL (DUA, AC, ALERTAS) ---

@app.get("/api/instruments/catalog")
def get_instruments_catalog():
    """Retorna el catálogo de instrumentos con descripciones pedagógicas."""
    return {"catalog": CATALOGO_INSTRUMENTOS}

@app.get("/api/evaluation/plan/{subject_name}")
def get_subject_evaluation_plan(subject_name: str):
    """Retorna el plan de evaluación de la materia con adaptaciones e instrumentos sugeridos."""
    clean_subj = sanitize_folder_name(subject_name)
    plan = get_evaluation_plan(clean_subj)
    return plan

@app.post("/api/evaluation/plan/{subject_name}")
def save_subject_evaluation_plan(subject_name: str, payload: dict):
    """Guarda el plan de evaluación configurado por el docente para la materia."""
    clean_subj = sanitize_folder_name(subject_name)
    res = save_evaluation_plan(clean_subj, payload)
    return res

@app.get("/api/evaluation/students-dua/{subject_name}")
def list_students_dua(subject_name: str):
    """Retorna la lista de estudiantes con su perfil DUA e instrumentos sugeridos."""
    clean_subj = sanitize_folder_name(subject_name)
    return {"students": get_students_dua_profile_list(clean_subj)}

class StudentDuaUpdateRequest(BaseModel):
    student_id: str
    profile: dict

@app.post("/api/evaluation/students-dua/{subject_name}")
def update_student_dua(subject_name: str, req: StudentDuaUpdateRequest):
    """Guarda la personalización DUA de un estudiante específico."""
    clean_subj = sanitize_folder_name(subject_name)
    res = save_student_dua_profile(clean_subj, req.student_id, req.profile)
    return res

@app.get("/api/evaluation/students-dua/{subject_name}/export-docx")
def export_students_dua_docx(subject_name: str):
    """Genera y descarga la Matriz Institucional DUA en formato Word."""
    from fastapi.responses import FileResponse
    clean_subj = sanitize_folder_name(subject_name)
    doc_path = generate_dua_matrix_docx(clean_subj)
    return FileResponse(
        path=doc_path,
        filename=os.path.basename(doc_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

class RubricRequest(BaseModel):
    actividad_nombre: str
    competencia: Optional[str] = "Investigación y rigor metodológico"
    criterios_clave: Optional[List[str]] = None

@app.post("/api/evaluation/generate-rubric/{subject_name}")
async def generate_cbl_rubric(subject_name: str, req: RubricRequest):
    """Genera una rúbrica analítica CBL de 4 niveles adaptada a la actividad."""
    api_key = os.environ.get("GEMINI_API_KEY")
    prompt = f"""
    Eres un evaluador pedagógico experto en Aprendizaje Basado en Competencias (CBL).
    Asignatura: {subject_name}
    Actividad de Evaluación: {req.actividad_nombre}
    Competencia a evaluar: {req.competencia}
    
    Diseña una rúbrica analítica de 4 niveles:
    1. Emergente (1-50): Requiere andamiaje directo y presenta errores conceptuales.
    2. En Desarrollo (51-70): Aplica con soporte ocasional; requiere consolidar rigor.
    3. Competente (71-85): Demuestra maestría autónoma y evidencia sudor intelectual propio.
    4. Avanzado (86-100): Transfiere el conocimiento a nuevos problemas y reflexiona críticamente.
    
    Devuelve un JSON con:
    {{
      "actividad": "{req.actividad_nombre}",
      "competencia": "{req.competencia}",
      "criterios": [
        {{
          "dimension": "Criterio 1",
          "peso": "30%",
          "emergente": "Descriptor",
          "en_desarrollo": "Descriptor",
          "competente": "Descriptor",
          "avanzado": "Descriptor"
        }}
      ]
    }}
    """
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
            resp = await anyio.to_thread.run_sync(
                lambda: client.models.generate_content(
                    model=gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
            )
            rubric_res = json.loads((resp.text or "").strip())
            rubric_res["motor"] = gemini_model
            return rubric_res
        except Exception as e:
            print(f"[Rubric AI Fallback] {e}")

    # Fallback determinista
    return {
        "actividad": req.actividad_nombre,
        "competencia": req.competencia,
        "motor": "motor_determinista_local",
        "criterios": [
            {
                "dimension": "Rigor Epistémico y Comprensión Conceptual",
                "peso": "35%",
                "emergente": "Presenta conceptos desarticulados o copiados sin comprensión de base.",
                "en_desarrollo": "Define los conceptos correctamente pero le cuesta aplicarlos al problema.",
                "competente": "Aplica con precisión el marco conceptual demostrando esfuerzo intelectual autónomo.",
                "avanzado": "Sintetiza posturas teóricas con visión crítica y propone perspectivas originales."
            },
            {
                "dimension": "Procedimiento y Evidencia de Proceso (Sudor Intelectual)",
                "peso": "35%",
                "emergente": "Sin evidencia de iteración o entrega producto final automatizado sin justificación.",
                "en_desarrollo": "Muestra algunos borradores pero con saltos lógicos en la resolución.",
                "competente": "Documenta un proceso reflexivo claro, justificando cada decisión metodológica.",
                "avanzado": "Demuestra maestría en la resolución de contingencias metodológicas imprevistas."
            },
            {
                "dimension": "Sustentación Oral y Defensa Socrática (Anti-Outsourcing)",
                "peso": "30%",
                "emergente": "Incapaz de explicar verbalmente las decisiones tomadas en el documento escrito.",
                "en_desarrollo": "Explica la estructura general pero duda ante preguntas de profundización.",
                "competente": "Defiende con solidez y solvencia verbal cada apartado de su trabajo.",
                "avanzado": "Argumenta con solvencia y debate constructivamente alternativas metodológicas."
            }
        ]
    }

class ExportRubricRequest(BaseModel):
    actividad: str
    competencia: str
    criterios: List[Dict[str, Any]]

@app.post("/api/evaluation/export-rubric-docx")
def export_rubric_docx(req: ExportRubricRequest):
    """Exporta la rúbrica generada a un documento Word (.docx) formal."""
    import tempfile
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    from fastapi.responses import FileResponse

    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title.add_run("RÚBRICA ANALÍTICA DE EVALUACIÓN POR COMPETENCIAS (CBL)")
    r_title.bold = True
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub.add_run(f"Actividad: {req.actividad} | Competencia: {req.competencia}")
    r_sub.italic = True
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph()

    table = doc.add_table(rows=1, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Criterio / Dimensión", "Peso", "1. Emergente\n(1-50)", "2. En Desarrollo\n(51-70)", "3. Competente\n(71-85)", "4. Avanzado\n(86-100)"]
    hdr_cells = table.rows[0].cells
    for idx, text in enumerate(headers):
        hdr_cells[idx].text = text
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1A3A5C"/>')
        hdr_cells[idx]._tc.get_or_add_tcPr().append(shd)
        for p in hdr_cells[idx].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for crit in req.criterios:
        row = table.add_row()
        c = row.cells
        c[0].text = str(crit.get("dimension", ""))
        c[1].text = str(crit.get("peso", ""))
        c[2].text = str(crit.get("emergente", ""))
        c[3].text = str(crit.get("en_desarrollo", ""))
        c[4].text = str(crit.get("competente", ""))
        c[5].text = str(crit.get("avanzado", ""))
        for i in range(6):
            for p in c[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8.5)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx", prefix="RUBRICA_")
    temp_path = temp_file.name
    temp_file.close()
    doc.save(temp_path)

    clean_act = re.sub(r'[<>:"/\\|?*]', '', req.actividad).strip()
    filename = f"RUBRICA_CBL_{clean_act[:25]}.docx"
    return FileResponse(
        path=temp_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

class StudentDuaSuggestRequest(BaseModel):
    student_id: str
    iniciales: str
    promedio: float
    iteraciones: int
    alerta_outsourcing: bool
    riesgo_alto: bool
    observaciones_previas: Optional[str] = ""

async def call_gemini_with_fallback(prompt: str, config=None, preferred_model: Optional[str] = None):
    """Llama a Gemini con reintento automático en modelos flash disponibles para mitigar spikes 503."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Gemini Init Error]: {e}")
        return None, None

    primary = preferred_model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    fallback_models = [primary, "gemini-3.5-flash-lite", "gemini-3.6-flash"]
    models_to_try = []
    for m in fallback_models:
        if m and m not in models_to_try:
            models_to_try.append(m)

    for model_name in models_to_try:
        try:
            resp = await anyio.to_thread.run_sync(
                lambda: client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
            )
            if resp and resp.text:
                return resp.text, model_name
        except Exception as e:
            print(f"[Gemini Fallback - {model_name}]: {str(e)[:120]}")
            continue

    return None, None

@app.post("/api/evaluation/suggest-dua/{subject_name}")
async def suggest_student_dua_profile(subject_name: str, req: StudentDuaSuggestRequest):
    """Sugiere adaptaciones pedagógicas personalizadas según el marco DUA (CAST 2024) utilizando Gemini."""
    canonical_name, rev_dir = resolve_subject_folder(subject_name)
    
    prompt = f"""
    Eres un especialista en Diseño Universal para el Aprendizaje (DUA, marco CAST 2024) y Pedagogía Crítica (Paulo Freire).
    Asignatura: {canonical_name}
    Estudiante: {req.iniciales} (ID: {req.student_id})
    Métricas de Aula:
    - Promedio de Calificaciones: {req.promedio}/100
    - Sudor Intelectual / Iteraciones de Prompts: {req.iteraciones}
    - Alerta de Outsourcing Cognitivo: {'SÍ (Posible uso de IA como muleta sin autoría real)' if req.alerta_outsourcing else 'NO'}
    - Situación de Riesgo Académico: {'SÍ (Rezago formativo)' if req.riesgo_alto else 'NO'}
    - Observaciones previas: {req.observaciones_previas or 'Ninguna'}
    
    Genera una propuesta de adaptación DUA integral y equilibrada respondiendo con este JSON exacto:
    {{
      "principio_1_compromiso": "Estrategia para captar interés, mantener el esfuerzo y autorregulación emocional",
      "principio_2_representacion": "Formato de presentación de contenidos (organizadores visuales, audio, formato dual, etc.)",
      "principio_3_accion_expresion": "Canal de demostración del aprendizaje (defensa oral, portafolio, informe, micro-entrevista)",
      "instrumento_clave": "Nombre del instrumento sugerido (ej: Guía de Triangulación Socrática, Micro-quizzes, Rúbrica CBL)",
      "tiempo_extendido": true o false,
      "evaluacion_fragmentada": true o false,
      "observaciones": "Fundamentación pedagógica breve (2-3 líneas) explicando por qué esta adaptación promueve el músculo intelectual del estudiante sin reducir el rigor epistémico."
    }}
    """
    try:
        from google.genai import types
        cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.3)
    except Exception:
        cfg = None

    text_resp, model_used = await call_gemini_with_fallback(prompt, config=cfg)
    if text_resp:
        try:
            res_json = json.loads(text_resp.strip())
            res_json["motor"] = model_used
            return res_json
        except Exception as e:
            print(f"[DUA JSON Parse Error]: {e}")

    # Fallback determinista
    if req.alerta_outsourcing:
        p1 = "Coloquio socrático focalizado: metas de autoría personal y diálogo argumentativo."
        p2 = "Andamiaje inverso: solicitar el mapa mental del proceso de redacción."
        p3 = "Defensa oral socrática individual (Triangulación Socrática obligatoria)."
        inst = "Guía de Triangulación Socrática"
        t_ext = False
        frag = False
        obs = "Se prioriza la contrastación dialógica verbal para prevenir el outsourcing cognitivo y validar el esfuerzo reflexivo propio."
    elif req.riesgo_alto:
        p1 = "Metas cortas y refuerzo formativo continuo para mitigar la frustración."
        p2 = "Organizadores gráficos y guías estructuradas paso a paso con formato dual."
        p3 = "Evaluación fragmentada por hitos pequeños con retroalimentación formativa."
        inst = "Batería de Micro-quizzes Tempranos"
        t_ext = True
        frag = True
        obs = "Adaptación orientada a andamiar la Zona de Desarrollo Próximo (ZDP) y fortalecer prerrequisitos esenciales."
    else:
        p1 = "Elección autónoma de problemas reales de investigación dentro del área temática."
        p2 = "Textos académicos enriquecidos con diagramas de flujo metodológicos."
        p3 = "Portafolio digital de evidencias de investigación con rúbrica CBL analítica."
        inst = "Matriz de Hitos y Rúbrica CBL"
        t_ext = False
        frag = False
        obs = "Perfil estándar con promoción de autonomía y transferencia crítica."

    return {
        "principio_1_compromiso": p1,
        "principio_2_representacion": p2,
        "principio_3_accion_expresion": p3,
        "instrumento_clave": inst,
        "tiempo_extendido": t_ext,
        "evaluacion_fragmentada": frag,
        "observaciones": obs,
        "motor": "motor_determinista_local"
    }

class CopilotMessage(BaseModel):
    role: str
    content: str

class CopilotChatRequest(BaseModel):
    subject_name: Optional[str] = ""
    message: str
    history: Optional[List[CopilotMessage]] = []

@app.post("/api/copilot/chat")
async def pedagogical_copilot_chat(req: CopilotChatRequest):
    """Copiloto Pedagógico Inteligente con Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    context_info = "Sin materia seleccionada en este momento."
    if req.subject_name:
        canonical_name, rev_dir = resolve_subject_folder(req.subject_name)
        man_path = os.path.join(rev_dir, "manifiesto.json")
        ins_path = os.path.join(rev_dir, "bases_de_datos", "insights.json")
        
        manifest = {}
        if os.path.exists(man_path):
            try:
                with open(man_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                pass
                
        insights = {}
        if os.path.exists(ins_path):
            try:
                with open(ins_path, "r", encoding="utf-8") as f:
                    insights = json.load(f)
            except Exception:
                pass
                
        context_info = f"""
        Materia Activa: {canonical_name}
        Datos Curriculares: Nivel {manifest.get('level', 'Superior')}, Sistema {manifest.get('system', 'Superior')}, Periodo {manifest.get('period', '1')}.
        Problema del Contexto: {manifest.get('description', 'Formación en investigación y rigor epistémico')}.
        Diagnóstico de Aula: Total estudiantes: {insights.get('total_estudiantes', 0)}, Promedio: {insights.get('promedio_general', 'N/A')}, Casos de Riesgo: {insights.get('estudiantes_riesgo_count', 0)}, Alertas de Outsourcing Cognitivo: {insights.get('estudiantes_outsourcing_count', 0)}.
        """

    system_prompt = f"""
    Eres el "Copiloto Pedagógico" de Carpeta Pedagógica 2.0. Eres un mentor de élite en docencia universitaria y escolar, especialista en:
    1. Aprendizaje Basado en Competencias (CBL) y taxonomías de desempeño auténtico.
    2. Diseño Universal para el Aprendizaje (DUA, marco CAST 2024: Compromiso, Representación, Acción/Expresión).
    3. Prevención del "Outsourcing Cognitivo" y fomento del sudor intelectual propio (Paulo Freire, John Dewey, Lev Vygotsky ZDP, John Hattie d=1.16).
    4. Evaluación Formativa, rúbricas analíticas y Triangulación Socrática dialógica.
    
    Contexto de la materia actual:
    {context_info}
    
    Instrucciones para tus respuestas:
    - Sé conciso, claro, estructurado y directamente accionable para el docente en el aula.
    - Usa markdown con viñetas, negritas y llamadas claras.
    - Si te preguntan por evaluación o casos de alumnos, sugiere instrumentos específicos del catálogo de Carpeta Pedagógica 2.0 (Triangulación Socrática, Micro-quizzes, Registro de Sudor Intelectual, Rúbrica CBL, Ficha Socioeducativa o Ficha de Autoevaluación).
    - Mantén un tono cálido, colegiado y motivador.
    """

    history_text = ""
    for h in (req.history or [])[-6:]:
        prefix = "Docente" if h.role == "user" else "Copiloto"
        history_text += f"{prefix}: {h.content}\n\n"
        
    full_prompt = f"{system_prompt}\n\nHistorial de Conversación Reciente:\n{history_text}\nDocente: {req.message}\nCopiloto:"
    
    try:
        from google.genai import types
        cfg = types.GenerateContentConfig(temperature=0.4)
    except Exception:
        cfg = None

    text_resp, model_used = await call_gemini_with_fallback(full_prompt, config=cfg)
    if text_resp:
        return {
            "reply": text_resp.strip(),
            "motor": model_used,
            "subject_name": req.subject_name
        }

    reply = f"""
    ### 🧭 Sugerencia del Copiloto (Modo Local)
    
    Para la materia **{req.subject_name or 'seleccionada'}**, te sugiero considerar las siguientes directrices pedagógicas:
    
    1. **Validación del Sudor Intelectual:** Si detectas trabajos con redacción avanzada pero pocas iteraciones de borradores, programa una **Triangulación Socrática** de 5 minutos pidiéndole al alumno que explique el porqué de sus fuentes clave.
    2. **Inclusión DUA:** Diversifica los formatos de entrega permitiendo tanto informes escritos como defensas en video-ensayo o mapas conceptuales interactivos.
    3. **Retroalimentación Formativa ($d=1.16$):** Aplica la *Ficha de Autoevaluación y Co-evaluación* antes de la entrega final para que los estudiantes autorregulen su propio desempeño.
    """
    return {
        "reply": reply.strip(),
        "motor": "motor_determinista_local",
        "subject_name": req.subject_name
    }

@app.post("/api/analytics/narrative/{subject_name}")
async def generate_analytics_narrative(subject_name: str):
    """Genera una síntesis ejecutiva pedagógica profunda con Gemini basada en los datos analíticos."""
    canonical_name, rev_dir = resolve_subject_folder(subject_name)
    ins_path = os.path.join(rev_dir, "bases_de_datos", "insights.json")
    if not os.path.exists(ins_path):
        raise HTTPException(status_code=404, detail="No hay insights analíticos generados para esta materia aún.")
        
    with open(ins_path, "r", encoding="utf-8") as f:
        insights = json.load(f)
        
    api_key = os.environ.get("GEMINI_API_KEY")
    prompt = f"""
    Eres un auditor académico y consultor en analítica de aprendizaje institucional.
    Genera un INFORME EJECUTIVO PEDAGÓGICO en Markdown para la asignatura "{canonical_name}" basado en estas métricas cuantitativas y cualitativas de aula:
    - Población analizada: {insights.get('total_estudiantes', 0)} estudiantes
    - Promedio general: {insights.get('promedio_general', 'N/A')}/100 (Mediana: {insights.get('mediana', 'N/A')})
    - Desviación Estándar: {insights.get('desviacion_estandar', 'N/A')}
    - Asimetría de Fisher (g1): {insights.get('asimetria_fisher', 'N/A')} ({insights.get('interpretacion_asimetria', '')})
    - Curtosis (g2): {insights.get('curtosis', 'N/A')}
    - Estudiantes en Riesgo Alto de Abandono/Rezago: {insights.get('estudiantes_riesgo_count', 0)}
    - Alertas de Outsourcing Cognitivo detectadas: {insights.get('estudiantes_outsourcing_count', 0)}
    - Muestra de perfiles de riesgo: {json.dumps(insights.get('casos_criticos', [])[:4], ensure_ascii=False)}
    
    Estructura requerida del informe en Markdown:
    # 📑 Diagnóstico Ejecutivo de Analítica del Aprendizaje
    ## 1. Clima y Madurez Académica del Aula
    (Diagnóstico interpretativo del grupo, analizando la dispersión y motivación).
    ## 2. Hallazgos Críticos y Vigilancia Epistémica
    (Análisis de la asimetría, brechas formativas y detección de outsourcing cognitivo).
    ## 3. Plan de Intervención Semanal (3 Acciones Inmediatas)
    (Paso 1, Paso 2 y Paso 3 concretos para el docente en el aula).
    ## 4. Recomendaciones para Acreditación y Dirección Académica
    (Impacto en tasas de retención y sugerencias de acompañamiento DUA).
    """

    try:
        from google.genai import types
        cfg = types.GenerateContentConfig(temperature=0.3)
    except Exception:
        cfg = None

    text_resp, model_used = await call_gemini_with_fallback(prompt, config=cfg)
    if text_resp:
        return {
            "status": "ok",
            "report": text_resp.strip(),
            "reporte_narrativo": text_resp.strip(),
            "motor": model_used
        }

    report = f"""
    # 📑 Diagnóstico Ejecutivo de Analítica del Aprendizaje
    **Materia:** {canonical_name} | **Motor:** Determinista Local
    
    ## 1. Clima y Madurez Académica del Aula
    El curso cuenta con **{insights.get('total_estudiantes', 0)} estudiantes evaluados**. El promedio general se sitúa en **{insights.get('promedio_general', 0):.1f}/100** con una dispersión de **{insights.get('desviacion_estandar', 0):.1f} puntos**. La asimetría calculada de Fisher ({insights.get('asimetria_fisher', 0):.2f}) refleja una concentración típica de estudiantes que requiere atención diferenciada.
    
    ## 2. Hallazgos Críticos y Vigilancia Epistémica
    - **{insights.get('estudiantes_riesgo_count', 0)} estudiantes** en situación de rezago académico temprano.
    - **{insights.get('estudiantes_outsourcing_count', 0)} estudiantes** con alerta de *outsourcing cognitivo* (notas elevadas pero desconexión de proceso iterativo).
    
    ## 3. Plan de Intervención Semanal
    1. **Triangulación Socrática:** Citar a los alumnos con alerta de outsourcing para contrastar verbalmente la formulación del problema de investigación.
    2. **Nivelación Temprana:** Aplicar la batería de micro-quizzes diagnósticos en la sesión siguiente.
    3. **Acompañamiento DUA:** Habilitar formatos flexibles de entrega (organizadores visuales + rúbrica analítica).
    
    ## 4. Recomendaciones para Dirección Académica
    Implementar el seguimiento de la matriz DUA institucional para garantizar la retención y equidad formativa.
    """
    return {
        "status": "ok",
        "report": report.strip(),
        "reporte_narrativo": report.strip(),
        "motor": "motor_determinista_local"
    }


@app.on_event("startup")
def on_startup():
    init_db()
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(base_dir, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la Carpeta Pedagógica 2.0"}

@app.post("/api/documents/analyze-spreadsheet")
async def upload_and_analyze(file: UploadFile = File(...)):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        raise HTTPException(status_code=400, detail="Solo se soportan archivos CSV o XLSX por ahora.")
        
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # El archivo está guardado, pasamos a analizar la estructura con Gemini
    analysis_result = analyze_spreadsheet_structure(file_location)
    
    return {
        "filename": file.filename,
        "message": "Archivo pre-procesado. Requiere autorización humana.",
        "ai_analysis": analysis_result
    }

@app.get("/api/documents/pending")
def get_pending_documents():
    """Devuelve las carpetas agrupadas por Materia y Versión."""
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    
    if not os.path.exists(base_dir):
        return {"subjects": []}
        
    subjects_dict = {}
    
    # Solo miramos el primer nivel de carpetas dentro de uploads
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and not item.startswith(('_', '.')):
            is_rev = item.endswith("-REV")
            base_name = item.replace("-REV", "") if is_rev else item
            
            if base_name not in subjects_dict:
                subjects_dict[base_name] = {"name": base_name, "versions": []}
            
            # Buscar archivos recursivamente dentro de esta versión
            files_list = []
            for root, _, files in os.walk(item_path):
                for f in files:
                    if f.endswith(('.xlsx', '.csv', '.docx', '.jpg')):
                        files_list.append({
                            "filename": f,
                            "path": os.path.relpath(os.path.join(root, f), base_dir).replace('\\', '/')
                        })
                        
            subjects_dict[base_name]["versions"].append({
                "name": "Integrada (-REV)" if is_rev else "Original",
                "folder_name": item,
                "files": files_list
            })
            
    # Convertir a lista y ordenar las versiones para que Original salga primero
    result = []
    for subj in subjects_dict.values():
        subj["versions"].sort(key=lambda x: x["name"], reverse=True)
        result.append(subj)
        
    return {"subjects": result}

@app.post("/api/documents/analyze-local")
async def analyze_local(filepath: str):
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    full_path = os.path.join(base_dir, filepath)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"File not found: {full_path}")
        
    analysis_result = analyze_spreadsheet_structure(full_path)
    return {
        "filename": os.path.basename(full_path),
        "message": "Archivo pre-procesado. Requiere autorización humana.",
        "ai_analysis": analysis_result
    }

@app.get("/api/analytics/{subject_name}")
def get_analytics(subject_name: str):
    """Devuelve los insights (JSON) y las llaves de nombres (JSON) de una materia."""
    canonical_name, rev_dir = resolve_subject_folder(subject_name)
    target_dir = os.path.join(rev_dir, "bases_de_datos")
    
    insights_path = os.path.join(target_dir, "insights.json")
    llave_path = os.path.join(target_dir, "llave_nombres.json")
    
    insights = {}
    llaves = {}
    
    if os.path.exists(insights_path):
        try:
            with open(insights_path, "r", encoding="utf-8") as f:
                insights = json.load(f)
        except Exception:
            pass
            
    if os.path.exists(llave_path):
        try:
            with open(llave_path, "r", encoding="utf-8") as f:
                llaves = json.load(f)
        except Exception:
            pass
            
    return {
        "insights": insights,
        "llaves": llaves
    }

@app.post("/api/stages/audit/{subject_name}/{stage_id}")
def audit_stage_data(subject_name: str, stage_id: str):
    """Audita la suficiencia de datos antes de ejecutar una etapa y devuelve trade-offs e instrumentos."""
    import pandas as pd
    clean_subj = sanitize_folder_name(subject_name)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    target_dir = os.path.join(base_dir, "uploads", f"{clean_subj}-REV", "bases_de_datos")
    
    file_to_check = None
    if stage_id == "e1":
        raw_dir = os.path.join(base_dir, "uploads", clean_subj)
        if os.path.exists(raw_dir):
            files = [f for f in os.listdir(raw_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
            if files:
                file_to_check = os.path.join(raw_dir, files[0])
    elif stage_id in ["e2", "e3"]:
        cand = os.path.join(target_dir, "BASE_INTEGRADA.xlsx")
        if os.path.exists(cand):
            file_to_check = cand
    elif stage_id == "e4":
        cand = os.path.join(target_dir, "BASE_LIMPIA_ANONIMIZADA.xlsx")
        if os.path.exists(cand):
            file_to_check = cand

    columns_found = []
    if file_to_check and os.path.exists(file_to_check):
        try:
            df = pd.read_excel(file_to_check, nrows=5)
            columns_found = [str(c).lower() for c in df.columns]
        except Exception:
            pass

    # Evaluación de Dimensiones Científicas y Enfoque Humano
    has_performance = any(k in " ".join(columns_found) for k in ["nota", "examen", "parcial", "practica", "puntaje", "promedio"])
    has_competency = any(k in " ".join(columns_found) for k in ["competencia", "hito", "proficiencia", "rubrica", "logro", "cbl"])
    has_interaction = any(k in " ".join(columns_found) for k in ["quiz", "cuestionario", "diagnostico", "plataforma", "click", "interaccion", "micro"])
    has_socio = any(k in " ".join(columns_found) for k in ["trabajo", "empleo", "tutor", "convivencia", "hijos", "socio", "conectividad", "edad"])
    has_affective = any(k in " ".join(columns_found) for k in ["autoevaluacion", "reflexion", "sentimiento", "confianza", "frustracion", "coraje", "bitacora"])
    
    # NUEVAS DIMENSIONES (Sudor Intelectual y DUA)
    has_process = any(k in " ".join(columns_found) for k in ["prompt", "iteracion", "dialogo", "participacion", "esfuerzo", "autonomia"])
    has_dua = any(k in " ".join(columns_found) for k in ["formato", "expresion", "oral", "visual", "performativo", "dua"])

    detected = []
    missing = []

    if has_competency:
        detected.append({"id": "cbl", "name": "Competencias (CBL)", "detail": "Descriptores de maestría"})
    else:
        missing.append({"id": "cbl", "name": "Matriz de Hitos (CBL)", "impact": "Impide detectar si una nota baja se debe a teoría o a práctica"})

    if has_interaction:
        detected.append({"id": "interaction", "name": "Interacción (Semana 1)", "detail": "Datos de participación temprana"})
    else:
        missing.append({"id": "interaction", "name": "Micro-quizzes (Semana 1)", "impact": "Impide alerta temprana en Semana 1"})

    if has_process:
        detected.append({"id": "process", "name": "Sudor Intelectual / Proceso", "detail": "Evidencia de esfuerzo e iteración (Anti-Outsourcing)"})
    else:
        missing.append({"id": "process", "name": "Sudor Intelectual (Métricas Cualitativas)", "impact": "Peligro de Educación Bancaria (Freire). Riesgo de Outsourcing Cognitivo al no medir el esfuerzo del estudiante."})

    if has_dua:
        detected.append({"id": "dua", "name": "Inclusión y DUA", "detail": "Registro de formatos múltiples de expresión"})
    else:
        missing.append({"id": "dua", "name": "Inclusión (Métricas DUA)", "impact": "Posible sesgo hacia la evaluación tradicional escrita (Currículo Oculto)."})

    # Trade-offs específicos
    if stage_id == "e1":
        ventajas = [
            "Procesamiento rápido con la información disponible."
        ]
        desventajas = [
            "Análisis superficial basado en notas (Educación Bancaria).",
            "Imposibilidad de detectar si el estudiante delegó su aprendizaje a la IA (Outsourcing Cognitivo)."
        ]
        sugerencia = {
            "instrument_id": "registro_sudor",
            "name": "Registro de Sudor Intelectual y DUA",
            "description": "Plantilla Excel para documentar el nivel de iteración de prompts y participación.",
            "benefit": "Permite medir el esfuerzo real del alumno y detectar el uso de IA como muleta vs copiloto."
        }
    elif stage_id == "e3":
        ventajas = [
            "Genera el informe con clasificaciones de riesgo automáticas."
        ]
        desventajas = [
            "Si faltan variables de proceso, el modelo no podrá sugerir 'Triangulación Socrática'."
        ]
        sugerencia = {
            "instrument_id": "triangulacion",
            "name": "Guía de Triangulación Socrática",
            "description": "Documento para entrevistar a estudiantes con trabajos 'sospechosamente perfectos'.",
            "benefit": "Previene el Outsourcing Cognitivo validando el 'músculo intelectual' verbalmente."
        }
    else:
        ventajas = [
            "Construye la vista de analítica con la información que se tenga."
        ]
        desventajas = [
            "Los gráficos de Deci & Ryan (Autonomía/Competencia) no se generarán en el Dashboard por falta de datos cualitativos."
        ]
        sugerencia = {
            "instrument_id": "registro_sudor",
            "name": "Registro de Sudor Intelectual",
            "description": "Herramienta vital para alimentar el Dashboard de Enfoque Humano.",
            "benefit": "Visibilidad total del proceso de aprendizaje."
        }

    status = "completo" if len(missing) == 0 else "parcial" if len(detected) > 0 else "critico"

    return {
        "stage_id": stage_id,
        "subject_name": subject_name,
        "status": status,
        "columns_detected": columns_found,
        "dimensions_detected": detected,
        "dimensions_missing": missing,
        "trade_offs": {
            "ventajas": ventajas,
            "desventajas": desventajas
        },
        "instrument_suggested": sugerencia
    }

@app.get("/api/instruments/download/{instrument_type}")
def download_instrument(instrument_type: str):
    """Descarga plantillas de instrumentos para recolectar datos faltantes."""
    from fastapi.responses import Response
    from instruments import (
        generate_rubrica_cbl,
        generate_micro_quizzes,
        generate_ficha_socioeducativa,
        generate_ficha_autorregulacion,
        generate_registro_sudor_intelectual,
        generate_triangulacion_socratica
    )
    
    generators = {
        "rubrica_cbl": generate_rubrica_cbl,
        "micro_quizzes": generate_micro_quizzes,
        "ficha_socioeducativa": generate_ficha_socioeducativa,
        "ficha_autorregulacion": generate_ficha_autorregulacion,
        "self_peer_assessment": generate_ficha_autorregulacion,
        "registro_sudor": generate_registro_sudor_intelectual,
        "triangulacion": generate_triangulacion_socratica
    }
    
    gen_fn = generators.get(instrument_type)
    if not gen_fn:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")
        
    content, filename, media_type = gen_fn()
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/documents/export-anonymized/{subject_name}")
def export_anonymized_dataset(subject_name: str, format: str = "xlsx"):
    """Permite exportar el dataset anonimizado y limpio para análisis en R, SPSS, Stata o Python."""
    from fastapi.responses import FileResponse, Response
    import pandas as pd
    import io
    
    clean_subj = sanitize_folder_name(subject_name)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    target_dir = os.path.join(base_dir, "uploads", f"{clean_subj}-REV", "bases_de_datos")
    
    xlsx_path = os.path.join(target_dir, "BASE_LIMPIA_ANONIMIZADA.xlsx")
    if not os.path.exists(xlsx_path):
        xlsx_path = os.path.join(target_dir, "BASE_INTEGRADA.xlsx")
        
    if not os.path.exists(xlsx_path):
        raise HTTPException(status_code=404, detail="No se encontró dataset procesado para esta materia. Ejecuta la Etapa 1 o 2.")
        
    if format == "csv":
        df = pd.read_excel(xlsx_path)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8")
        return Response(
            content=csv_buffer.getvalue().encode("utf-8"),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="DATASET_ANONIMIZADO_{clean_subj}.csv"'}
        )
    else:
        return FileResponse(
            path=xlsx_path,
            filename=f"DATASET_ANONIMIZADO_{clean_subj}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

@app.get("/api/documents/export-carpeta-completa/{subject_name}")
def export_consolidated_carpeta_pedagogica(subject_name: str):
    """Genera y descarga el Dossier Completo Oficial (Carpeta Pedagógica 2.0 Consolidada) en Word."""
    from fastapi.responses import FileResponse
    from dossier_service import build_consolidated_carpeta_docx
    clean_subj = sanitize_folder_name(subject_name)
    if clean_subj.endswith("-REV"):
        clean_subj = clean_subj[:-4].strip()
        
    doc_path = build_consolidated_carpeta_docx(clean_subj)
    return FileResponse(
        path=doc_path,
        filename=os.path.basename(doc_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/api/settings/drive-status")
def get_google_drive_status():
    """Retorna el estado de configuración de la API de Google Drive o el modo de contingencia activo."""
    from drive_service import get_drive_status
    return get_drive_status()

class GeminiKeyRequest(BaseModel):
    api_key: str

@app.get("/api/settings/gemini-status")
def get_gemini_status():
    """Retorna el estado de la API de Gemini o el modo de contingencia activo."""
    from dotenv import load_dotenv
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_file, override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    active_model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    if api_key and api_key.strip():
        masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        return {
            "configured": True,
            "status": "activo",
            "message": f"API de Gemini configurada ({active_model}) y lista para análisis cualitativo y prescriptivo.",
            "masked_key": masked,
            "model": active_model
        }
    else:
        return {
            "configured": False,
            "status": "motor_local",
            "message": "Modo de Contingencia Activo: Operando con motor determinista y no paramétrico local (Spearman ρ, Fisher g1, Curtosis g2, Vygotsky ZDP). Para enriquecer los análisis con narrativa de IA, configura tu clave de Google AI Studio.",
            "masked_key": None,
            "model": "motor_determinista_local"
        }

@app.post("/api/settings/gemini-key")
async def save_gemini_key(req: GeminiKeyRequest):
    """Valida la clave contra Google AI Studio en vivo mediante ListModels dinámico, la persiste en .env y actualiza el entorno."""
    new_key = req.api_key.strip()
    if not new_key:
        raise HTTPException(status_code=400, detail="La clave no puede estar vacía.")
        
    validated_model = None
    last_error = None
    
    try:
        from google import genai
        client = genai.Client(api_key=new_key)
        
        # 1. Consultar ModelService.ListModels para descubrir qué modelos soporta esta clave
        discovered_models = []
        try:
            def _get_models():
                valid_models = []
                for m in client.models.list():
                    actions = getattr(m, 'supported_actions', []) or []
                    # Modelos que soportan generateContent
                    if not actions or any('generatecontent' in str(a).lower() for a in actions):
                        name = getattr(m, 'name', '') or ''
                        if name:
                            valid_models.append(name)
                return valid_models
                
            discovered_models = await anyio.to_thread.run_sync(_get_models)
            print(f"[Google AI Studio] Modelos disponibles para la clave: {discovered_models}")
        except Exception as list_err:
            print(f"[Google AI Studio] Error en ListModels: {list_err}")
            err_str = str(list_err)
            if "API_KEY_INVALID" in err_str or "API key not valid" in err_str or "400" in err_str:
                return {
                    "success": False,
                    "status": "motor_local",
                    "message": "La clave de Google AI Studio es inválida o expiró. Por favor verifica que copiaste la clave completa de tu proyecto."
                }
            last_error = err_str

        # 2. Priorizar modelos candidatos: primero flash no preview, luego flash, luego pro
        candidate_models = []
        if discovered_models:
            def _model_priority(name: str) -> int:
                n = name.lower().replace("models/", "")
                if "flash" in n and "preview" not in n and "exp" not in n:
                    return 1
                if "flash" in n:
                    return 2
                if "pro" in n and "preview" not in n and "exp" not in n:
                    return 3
                if "pro" in n:
                    return 4
                return 5
                
            candidate_models = sorted(discovered_models, key=_model_priority)
            
        # Respaldo en caso de que list() retorne vacío
        fallback_candidates = [
            "gemini-2.0-flash",
            "models/gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "models/gemini-2.0-flash-lite",
            "gemini-2.5-flash",
            "models/gemini-2.5-flash",
            "gemini-1.5-flash",
            "models/gemini-1.5-flash"
        ]
        for fb in fallback_candidates:
            if fb not in candidate_models:
                candidate_models.append(fb)
                
        # 3. Probar generar contenido con los modelos candidatos
        for cand_model in candidate_models:
            try:
                def _test_gemini(m=cand_model):
                    return client.models.generate_content(
                        model=m,
                        contents='Responde únicamente con la palabra OK.'
                    )
                    
                test_response = await anyio.to_thread.run_sync(_test_gemini)
                if test_response and test_response.text:
                    validated_model = cand_model
                    print(f"[Google AI Studio] ¡Modelo validado exitosamente: {validated_model}!")
                    break
            except Exception as ex:
                last_error = str(ex)
                continue
                
        if not validated_model:
            return {
                "success": False,
                "status": "motor_local",
                "message": f"Fallo de validación con Google AI Studio: {last_error}. Se mantiene activo el motor determinista local como contingencia pedagógica."
            }
    except Exception as e:
        return {
            "success": False,
            "status": "motor_local",
            "message": f"Fallo de inicialización de cliente Google AI Studio: {str(e)}. Se mantiene activo el motor determinista local."
        }
        
    # Persistir en backend/.env tanto GEMINI_API_KEY como GEMINI_MODEL
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    key_found = False
    model_found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("GEMINI_API_KEY="):
            new_lines.append(f"GEMINI_API_KEY={new_key}\n")
            key_found = True
        elif line.strip().startswith("GEMINI_MODEL="):
            new_lines.append(f"GEMINI_MODEL={validated_model}\n")
            model_found = True
        else:
            new_lines.append(line)
            
    if not key_found:
        new_lines.append(f"\nGEMINI_API_KEY={new_key}\n")
    if not model_found:
        new_lines.append(f"GEMINI_MODEL={validated_model}\n")
        
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    # Actualizar en memoria del proceso
    os.environ["GEMINI_API_KEY"] = new_key
    os.environ["GEMINI_MODEL"] = validated_model
    
    masked = f"{new_key[:4]}...{new_key[-4:]}" if len(new_key) > 8 else "***"
    return {
        "success": True,
        "status": "activo",
        "message": f"¡Clave validada exitosamente con el modelo {validated_model} de Google AI Studio y guardada en el sistema!",
        "masked_key": masked,
        "model": validated_model
    }

# ==============================================================================
# MÓDULOS DE ADMINISTRACIÓN, PERFIL DE USUARIO Y LICENCIAMIENTO EDUCATIVO
# ==============================================================================

class UserProfileModel(BaseModel):
    nombre: Optional[str] = "Luis Alfredo Andia Valverde"
    titulo: Optional[str] = "Docente e Investigador Educativo"
    institucion: Optional[str] = "Universidad / Comunidad Académica"
    email: Optional[str] = "luis.andia.valverde@gmail.com"
    bio: Optional[str] = "Creador y desarrollador de Carpeta Pedagógica 2.0. Docente comprometido con el Aprendizaje Basado en Competencias (CBL), el Diseño Universal para el Aprendizaje (DUA marco CAST 2024) y la pedagogía crítica contra el outsourcing cognitivo."
    marco_predeterminado: Optional[str] = "cbl_cast"
    sensibilidad_outsourcing: Optional[str] = "normal"
    tolerancia_rezago: Optional[str] = "estricta"

@app.get("/api/user/profile")
def get_user_profile():
    """Retorna el perfil del docente configurado en la plataforma."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    profile_path = os.path.join(base_dir, "uploads", "user_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "nombre": "Luis Alfredo Andia Valverde",
        "titulo": "Docente e Investigador Educativo",
        "institucion": "Universidad / Comunidad Académica",
        "email": "luis.andia.valverde@gmail.com",
        "bio": "Creador y desarrollador de Carpeta Pedagógica 2.0. Docente comprometido con el Aprendizaje Basado en Competencias (CBL), el Diseño Universal para el Aprendizaje (DUA marco CAST 2024) y la pedagogía crítica contra el outsourcing cognitivo.",
        "marco_predeterminado": "cbl_cast",
        "sensibilidad_outsourcing": "normal",
        "tolerancia_rezago": "estricta",
        "autor": "Luis Alfredo Andia Valverde",
        "email_autor": "luis.andia.valverde@gmail.com",
        "licencia": "Autorizada su distribución y uso sin beneficio comercial (CC BY-NC 4.0)"
    }

@app.post("/api/user/profile")
def update_user_profile(profile: UserProfileModel):
    """Guarda o actualiza las preferencias del perfil docente."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    uploads_dir = os.path.join(base_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    profile_path = os.path.join(uploads_dir, "user_profile.json")
    data = profile.dict()
    data["autor"] = "Luis Alfredo Andia Valverde"
    data["email_autor"] = "luis.andia.valverde@gmail.com"
    data["licencia"] = "Autorizada su distribución y uso sin beneficio comercial (CC BY-NC 4.0)"
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "profile": data}

@app.get("/api/system/stats")
def get_system_stats():
    """Retorna estadísticas de salud del sistema, almacenamiento y versión."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    uploads_dir = os.path.join(base_dir, "uploads")
    
    total_size = 0
    total_files = 0
    subjects_count = 0
    subjects_list = []
    if os.path.exists(uploads_dir):
        for item in os.listdir(uploads_dir):
            item_path = os.path.join(uploads_dir, item)
            if os.path.isdir(item_path) and not item.startswith(('_', '.')):
                if not item.endswith("-REV"):
                    subjects_count += 1
                    subjects_list.append(item)
                for root, _, files in os.walk(item_path):
                    for f in files:
                        total_files += 1
                        try:
                            total_size += os.path.getsize(os.path.join(root, f))
                        except Exception:
                            pass

    total_mb = round(total_size / (1024 * 1024), 2)
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    
    return {
        "version": "1.0.0 (Personal & Educational Edition)",
        "autor": "Luis Alfredo Andia Valverde",
        "email_autor": "luis.andia.valverde@gmail.com",
        "licencia": "Autorizada su distribución y uso sin beneficio comercial (CC BY-NC 4.0)",
        "total_materias": subjects_count,
        "materias": subjects_list,
        "total_archivos": total_files,
        "espacio_utilizado_mb": total_mb,
        "gemini_activo": bool(gemini_key),
        "gemini_modelo": gemini_model if gemini_key else "motor_local_determinista",
        "estado_sistema": "Óptimo",
        "storage_dir": uploads_dir
    }

# ==============================================================================
# CONECTORES LMS (MOODLE • GOOGLE CLASSROOM • MICROSOFT TEAMS)
# ==============================================================================

class LmsDetectRequest(BaseModel):
    columns: List[str]

@app.post("/api/lms/detect-format")
def detect_lms_format(req: LmsDetectRequest):
    """Detecta automáticamente si la planilla de notas proviene de Moodle, Classroom, Teams o Excel genérico."""
    cols_lower = [c.lower() for c in req.columns]
    cols_str = " ".join(cols_lower)
    
    if any(k in cols_str for k in ["número de id", "numero de id", "id number", "institución", "departamento"]) and any(k in cols_str for k in ["tarea:", "cuestionario:", "feedback", "retroalimentación"]):
        lms = "moodle"
        name = "Moodle LMS"
        confidence = 0.95
        id_col = next((c for c in req.columns if any(k in c.lower() for k in ["id", "identificador", "número"])), req.columns[0] if req.columns else "")
    elif any(k in cols_str for k in ["dirección de correo electrónico", "email address"]) and any(k in cols_str for k in ["nombre", "apellidos", "classroom"]):
        lms = "classroom"
        name = "Google Classroom"
        confidence = 0.90
        id_col = next((c for c in req.columns if any(k in c.lower() for k in ["correo", "email", "alumno"])), req.columns[0] if req.columns else "")
    elif any(k in cols_str for k in ["teams", "assignment", "puntos de retroalimentación", "feedback points"]):
        lms = "teams"
        name = "Microsoft Teams Educación"
        confidence = 0.90
        id_col = next((c for c in req.columns if any(k in c.lower() for k in ["correo", "email", "nombre"])), req.columns[0] if req.columns else "")
    else:
        lms = "standard"
        name = "Planilla Excel Estándar"
        confidence = 0.80
        id_col = req.columns[0] if req.columns else ""
        
    return {
        "lms": lms,
        "name": name,
        "confidence": confidence,
        "student_id_column": id_col,
        "recommendation": f"Estructura identificada como {name}. Mapeo directo activado para el pipeline de 4 etapas."
    }

@app.get("/api/lms/export-feedback/{subject_name}")
def export_lms_feedback(subject_name: str, target_lms: str = "moodle"):
    """Exporta el feedback formativo y recomendaciones DUA formateadas para importar en Moodle, Classroom o Teams."""
    import pandas as pd
    import io
    from fastapi.responses import Response
    
    canonical_name, rev_dir = resolve_subject_folder(subject_name)
    dua_path = os.path.join(rev_dir, "bases_de_datos", "dua_profiles.json")
    insights_path = os.path.join(rev_dir, "bases_de_datos", "insights.json")
    
    dua_data = {}
    if os.path.exists(dua_path):
        try:
            with open(dua_path, "r", encoding="utf-8") as f:
                dua_data = json.load(f)
        except Exception:
            pass

    records = []
    # Si hay perfiles DUA, exportamos sus observaciones
    if dua_data:
        for st_id, prof in dua_data.items():
            feedback_text = f"Compromiso: {prof.get('principio_1_compromiso', '')}. Acción: {prof.get('principio_3_accion_expresion', '')}. Instrumento: {prof.get('instrumento_clave', '')}."
            records.append({
                "Identificador": st_id,
                "Iniciales": prof.get("iniciales", ""),
                "Calificacion_Sugerida": prof.get("promedio", 75),
                "Comentarios_Retroalimentacion": feedback_text
            })
    else:
        # Muestra estándar
        records.append({
            "Identificador": "EST-001",
            "Iniciales": "A.V.",
            "Calificacion_Sugerida": 85,
            "Comentarios_Retroalimentacion": "Excelente argumentación. Se recomienda defensa oral socrática para validar fuentes bibliográficas (DUA Acción/Expresión)."
        })
        records.append({
            "Identificador": "EST-002",
            "Iniciales": "C.R.",
            "Calificacion_Sugerida": 62,
            "Comentarios_Retroalimentacion": "Refuerzo formativo en formulación de hipótesis. Andamiaje con batería de micro-quizzes de acompañamiento."
        })
        
    df = pd.DataFrame(records)
    
    if target_lms == "moodle":
        # Formato CSV compatible con Moodle Gradebook Import
        df_moodle = df.rename(columns={
            "Identificador": "Número de ID",
            "Calificacion_Sugerida": "Calificación",
            "Comentarios_Retroalimentacion": "Comentarios de retroalimentación"
        })
        csv_buffer = io.StringIO()
        df_moodle.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        return Response(
            content=csv_buffer.getvalue().encode("utf-8-sig"),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="FEEDBACK_MOODLE_{canonical_name}.csv"'}
        )
    elif target_lms == "teams":
        # Formato Excel para Microsoft Teams Assignments
        out = io.BytesIO()
        df.to_excel(out, index=False, sheet_name="Teams Feedback")
        return Response(
            content=out.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="FEEDBACK_TEAMS_{canonical_name}.xlsx"'}
        )
    else:
        # Formato CSV para Google Classroom
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        return Response(
            content=csv_buffer.getvalue().encode("utf-8-sig"),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="FEEDBACK_CLASSROOM_{canonical_name}.csv"'}
        )

@app.get("/api/system/backup")
def download_system_backup():
    """Genera y descarga un respaldo comprimido .ZIP de toda la carpeta de uploads y expedientes."""
    import zipfile
    import io
    from fastapi.responses import Response
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    uploads_dir = os.path.join(base_dir, "uploads")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(uploads_dir):
            for root, _, files in os.walk(uploads_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    rel = os.path.relpath(fp, uploads_dir)
                    zf.write(fp, rel)
    
    buf.seek(0)
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="BACKUP_CARPETA_PEDAGOGICA_2.0.zip"'}
    )

@app.post("/api/system/clear-cache")
def clear_system_cache():
    """Limpia los archivos temporales y la caché de procesamiento."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    scratch_dir = os.path.join(base_dir, "scratch")
    count = 0
    if os.path.exists(scratch_dir):
        for f in os.listdir(scratch_dir):
            fp = os.path.join(scratch_dir, f)
            if os.path.isfile(fp):
                try:
                    os.remove(fp)
                    count += 1
                except Exception:
                    pass
    return {"status": "ok", "message": f"Se limpiaron {count} archivos temporales del sistema."}

from fastapi.responses import FileResponse

@app.get("/api/drive/status")
def drive_status_endpoint():
    """Retorna el estado de configuración de Google Drive."""
    from drive_service import get_drive_status
    return get_drive_status()

@app.post("/api/drive/backup-subject/{subject_name}")
async def backup_subject_drive_endpoint(subject_name: str):
    """Genera el respaldo de las carpetas de la materia (Base y REV generadas en Etapa 1) y lo sube a Google Drive."""
    from drive_service import backup_subject_to_drive
    clean_name = sanitize_folder_name(subject_name)
    try:
        result = await anyio.to_thread.run_sync(backup_subject_to_drive, clean_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en respaldo Drive: {str(e)}")

@app.get("/api/drive/download-backup/{filename}")
def download_backup_zip(filename: str):
    """Descarga el archivo ZIP del respaldo de una materia específica."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "uploads", "_backups", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo de respaldo no encontrado")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/zip"
    )

