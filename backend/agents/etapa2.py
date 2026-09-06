"""
etapa2.py - Procesamiento y Anonimización Universal
Anonimiza cualquier materia y genera BASE_LIMPIA_ANONIMIZADA.xlsx + llave_nombres.json
"""
import os
import sys
import pandas as pd
import json

def run():
    print("Iniciando Etapa 2: Procesamiento y Anonimización...")
    subject_name = sys.argv[1] if len(sys.argv) > 1 else "INV101 - Introduccion a la Investigacion"
    
    agents_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(agents_dir)
    root_dir = os.path.dirname(backend_dir)
    target_dir = os.path.join(root_dir, "uploads", f"{subject_name}-REV", "bases_de_datos")
    
    input_file = os.path.join(target_dir, "BASE_INTEGRADA.xlsx")
    output_file = os.path.join(target_dir, "BASE_LIMPIA_ANONIMIZADA.xlsx")
    llave_file = os.path.join(target_dir, "llave_nombres.json")
    
    if not os.path.exists(input_file):
        print(f"Error: No se encontró {input_file}. Ejecuta la Etapa 1 primero.")
        sys.exit(1)
        
    print(f"Leyendo base integrada: {input_file}")
    df = pd.read_excel(input_file)
    
    # Detectar columna de nombre
    name_col = None
    for c in ["Nombre", "Nombre Completo", "Estudiante", "Alumno", "Student", "Name"]:
        if c in df.columns:
            name_col = c
            break
    if not name_col:
        for c in df.columns:
            if df[c].dtype == object:
                name_col = c
                break
                
    if name_col:
        print(f"Columna de identificación detectada: '{name_col}'")
        nombres_unicos = df[name_col].dropna().unique()
        mapa_nombres = {nombre: f"Est_{i+1:03d}" for i, nombre in enumerate(nombres_unicos)}
        mapa_inverso = {f"Est_{i+1:03d}": str(nombre) for i, nombre in enumerate(nombres_unicos)}
        
        df[name_col] = df[name_col].map(mapa_nombres)
        df.rename(columns={name_col: "Estudiante_ID"}, inplace=True)
        
        with open(llave_file, 'w', encoding='utf-8') as f:
            json.dump(mapa_inverso, f, ensure_ascii=False, indent=2)
        print(f"Llave de nombres generada ({len(mapa_inverso)} alumnos): {llave_file}")
    else:
        print("No se encontró columna de nombres; conservando estructura.")
        
    # Limpiar columnas de datos personales (PII)
    pii_keywords = ["email", "correo", "telefono", "celular", "cedula", "ci-", "dni", "rut", "arquetipo"]
    cols_to_drop = [c for c in df.columns if any(k in str(c).lower() for k in pii_keywords)]
    if cols_to_drop:
        print(f"Eliminando columnas PII: {cols_to_drop}")
        df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

    # Imputar valores vacíos con diferenciación estadística:
    # 1. Variables de conteo/frecuencia (iteraciones, clicks, eventos Moodle): NaN = 0 (cero real de actividad)
    # 2. Variables de evaluación continua (notas, puntajes): NaN = mediana muestral
    # 3. Variables categóricas: NaN = "No registrado"
    print("Imputando valores vacíos con diferenciación metodológica...")
    count_keywords = ["iteracion", "prompt", "moodle", "evento", "click", "asist", "total_asist", "horas"]
    for col in df.columns:
        if df[col].isnull().any():
            is_count = any(k in str(col).lower() for k in count_keywords)
            if df[col].dtype in ['float64', 'int64']:
                if is_count:
                    df[col].fillna(0, inplace=True)
                else:
                    med = df[col].median()
                    df[col].fillna(med, inplace=True)
            else:
                df[col].fillna("No registrado", inplace=True)
                
    # Guardar
    df.to_excel(output_file, index=False)
    print(f"Base limpia guardada en: {output_file}")
    print("Etapa 2 completada con éxito.")

if __name__ == "__main__":
    run()
