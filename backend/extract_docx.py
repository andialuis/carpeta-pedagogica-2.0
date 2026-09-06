import docx
import os
import json

def extract_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

base_dir = r"C:\Users\RcRd.03\Desktop\Taller Analítica de Aprendizaje"
prompt_file = os.path.join(base_dir, "Instrucciones para hacer PDC.docx")
script_file = os.path.join(base_dir, "Script para exportar a PDC primaria.docx")

# Extraer el Megaprompt
if os.path.exists(prompt_file):
    prompt_text = extract_docx(prompt_file)
    with open(r"C:\Users\RcRd.03\Desktop\Carpeta Pedagógica 2.0\backend\prompts_gallery\megaprompt_pdc.txt", "w", encoding="utf-8") as f:
        f.write(prompt_text)
    print("Megaprompt extraído.")

# Extraer el Script
if os.path.exists(script_file):
    script_text = extract_docx(script_file)
    with open(r"C:\Users\RcRd.03\Desktop\Carpeta Pedagógica 2.0\backend\export_scripts\export_pdc_primaria.py", "w", encoding="utf-8") as f:
        f.write(script_text)
    print("Script de exportación extraído.")
