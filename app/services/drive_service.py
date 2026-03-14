"""
drive_service.py — Sube minutas a Google Drive usando OAuth2.

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
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES         = ["https://www.googleapis.com/auth/drive"]
ROOT_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "").strip()
MIME_DOCX      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_FOLDER    = "application/vnd.google-apps.folder"


def _get_service():
    """
    Autentica con OAuth2 usando el token guardado en GOOGLE_OAUTH_TOKEN (Railway)
    o en token.json (local).
    El refresh_token renueva el acceso automáticamente — no expira.
    """
    token_json = os.getenv("GOOGLE_OAUTH_TOKEN")
    if token_json:
        token_data = json.loads(token_json)
    else:
        # Desarrollo local
        with open("token.json") as f:
            token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", SCOPES),
    )

    # Refrescar token si está vencido
    if not creds.valid:
        creds.refresh(Request())

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _get_or_create_folder(service, nombre: str, parent_id: str) -> str:
    """Busca carpeta por nombre dentro de parent_id. Si no existe, la crea."""
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
        raise ValueError("DRIVE_FOLDER_ID no está configurado")

    service = _get_service()

    # Crear estructura de carpetas
    carpeta_proyecto = _get_or_create_folder(service, proyecto_nombre,     ROOT_FOLDER_ID)
    carpeta_anio     = _get_or_create_folder(service, str(fecha.year),      carpeta_proyecto)
    carpeta_mes      = _get_or_create_folder(service, f"{fecha.month:02d}", carpeta_anio)
    carpeta_dia      = _get_or_create_folder(service, f"{fecha.day:02d}",   carpeta_mes)

    nombre_archivo = ruta_local.name

    # Reemplazar si ya existe
    q = (
        f"name='{nombre_archivo}' "
        f"and '{carpeta_dia}' in parents "
        f"and trashed=false"
    )
    existentes = service.files().list(q=q, fields="files(id)").execute().get("files", [])
    media = MediaFileUpload(str(ruta_local), mimetype=MIME_DOCX, resumable=False)

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
