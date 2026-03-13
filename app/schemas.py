"""schemas.py — Modelos de entrada/salida de la API."""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models import Moneda, ColorSemaforo


# ─── PROYECTOS ────────────────────────────────────────────────────────────────

class ProyectoOut(BaseModel):
    id:          int
    nombre:      str
    moneda:      Moneda
    activo:      bool
    class Config: from_attributes = True


# ─── LOTES ────────────────────────────────────────────────────────────────────

class LoteOut(BaseModel):
    id:            int
    proyecto_id:   int
    manzana:       str
    numero:        str
    area:          float
    partida:       Optional[str]
    nombre_predio: Optional[str]
    class Config: from_attributes = True


# ─── DISTRITOS ────────────────────────────────────────────────────────────────

class DistritoOut(BaseModel):
    id:        int
    region:    str
    provincia: str
    distrito:  str
    class Config: from_attributes = True


# ─── CONTRATOS ────────────────────────────────────────────────────────────────

class ContratoCreate(BaseModel):
    numero:        int
    proyecto_id:   int
    lote_id:       int
    fecha:         date

    # Titular
    titular:       str
    dni:           Optional[str]
    ocupacion1:    Optional[str]
    genero1:       Optional[str]
    estado_civil1: Optional[str]
    distrito1_id:  Optional[int]
    direccion1:    Optional[str]

    # Copropietario
    copropietario: Optional[str]
    dni2:          Optional[str]
    ocupacion2:    Optional[str]
    genero2:       Optional[str]
    estado_civil2: Optional[str]
    distrito2_id:  Optional[int]
    direccion2:    Optional[str]

    # Económico
    moneda:        Moneda
    precio:        float
    separacion:    float = 0.0
    sep_en_soles:  Optional[float]
    tipo_cambio:   Optional[float]
    pago:          float = 0.0

    # Plazo
    f_pago_total:  Optional[date]
    plazo_meses:   Optional[int]


class ContratoUpdate(BaseModel):
    fecha:         Optional[date]
    titular:       Optional[str]
    dni:           Optional[str]
    ocupacion1:    Optional[str]
    genero1:       Optional[str]
    estado_civil1: Optional[str]
    distrito1_id:  Optional[int]
    direccion1:    Optional[str]
    copropietario: Optional[str]
    dni2:          Optional[str]
    ocupacion2:    Optional[str]
    genero2:       Optional[str]
    estado_civil2: Optional[str]
    distrito2_id:  Optional[int]
    direccion2:    Optional[str]
    moneda:        Optional[Moneda]
    precio:        Optional[float]
    separacion:    Optional[float]
    sep_en_soles:  Optional[float]
    tipo_cambio:   Optional[float]
    pago:          Optional[float]
    f_pago_total:  Optional[date]
    plazo_meses:   Optional[int]


class LoteResumen(BaseModel):
    manzana: str
    numero:  str
    area:    float
    class Config: from_attributes = True


class ContratoOut(BaseModel):
    id:            int
    numero:        int
    proyecto_id:   int
    lote_id:       int
    fecha:         date
    titular:       str
    dni:           Optional[str]
    ocupacion1:    Optional[str]
    genero1:       Optional[str]
    estado_civil1: Optional[str]
    direccion1:    Optional[str]
    copropietario: Optional[str]
    moneda:        Moneda
    precio:        float
    separacion:    float
    sep_en_soles:  Optional[float]
    tipo_cambio:   Optional[float]
    pago:          float
    f_pago_total:  Optional[date]
    plazo_meses:   Optional[int]
    saldo:         float
    estado:        str
    creado_en:     Optional[datetime]
    lote:          Optional[LoteResumen]
    class Config: from_attributes = True
