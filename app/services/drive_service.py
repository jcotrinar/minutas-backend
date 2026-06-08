"""
drive_service.py — Sube minutas a Google Drive usando OAuth2.
"""
import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

SCOPES         = ["https://www.googleapis.com/auth/drive"]
ROOT_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "").strip()
MIME_DOCX      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_PDF       = "application/pdf"
MIME_FOLDER    = "application/vnd.google-apps.folder"

MESES_ES = {
    1:"ENE", 2:"FEB", 3:"MAR", 4:"ABR",
    5:"MAY", 6:"JUN", 7:"JUL", 8:"AGO",
    9:"SEP", 10:"OCT", 11:"NOV", 12:"DIC"
}


def _get_service():
    token_json = os.getenv("GOOGLE_OAUTH_TOKEN")
    if token_json:
        token_data = json.loads(token_json)
    else:
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

    if not creds.valid:
        # Se añade sesión con timeout explícito para refrescar el token
        session = requests.Session()
        request_adapter = GoogleRequest(session=session)
        creds.refresh(request_adapter)

    # ── NUEVO: Forzar Timeout en las conexiones HTTP con Google API ──────────
    authenticated_session = google.auth.transport.requests.AuthorizedSession(creds)
    authenticated_session.timeout = 90.0  # 90 segundos límite por petición HTTP

    return build("drive", "v3", http=authenticated_session, cache_discovery=False)


def _get_or_create_folder(service, nombre: str, parent_id: str) -> str:
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
    if not ROOT_FOLDER_ID:
        raise ValueError("DRIVE_FOLDER_ID no está configurado")

    service = _get_service()

    carpeta_proyecto = _get_or_create_folder(service, proyecto_nombre,     ROOT_FOLDER_ID)
    carpeta_anio     = _get_or_create_folder(service, str(fecha.year),      carpeta_proyecto)
    carpeta_mes      = _get_or_create_folder(service, MESES_ES[fecha.month], carpeta_anio)
    carpeta_dia      = _get_or_create_folder(service, f"{fecha.day:02d}",   carpeta_mes)

    nombre_archivo = ruta_local.name

    q = (
        f"name='{nombre_archivo}' "
        f"and '{carpeta_dia}' in parents "
        f"and trashed=false"
    )
    existentes = service.files().list(q=q, fields="files(id)").execute().get("files", [])
    media = MediaFileUpload(str(ruta_local), mimetype=MIME_PDF, resumable=False)

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