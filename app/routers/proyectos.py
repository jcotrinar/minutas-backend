"""
proyectos.py — Router para proyectos.
Incluye endpoint PATCH /proyectos/{id}/entrega para configurar entrega global.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app import models
from app.schemas import ProyectoOut

router = APIRouter()


# ── Schema solo para el PATCH de entrega ────────────────────────────────────

class EntregaUpdate(BaseModel):
    entrega:               str
    entrega_texto:         str
    fecha_limite_entrega:  Optional[str] = None   # "YYYY-MM-DD" o null


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ProyectoOut])
def listar_proyectos(db: Session = Depends(get_db)):
    return db.query(models.Proyecto).filter(models.Proyecto.activo == True).all()


@router.get("/{proyecto_id}", response_model=ProyectoOut)
def obtener_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(models.Proyecto).filter(models.Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto


@router.patch("/{proyecto_id}/entrega", response_model=ProyectoOut)
def actualizar_entrega(
    proyecto_id: int,
    data: EntregaUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza la configuración de entrega global del proyecto."""
    proyecto = db.query(models.Proyecto).filter(models.Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    from datetime import date
    proyecto.entrega       = data.entrega
    proyecto.entrega_texto = data.entrega_texto.strip()
    if data.fecha_limite_entrega:
        proyecto.fecha_limite_entrega = date.fromisoformat(data.fecha_limite_entrega)
    else:
        proyecto.fecha_limite_entrega = None
    db.commit()
    db.refresh(proyecto)
    return proyecto
