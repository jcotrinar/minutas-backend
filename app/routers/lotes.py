"""routers/lotes.py"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Lote
from app.schemas import LoteOut

router = APIRouter()

@router.get("/", response_model=List[LoteOut])
def listar(
    proyecto_id: int,
    manzana: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Lote).filter(Lote.proyecto_id == proyecto_id)
    if manzana:
        q = q.filter(Lote.manzana == manzana)
    return q.order_by(Lote.manzana, Lote.numero).all()

@router.get("/manzanas")
def manzanas(proyecto_id: int, db: Session = Depends(get_db)):
    rows = db.query(Lote.manzana).filter(Lote.proyecto_id == proyecto_id).distinct().order_by(Lote.manzana).all()
    return [r[0] for r in rows]
