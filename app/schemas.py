from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime


# ─── LOTE ────────────────────────────────────────────────────────────────────

class LoteBase(BaseModel):
    manzana: str
    numero:  int
    area:    float
    uc:      Optional[int]    = None
    partida: Optional[str]   = None
    has:     Optional[float] = None

class LoteCreate(LoteBase):
    pass

class LoteOut(LoteBase):
    id:    int
    mz_lt: Optional[str] = None
    class Config:
        from_attributes = True


# ─── DISTRITO ─────────────────────────────────────────────────────────────────

class DistritoOut(BaseModel):
    id:        int
    region:    str
    provincia: str
    distrito:  str
    class Config:
        from_attributes = True


# ─── CONTRATO ─────────────────────────────────────────────────────────────────

class ContratoBase(BaseModel):
    numero:        int
    lote_id:       int
    precio:        float
    separacion:    float = 0.0
    pago:          float = 0.0
    fecha:         date
    f_separacion:  Optional[date] = None
    f_pago_total:  Optional[date] = None

    # Titular
    titular:       str
    ocupacion1:    Optional[str] = None
    genero1:       Optional[str] = Field(None, pattern="^[MF]$")
    estado_civil1: Optional[str] = Field(None, pattern="^[SCDV]$")
    dni:           Optional[str] = None
    direccion1:    Optional[str] = None
    distrito1_id:  Optional[int] = None

    # Copropietario
    copropietario:  Optional[str] = None
    ocupacion2:     Optional[str] = None
    genero2:        Optional[str] = Field(None, pattern="^[MF]$")
    estado_civil2:  Optional[str] = Field(None, pattern="^[SCDV]$")
    dni2:           Optional[str] = None
    direccion2:     Optional[str] = None
    distrito2_id:   Optional[int] = None

class ContratoCreate(ContratoBase):
    pass

class ContratoUpdate(BaseModel):
    precio:        Optional[float] = None
    separacion:    Optional[float] = None
    pago:          Optional[float] = None
    f_pago_total:  Optional[date]  = None
    copropietario: Optional[str]   = None
    # (agrega más campos según necesites actualizar)

class ContratoOut(ContratoBase):
    id:            int
    saldo:         float
    estado:        str          # VERDE / AMARILLO / AZUL / ROJO
    creado_en:     Optional[datetime] = None
    sincronizado:  bool
    lote:          Optional[LoteOut]      = None
    distrito1:     Optional[DistritoOut] = None
    distrito2:     Optional[DistritoOut] = None

    class Config:
        from_attributes = True


# ─── MINUTA ──────────────────────────────────────────────────────────────────

class MinutaRequest(BaseModel):
    contrato_id:   int
    subir_a_drive: bool = True   # Si False, solo devuelve el archivo sin subir

class MinutaResponse(BaseModel):
    contrato_id:   int
    estado:        str
    archivo_local: str           # Ruta en el servidor
    drive_url:     Optional[str] = None   # URL del archivo en Drive (si se subió)
    nombre:        str           # Nombre del archivo generado
