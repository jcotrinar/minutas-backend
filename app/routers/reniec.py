"""routers/reniec.py"""
from fastapi import APIRouter, HTTPException
from app.services.reniec_service import consultar_dni

router = APIRouter()


@router.get("/{dni}")
def obtener_dni(dni: str):
    dni = dni.strip()
    if len(dni) != 8 or not dni.isdigit():
        raise HTTPException(400, "DNI inválido, debe tener 8 dígitos")
    datos = consultar_dni(dni)
    if not datos:
        raise HTTPException(404, "No se encontró información para el DNI ingresado")
    return datos
