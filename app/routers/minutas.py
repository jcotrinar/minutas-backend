"""routers/minutas.py"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contrato, Template, ColorSemaforo
from app.services.generador_minutas import generar_minuta

router = APIRouter()

@router.post("/generar/{contrato_id}")
def generar(contrato_id: int, db: Session = Depends(get_db)):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(404, "Contrato no encontrado")

    color    = ColorSemaforo(contrato.estado)
    template = db.query(Template).filter(
        Template.proyecto_id == contrato.proyecto_id,
        Template.color       == color
    ).first()

    if not template:
        raise HTTPException(404, f"Template {color.value} no encontrado para este proyecto")

    lote      = contrato.lote
    distrito1 = contrato.distrito1
    distrito2 = contrato.distrito2

    ruta = generar_minuta(contrato, lote, template, distrito1, distrito2)
    return {"archivo": str(ruta)}


@router.get("/descargar/{contrato_id}")
def descargar(contrato_id: int, db: Session = Depends(get_db)):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(404, "Contrato no encontrado")

    color    = ColorSemaforo(contrato.estado)
    template = db.query(Template).filter(
        Template.proyecto_id == contrato.proyecto_id,
        Template.color       == color
    ).first()

    if not template:
        raise HTTPException(404, f"Template {color.value} no encontrado para este proyecto")

    ruta = generar_minuta(contrato, contrato.lote, template, contrato.distrito1, contrato.distrito2)

    return FileResponse(
        path=str(ruta),
        filename=ruta.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
