import os
import pickle
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
            
    # Si no hay credenciales válidas, pedir al usuario que se loguee
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("No se encontró token.pickle. Por favor autentícate ejecutando auth.py primero.")

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path: str, convert_to_google_format: bool = True):
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

    media = MediaFileUpload(file_path, resumable=True)
    
    # Subir a la raíz por defecto (o podríamos crear una carpeta "Carpeta Pedagógica 2.0")
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    return {
        'id': file.get('id'),
        'webViewLink': file.get('webViewLink')
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
        "mode": "api" if authenticated else "apps_script_contingency",
        "message": "API de Google Drive autenticada y conectada." if authenticated else "Modo de Contingencia Activo: Sincronización mediante Google Apps Script preconfigurado en Google Drive."
    }
