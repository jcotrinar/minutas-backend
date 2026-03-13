"""
drive_service.py
Sube las minutas generadas a Google Drive automáticamente.
Equivalente a la parte de MkDir + SaveAs del Módulo1 VBA,
pero en la nube.
"""

import os
import json
from pathlib import Path
from typing import Optional

# google-auth y google-api-python-client
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    DRIVE_DISPONIBLE = True
except ImportError:
    DRIVE_DISPONIBLE = False

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ID de la carpeta raíz en Drive donde se guardan las minutas
# Configura en .env: DRIVE_FOLDER_ID=xxxxxxxxxx
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")


def _get_service():
    """Retorna el cliente autenticado de Drive."""
    if not DRIVE_DISPONIBLE:
        raise RuntimeError("Instala: pip install google-auth google-api-python-client")

    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Credenciales de Google no encontradas en: {CREDENTIALS_PATH}\n"
            "Descárgalas desde Google Cloud Console → Service Account → JSON key"
        )

    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def _obtener_o_crear_carpeta(service, nombre: str, padre_id: str) -> str:
    """Busca una carpeta por nombre dentro de padre_id; si no existe, la crea."""
    query = (
        f"name='{nombre}' and "
        f"'{padre_id}' in parents and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"trashed=false"
    )
    resultado = service.files().list(q=query, fields="files(id)").execute()
    archivos  = resultado.get("files", [])

    if archivos:
        return archivos[0]["id"]

    # Crear carpeta
    metadata = {
        "name":     nombre,
        "mimeType": "application/vnd.google-apps.folder",
        "parents":  [padre_id],
    }
    carpeta = service.files().create(body=metadata, fields="id").execute()
    return carpeta["id"]


def subir_minuta(ruta_local: Path, año: str, mes: str) -> Optional[str]:
    """
    Sube un archivo .docx a Drive en la estructura:
    [Carpeta raíz] / [año] / [mes] / archivo.docx

    Retorna la URL del archivo en Drive, o None si falla.
    """
    if not DRIVE_DISPONIBLE or not DRIVE_FOLDER_ID:
        return None

    try:
        service = _get_service()

        # Crear/obtener subcarpetas año y mes
        carpeta_año = _obtener_o_crear_carpeta(service, año, DRIVE_FOLDER_ID)
        carpeta_mes = _obtener_o_crear_carpeta(service, mes, carpeta_año)

        # Subir archivo
        metadata = {
            "name":    ruta_local.name,
            "parents": [carpeta_mes],
        }
        media = MediaFileUpload(
            str(ruta_local),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=True,
        )
        archivo = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink",
        ).execute()

        return archivo.get("webViewLink")

    except Exception as e:
        # No falla silenciosamente — el backend registra el error
        print(f"[Drive] Error al subir {ruta_local.name}: {e}")
        return None
