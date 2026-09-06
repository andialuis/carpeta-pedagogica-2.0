import os
from google import genai
from google.genai import types
import pandas as pd
import json

def analyze_spreadsheet_structure(file_path: str):
    """Analiza la estructura de una hoja de cálculo usando Gemini 2.5 Flash o motor de contingencia determinista."""
    # Intentar leer las primeras 5 filas
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=5)
        else:
            df = pd.read_excel(file_path, nrows=5)
    except Exception as e:
        return {"error": f"No se pudo leer el archivo: {str(e)}"}
    
    # Inferencia determinista local como base
    local_mapping = {
        "student_identifier_column": df.columns[0] if len(df.columns) > 0 else "N/A",
        "analytics_columns": list(df.columns[1:]) if len(df.columns) > 1 else []
    }
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        # Fallback determinista con metadatos pedagógicos claros
        return {
            "suggested_mapping": local_mapping,
            "observations": "Medida de Contingencia Pedagógica: Clave de Gemini no detectada. Se aplicó deducción determinista basada en el encabezado de las columnas.",
            "requires_human_verification": True,
            "motor_ia": {
                "modo": "motor_local",
                "modelo": "deduccion_determinista_local",
                "mensaje": "Operando en contingencia local. Configure su API Key de Gemini para activar inferencia semántica profunda.",
                "fallback_activado": True,
                "error_motivo": "API_KEY_NO_CONFIGURADA"
            }
        }

    sample_data = df.to_string()
    prompt = f"""
    Eres un asistente experto en analítica de aprendizaje.
    A continuación te presento las primeras 5 filas de un documento subido por un docente:
    
    {sample_data}
    
    Tu tarea es inferir la estructura de estos datos para extraer UNICAMENTE la información mínima requerida para analítica (identificador de estudiante, calificaciones, asistencias).
    
    Devuelve un JSON con el siguiente esquema exacto:
    {{
        "suggested_mapping": {{
            "student_identifier_column": "nombre_de_columna",
            "analytics_columns": ["columna1", "columna2"]
        }},
        "observations": "Comentarios sobre inconsistencias o sugerencias para el docente.",
        "requires_human_verification": true
    }}
    """

    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        raw_text = (response.text or "").strip()
        data = json.loads(raw_text)
        data["motor_ia"] = {
            "modo": "gemini",
            "modelo": model_name,
            "mensaje": f"Estructura inferida exitosamente mediante {model_name} con Structured Outputs.",
            "fallback_activado": False,
            "error_motivo": None
        }
        return data
    except Exception as e:
        # Fallback resiliente ante errores de red o cuotas
        return {
            "suggested_mapping": local_mapping,
            "observations": f"Medida de Contingencia Pedagógica: La API de Gemini reportó un error ({str(e)}). Se utilizó la deducción determinista local sin interrumpir el flujo.",
            "requires_human_verification": True,
            "motor_ia": {
                "modo": "motor_local",
                "modelo": model_name,
                "mensaje": "Fallo en llamada a Gemini. Se activó motor determinista local para proteger la operación.",
                "fallback_activado": True,
                "error_motivo": str(e)
            }
        }

