"""routers/contratos.py"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Contrato
from app.schemas import ContratoCreate, ContratoUpdate, ContratoOut

router = APIRouter()


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
    contratos = q.order_by(Contrato.numero.desc()).offset(skip).limit(limit).all()
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
    if db.query(Contrato).filter(Contrato.numero == data.numero).first():
        raise HTTPException(400, f"Ya existe el contrato número {data.numero}")
    c = Contrato(**data.model_dump())
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
