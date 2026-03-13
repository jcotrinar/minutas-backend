"""routers/proyectos.py"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Proyecto
from app.schemas import ProyectoOut
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ProyectoOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Proyecto).filter(Proyecto.activo == True).all()
