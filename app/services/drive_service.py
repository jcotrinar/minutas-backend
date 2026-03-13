"""
drive_service.py — Sube minutas a Google Drive.

Estructura de carpetas en Drive:
  DRIVE_FOLDER_ID/
  └── {Proyecto}/
      └── {Año}/
          └── {Mes}/
              └── {Dia}/
                  └── A-3,Sol y Luna Malabrigo.docx
"""
import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES         = ["https://www.googleapis.com/auth/drive"]
ROOT_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
MIME_DOCX      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_FOLDER    = "application/vnd.google-apps.folder"


def _get_service():
    """
    Autentica con Google Drive.
    Prioridad:
      1. GOOGLE_CREDENTIALS_JSON — variable de entorno con el JSON completo (Railway)
      2. GOOGLE_CREDENTIALS_PATH — ruta al archivo .json (desarrollo local)
    """
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        # Railway: leer credenciales desde variable de entorno
        info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        # Local: leer desde archivo
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _get_or_create_folder(service, nombre: str, parent_id: str) -> str:
    """Busca una carpeta por nombre dentro de parent_id. Si no existe, la crea."""
    q = (
        f"name='{nombre}' "
        f"and mimeType='{MIME_FOLDER}' "
        f"and '{parent_id}' in parents "
        f"and trashed=false"
    )
    res = service.files().list(q=q, fields="files(id, name)").execute()
    archivos = res.get("files", [])
    if archivos:
        return archivos[0]["id"]

    metadata = {
        "name":     nombre,
        "mimeType": MIME_FOLDER,
        "parents":  [parent_id],
    }
    carpeta = service.files().create(body=metadata, fields="id").execute()
    return carpeta["id"]


def subir_a_drive(ruta_local: Path, proyecto_nombre: str, fecha) -> str:
    """
    Sube el archivo a Drive en la estructura:
      ROOT / Proyecto / Año / Mes / Dia

    Retorna el link del archivo subido.
    """
    if not ROOT_FOLDER_ID:
        raise ValueError("DRIVE_FOLDER_ID no está configurado en .env")

    service = _get_service()

    # Crear estructura de carpetas
    carpeta_proyecto = _get_or_create_folder(service, proyecto_nombre,     ROOT_FOLDER_ID)
    carpeta_anio     = _get_or_create_folder(service, str(fecha.year),      carpeta_proyecto)
    carpeta_mes      = _get_or_create_folder(service, f"{fecha.month:02d}", carpeta_anio)
    carpeta_dia      = _get_or_create_folder(service, f"{fecha.day:02d}",   carpeta_mes)

    # Subir archivo — si ya existe con el mismo nombre, lo reemplaza
    nombre_archivo = ruta_local.name
    q = (
        f"name='{nombre_archivo}' "
        f"and '{carpeta_dia}' in parents "
        f"and trashed=false"
    )
    existentes = service.files().list(q=q, fields="files(id)").execute().get("files", [])
    media = MediaFileUpload(str(ruta_local), mimetype=MIME_DOCX, resumable=True)

    if existentes:
        file_id = existentes[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        metadata = {"name": nombre_archivo, "parents": [carpeta_dia]}
        archivo  = service.files().create(
            body=metadata, media_body=media, fields="id"
        ).execute()
        file_id = archivo["id"]

    return f"https://drive.google.com/file/d/{file_id}/view"
