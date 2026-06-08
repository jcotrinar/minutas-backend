"""
generar_token.py — Corre UNA SOLA VEZ localmente para generar token.json
Uso: python generar_token.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Cambia esto si tu archivo tiene otro nombre
OAUTH_CREDENTIALS = "oauth_credentials.json"

flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CREDENTIALS, SCOPES)
creds = flow.run_local_server(port=0)

# Guardar token
token_data = {
    "token":         creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri":     creds.token_uri,
    "client_id":     creds.client_id,
    "client_secret": creds.client_secret,
    "scopes":        list(creds.scopes),
}

with open("token.json", "w") as f:
    json.dump(token_data, f, indent=2)

print("✅ token.json generado correctamente")
print(f"   refresh_token: {creds.refresh_token[:20]}...")
