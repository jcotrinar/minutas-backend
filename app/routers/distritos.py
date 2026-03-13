from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.DistritoOut])
def listar_distritos(
    region:    Optional[str] = Query(None),
    provincia: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Distrito)
    if region:
        query = query.filter(models.Distrito.region.ilike(f"%{region}%"))
    if provincia:
        query = query.filter(models.Distrito.provincia.ilike(f"%{provincia}%"))
    return query.order_by(models.Distrito.region, models.Distrito.provincia, models.Distrito.distrito).all()

@router.get("/regiones", response_model=List[str])
def listar_regiones(db: Session = Depends(get_db)):
    resultado = db.query(models.Distrito.region).distinct().order_by(models.Distrito.region).all()
    return [r[0] for r in resultado]

@router.get("/provincias/{region}", response_model=List[str])
def listar_provincias(region: str, db: Session = Depends(get_db)):
    resultado = (
        db.query(models.Distrito.provincia)
        .filter(models.Distrito.region.ilike(f"%{region}%"))
        .distinct()
        .order_by(models.Distrito.provincia)
        .all()
    )
    return [r[0] for r in resultado]

@router.get("/distritos/{region}/{provincia}", response_model=List[str])
def listar_distritos_por_provincia(region: str, provincia: str, db: Session = Depends(get_db)):
    resultado = (
        db.query(models.Distrito.distrito)
        .filter(
            models.Distrito.region.ilike(f"%{region}%"),
            models.Distrito.provincia.ilike(f"%{provincia}%")
        )
        .order_by(models.Distrito.distrito)
        .all()
    )
    return [r[0] for r in resultado]
