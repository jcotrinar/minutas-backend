from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

# ─── LOTES ───────────────────────────────────────────────────────────────────

router = APIRouter()

@router.get("/", response_model=List[schemas.LoteOut])
def listar_lotes(
    manzana: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Lote)
    if manzana:
        query = query.filter(models.Lote.manzana == manzana.upper())
    return query.order_by(models.Lote.manzana, models.Lote.numero).all()

@router.get("/manzanas", response_model=List[str])
def listar_manzanas(db: Session = Depends(get_db)):
    """Lista de manzanas únicas, para el ComboBox de la app."""
    resultado = db.query(models.Lote.manzana).distinct().order_by(models.Lote.manzana).all()
    return [r[0] for r in resultado]
