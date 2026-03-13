"""
models.py — Modelos de base de datos simplificados.
4 tablas reales + distritos para autocompletar ubigeo.
"""
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase  # ✅ API moderna SQLAlchemy 2.x
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import enum


class Base(DeclarativeBase):
    pass


class Moneda(str, enum.Enum):
    SOLES   = "SOLES"
    DOLARES = "DOLARES"


class ColorSemaforo(str, enum.Enum):
    VERDE    = "VERDE"
    AMARILLO = "AMARILLO"
    AZUL     = "AZUL"
    ROJO     = "ROJO"


class Proyecto(Base):
    __tablename__ = "proyectos"

    id          = Column(Integer, primary_key=True)
    nombre      = Column(String(100), nullable=False)
    descripcion = Column(String(200))
    moneda      = Column(Enum(Moneda), default=Moneda.SOLES)
    activo      = Column(Boolean, default=True)

    fecha_limite_entrega = Column(Date, nullable=True)

    # Configuración global de entrega del lote para todos los contratos del proyecto
    entrega       = Column(String(50),  nullable=True)   # ej: "INMEDIATA", "AL_FINALIZAR_HABILITACION", "FECHA_ESPECIFICA"
    entrega_texto = Column(String(500), nullable=True)   # texto que se inserta en «ENTREGA_TEXTO»

    lotes      = relationship("Lote",     back_populates="proyecto")
    contratos  = relationship("Contrato", back_populates="proyecto")
    templates  = relationship("Template", back_populates="proyecto")


class Lote(Base):
    __tablename__ = "lotes"

    id            = Column(Integer, primary_key=True)
    proyecto_id   = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    manzana       = Column(String(10), nullable=False)
    numero        = Column(String(10), nullable=False)
    area          = Column(Float, nullable=False)
    partida       = Column(String(20))
    nombre_predio = Column(String(300))

    proyecto  = relationship("Proyecto", back_populates="lotes")
    contratos = relationship("Contrato", back_populates="lote")


class Distrito(Base):
    __tablename__ = "distritos"

    id        = Column(Integer, primary_key=True)
    region    = Column(String(100), nullable=False)
    provincia = Column(String(100), nullable=False)
    distrito  = Column(String(100), nullable=False)


class Contrato(Base):
    __tablename__ = "contratos"

    id          = Column(Integer, primary_key=True)
    numero      = Column(Integer, unique=True, nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    lote_id     = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    fecha       = Column(Date, nullable=False)

    # Titular
    titular       = Column(String(200), nullable=False)
    dni           = Column(String(15))
    ocupacion1    = Column(String(100))
    genero1       = Column(String(1))
    estado_civil1 = Column(String(1))
    distrito1_id  = Column(Integer, ForeignKey("distritos.id"), nullable=True)
    direccion1    = Column(String(300))

    # Copropietario (opcional)
    copropietario = Column(String(200))
    dni2          = Column(String(15))
    ocupacion2    = Column(String(100))
    genero2       = Column(String(1))
    estado_civil2 = Column(String(1))
    distrito2_id  = Column(Integer, ForeignKey("distritos.id"), nullable=True)
    direccion2    = Column(String(300))

    # Económico
    moneda       = Column(Enum(Moneda), nullable=False)
    precio       = Column(Float, nullable=False)
    separacion   = Column(Float, default=0.0)
    sep_en_soles = Column(Float, nullable=True)
    tipo_cambio  = Column(Float, nullable=True)
    pago         = Column(Float, default=0.0)

    # Plazo
    f_pago_total = Column(Date, nullable=True)
    plazo_meses  = Column(Integer, nullable=True)

    # Metadatos
    creado_en      = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    sincronizado   = Column(Boolean, default=False)

    # Relaciones
    proyecto  = relationship("Proyecto",  back_populates="contratos")
    lote      = relationship("Lote",      back_populates="contratos")
    distrito1 = relationship("Distrito",  foreign_keys=[distrito1_id])
    distrito2 = relationship("Distrito",  foreign_keys=[distrito2_id])

    @property
    def saldo(self) -> float:
        return round(self.precio - (self.separacion or 0) - (self.pago or 0), 2)

    @property
    def estado(self) -> str:
        tiene_coprop = bool(self.copropietario)
        tiene_saldo  = self.saldo > 0
        if not tiene_coprop and not tiene_saldo:
            return ColorSemaforo.VERDE
        if not tiene_coprop and tiene_saldo:
            return ColorSemaforo.AMARILLO
        if tiene_coprop and not tiene_saldo:
            return ColorSemaforo.AZUL
        return ColorSemaforo.ROJO


class Template(Base):
    __tablename__ = "templates"

    id          = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    color       = Column(Enum(ColorSemaforo), nullable=False)
    ruta        = Column(String(300), nullable=False)

    proyecto = relationship("Proyecto", back_populates="templates")
