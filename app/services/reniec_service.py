# app/services/reniec_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Consulta de DNI (RENIEC) vía apis.net.pe — mismo patrón usado en otros
# proyectos (utils_apis.py).
#
# Fuentes, en orden:
#   1. apis.net.pe v2 (si hay token en la variable de entorno APIS_NET_PE_TOKEN)
#   2. apis.net.pe v1 (gratuita, sin token, con límite de peticiones)
#
# Si ambas fallan (sin internet, límite excedido, DNI no encontrado), retorna
# {} y el formulario permite completar los datos manualmente.
# ─────────────────────────────────────────────────────────────────────────────

import os
import requests

_TIMEOUT = 8  # segundos por intento

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}


def _leer_token():
    """Token opcional de apis.net.pe: variable de entorno APIS_NET_PE_TOKEN."""
    return (os.environ.get("APIS_NET_PE_TOKEN") or "").strip() or None


def _armar(d: dict):
    nombres = d.get("nombres", "")
    ap_pat = d.get("apellidoPaterno", "")
    ap_mat = d.get("apellidoMaterno", "")
    completo = " ".join(p for p in (nombres, ap_pat, ap_mat) if p).strip()
    if not completo:
        return None
    return {
        "nombre_completo": completo,
        "nombres": nombres,
        "apellido_paterno": ap_pat,
        "apellido_materno": ap_mat,
    }


def consultar_dni(dni: str) -> dict:
    """
    Consulta un DNI en RENIEC y devuelve un dict con:
      { 'nombre_completo', 'nombres', 'apellido_paterno', 'apellido_materno' }
    Devuelve {} si ninguna fuente responde. No incluye fecha de nacimiento —
    RENIEC no la expone en las consultas públicas/gratuitas.
    """
    dni = str(dni).strip()
    if len(dni) != 8 or not dni.isdigit():
        return {}

    token = _leer_token()

    # 1) v2 con token (más estable, mayor cuota)
    if token:
        try:
            r = requests.get(
                "https://api.apis.net.pe/v2/reniec/dni",
                params={"numero": dni},
                headers={**_HEADERS, "Authorization": f"Bearer {token}"},
                timeout=_TIMEOUT,
            )
            if r.ok:
                res = _armar(r.json())
                if res:
                    return res
        except requests.RequestException:
            pass

    # 2) v1 anónima
    try:
        r = requests.get(
            "https://api.apis.net.pe/v1/dni",
            params={"numero": dni},
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        if r.ok:
            res = _armar(r.json())
            if res:
                return res
    except requests.RequestException:
        pass

    return {}
