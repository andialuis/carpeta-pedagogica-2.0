import os
import pickle
import zipfile
import re
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes necesarios para subir y convertir archivos en Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Autentica y devuelve el servicio de Google Drive."""
    creds = None
    base_dir = os.path.dirname(__file__)
    token_path = os.path.join(base_dir, 'token.pickle')
    creds_path = os.path.join(base_dir, 'credentials.json')

    # Intentar cargar token existente
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # Si no hay credenciales válidas, intentar refrescar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("No se encontró token.pickle. Por favor autentícate ejecutando auth.py primero.")

    return build('drive', 'v3', credentials=creds)

def get_or_create_drive_folder(service, folder_name: str, parent_id: str = None) -> str:
    """Busca o crea una carpeta en Google Drive."""
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
        
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder.get('id')

def upload_to_drive(file_path: str, convert_to_google_format: bool = True, parent_folder_id: str = None):
    """Sube un archivo a Drive y opcionalmente lo convierte a formato de Google."""
    service = get_drive_service()
    
    file_name = os.path.basename(file_path)
    mime_type = None
    
    if convert_to_google_format:
        if file_path.endswith('.xlsx'):
            mime_type = 'application/vnd.google-apps.spreadsheet'
        elif file_path.endswith('.docx'):
            mime_type = 'application/vnd.google-apps.document'
            
    file_metadata = {'name': file_name}
    if mime_type:
        file_metadata['mimeType'] = mime_type
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, webContentLink'
    ).execute()
    
    return {
        'id': file.get('id'),
        'webViewLink': file.get('webViewLink'),
        'webContentLink': file.get('webContentLink')
    }

def get_drive_status():
    """Retorna el estado de configuración de la API de Google Drive."""
    base_dir = os.path.dirname(__file__)
    token_path = os.path.join(base_dir, 'token.pickle')
    creds_path = os.path.join(base_dir, 'credentials.json')
    has_token = os.path.exists(token_path)
    has_creds = os.path.exists(creds_path)
    authenticated = False
    
    if has_token:
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                if creds and creds.valid:
                    authenticated = True
                elif creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    authenticated = True
        except Exception:
            authenticated = False
            
    return {
        "configured": authenticated,
        "has_credentials_file": has_creds,
        "has_token": has_token,
        "mode": "api" if authenticated else "assisted",
        "message": "API de Google Drive autenticada y conectada." if authenticated else "Modo Asistido / Soberano: Generación de paquete ZIP descargable listo para arrastrar a Google Drive."
    }

def backup_subject_to_drive(subject_name: str) -> dict:
    """
    Empaqueta los expedientes de una materia (archivos originales y carpeta -REV generada en Etapa 1)
    y los sube a Google Drive (o genera el paquete para subida asistida).
    """
    backend_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(backend_dir)
    uploads_dir = os.path.join(root_dir, "uploads")
    
    clean_subj = subject_name.replace("/", " ").replace("\\", " ").strip()
    if clean_subj.endswith("-REV"):
        base_name = clean_subj[:-4].strip()
    else:
        base_name = clean_subj
        
    raw_dir = os.path.join(uploads_dir, base_name)
    rev_dir = os.path.join(uploads_dir, f"{base_name}-REV")
    
    # Crear carpeta temporal de respaldos si no existe
    backups_dir = os.path.join(uploads_dir, "_backups")
    os.makedirs(backups_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_slug = re.sub(r'[^a-zA-Z0-9_\-]', '_', base_name)
    zip_filename = f"RESPALDO_{safe_slug}_{timestamp}.zip"
    zip_path = os.path.join(backups_dir, zip_filename)
    
    # Comprimir ambas carpetas (Base y REV)
    archived_files_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Carpeta original (si existe)
        if os.path.exists(raw_dir):
            for root, _, files in os.walk(raw_dir):
                for f in files:
                    file_full = os.path.join(root, f)
                    rel_path = os.path.relpath(file_full, uploads_dir)
                    zf.write(file_full, arcname=rel_path)
                    archived_files_count += 1
                    
        # 2. Carpeta -REV (creada en Etapa 1)
        if os.path.exists(rev_dir):
            for root, _, files in os.walk(rev_dir):
                for f in files:
                    file_full = os.path.join(root, f)
                    rel_path = os.path.relpath(file_full, uploads_dir)
                    zf.write(file_full, arcname=rel_path)
                    archived_files_count += 1
                    
    zip_size_mb = round(os.path.getsize(zip_path) / (1024 * 1024), 2)
    
    # Verificar si Google Drive API está disponible
    status = get_drive_status()
    if status["configured"]:
        try:
            service = get_drive_service()
            # Carpeta raíz en Drive
            root_folder_id = get_or_create_drive_folder(service, "Carpeta Pedagógica 2.0")
            # Subcarpeta de la materia
            subject_folder_id = get_or_create_drive_folder(service, base_name, parent_id=root_folder_id)
            
            # Subir archivo ZIP a Drive
            upload_res = upload_to_drive(zip_path, convert_to_google_format=False, parent_folder_id=subject_folder_id)
            
            return {
                "status": "success",
                "mode": "api",
                "zip_filename": zip_filename,
                "zip_size_mb": zip_size_mb,
                "archived_files_count": archived_files_count,
                "drive_link": upload_res.get("webViewLink"),
                "download_url": f"/api/drive/download-backup/{zip_filename}",
                "message": f"Respaldo de {archived_files_count} archivos ({zip_size_mb} MB) subido exitosamente a tu Google Drive en la carpeta 'Carpeta Pedagógica 2.0/{base_name}'."
            }
        except Exception as e:
            print(f"Error subiendo a Google Drive por API: {e}")
            # Fallback al modo asistido
            return {
                "status": "partial",
                "mode": "assisted",
                "zip_filename": zip_filename,
                "zip_size_mb": zip_size_mb,
                "archived_files_count": archived_files_count,
                "drive_link": "https://drive.google.com",
                "download_url": f"/api/drive/download-backup/{zip_filename}",
                "message": f"El respaldo ZIP ({zip_size_mb} MB) fue generado con éxito en el servidor local. La API de Google Drive reportó: {e}. Puedes descargarlo y soltarlo directamente en Google Drive."
            }
    else:
        # Modo Asistido / Soberano
        return {
            "status": "success",
            "mode": "assisted",
            "zip_filename": zip_filename,
            "zip_size_mb": zip_size_mb,
            "archived_files_count": archived_files_count,
            "drive_link": "https://drive.google.com",
            "download_url": f"/api/drive/download-backup/{zip_filename}",
            "message": f"Respaldo comprimido generado exitosamente ({zip_size_mb} MB, {archived_files_count} archivos). Listo para descargar y almacenar en Google Drive."
        }
