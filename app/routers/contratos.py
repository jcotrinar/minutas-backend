from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.ContratoOut])
def listar_contratos(
    estado:   Optional[str] = Query(None, description="VERDE/AMARILLO/AZUL/ROJO"),
    busqueda: Optional[str] = Query(None, description="Nombre del titular"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista contratos con filtros opcionales. Incluye saldo y estado calculados."""
    query = db.query(models.Contrato)

    if busqueda:
        query = query.filter(
            models.Contrato.titular.ilike(f"%{busqueda}%")
        )

    contratos = query.offset(skip).limit(limit).all()

    # Filtrar por estado (se calcula en Python, no en SQL)
    if estado:
        contratos = [c for c in contratos if c.estado == estado.upper()]

    return contratos


@router.get("/{contrato_id}", response_model=schemas.ContratoOut)
def obtener_contrato(contrato_id: int, db: Session = Depends(get_db)):
    contrato = db.query(models.Contrato).filter(
        models.Contrato.id == contrato_id
    ).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return contrato


@router.post("/", response_model=schemas.ContratoOut, status_code=201)
def crear_contrato(data: schemas.ContratoCreate, db: Session = Depends(get_db)):
    # Verificar que el número no exista
    existe = db.query(models.Contrato).filter(
        models.Contrato.numero == data.numero
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail=f"Ya existe el contrato N° {data.numero}")

    # Verificar que el lote exista
    lote = db.query(models.Lote).filter(models.Lote.id == data.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    contrato = models.Contrato(**data.model_dump())
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato


@router.put("/{contrato_id}", response_model=schemas.ContratoOut)
def actualizar_contrato(
    contrato_id: int,
    data: schemas.ContratoUpdate,
    db: Session = Depends(get_db)
):
    contrato = db.query(models.Contrato).filter(
        models.Contrato.id == contrato_id
    ).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(contrato, campo, valor)

    db.commit()
    db.refresh(contrato)
    return contrato


@router.delete("/{contrato_id}", status_code=204)
def eliminar_contrato(contrato_id: int, db: Session = Depends(get_db)):
    contrato = db.query(models.Contrato).filter(
        models.Contrato.id == contrato_id
    ).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    db.delete(contrato)
    db.commit()
