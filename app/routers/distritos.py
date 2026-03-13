"""routers/distritos.py"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Distrito

router = APIRouter()

@router.get("/regiones")
def regiones(db: Session = Depends(get_db)):
    rows = db.query(Distrito.region).distinct().order_by(Distrito.region).all()
    return [r[0] for r in rows]

@router.get("/provincias/{region}")
def provincias(region: str, db: Session = Depends(get_db)):
    rows = db.query(Distrito.provincia).filter(
        Distrito.region == region
    ).distinct().order_by(Distrito.provincia).all()
    return [r[0] for r in rows]

@router.get("/distritos/{region}/{provincia}")
def distritos(region: str, provincia: str, db: Session = Depends(get_db)):
    rows = db.query(Distrito).filter(
        Distrito.region == region,
        Distrito.provincia == provincia
    ).order_by(Distrito.distrito).all()
    return [{"id": r.id, "distrito": r.distrito} for r in rows]
