"""routers/contratos.py"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import Contrato
from app.schemas import ContratoCreate, ContratoUpdate, ContratoOut

router = APIRouter()


def _siguiente_numero(db: Session, proyecto_id: int) -> int:
    """Calcula el siguiente numero_proyecto para el proyecto dado."""
    maximo = db.query(func.max(Contrato.numero_proyecto)).filter(
        Contrato.proyecto_id == proyecto_id
    ).scalar()
    return (maximo or 0) + 1


@router.get("/", response_model=List[ContratoOut])
def listar(
    proyecto_id: Optional[int] = None,
    estado:      Optional[str] = None,
    busqueda:    Optional[str] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(Contrato)
    if proyecto_id:
        q = q.filter(Contrato.proyecto_id == proyecto_id)
    if busqueda:
        q = q.filter(Contrato.titular.ilike(f"%{busqueda}%"))
    contratos = q.order_by(Contrato.numero_proyecto.desc()).offset(skip).limit(limit).all()
    if estado:
        contratos = [c for c in contratos if c.estado == estado]
    return contratos


@router.get("/{id}", response_model=ContratoOut)
def obtener(id: int, db: Session = Depends(get_db)):
    c = db.query(Contrato).filter(Contrato.id == id).first()
    if not c:
        raise HTTPException(404, "Contrato no encontrado")
    return c


@router.post("/", response_model=ContratoOut, status_code=201)
def crear(data: ContratoCreate, db: Session = Depends(get_db)):
    # El backend calcula el siguiente número automáticamente
    siguiente = _siguiente_numero(db, data.proyecto_id)
    c = Contrato(
        numero_proyecto=siguiente,
        **data.model_dump()
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{id}", response_model=ContratoOut)
def actualizar(id: int, data: ContratoUpdate, db: Session = Depends(get_db)):
    c = db.query(Contrato).filter(Contrato.id == id).first()
    if not c:
        raise HTTPException(404, "Contrato no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{id}", status_code=204)
def eliminar(id: int, db: Session = Depends(get_db)):
    c = db.query(Contrato).filter(Contrato.id == id).first()
    if not c:
        raise HTTPException(404, "Contrato no encontrado")
    db.delete(c)
    db.commit()
