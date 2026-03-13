from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Lote(Base):
    __tablename__ = "lotes"

    id        = Column(Integer, primary_key=True, index=True)
    manzana   = Column(String(10), nullable=False)
    numero    = Column(Integer, nullable=False)
    area      = Column(Float, nullable=False)          # m²
    uc        = Column(Integer)                        # Unidad Catastral
    partida   = Column(String(20))                     # Partida registral
    has       = Column(Float)                          # Hectáreas totales de la MZ
    mz_lt     = Column(String(20))                     # Ej: "A-1"

    contratos = relationship("Contrato", back_populates="lote")


class Distrito(Base):
    __tablename__ = "distritos"

    id        = Column(Integer, primary_key=True, index=True)
    region    = Column(String(100), nullable=False)
    provincia = Column(String(100), nullable=False)
    distrito  = Column(String(100), nullable=False)


class Contrato(Base):
    __tablename__ = "contratos"

    id            = Column(Integer, primary_key=True, index=True)

    # Número de contrato (correlativo del Excel original)
    numero        = Column(Integer, unique=True, nullable=False)

    # Datos del lote
    lote_id       = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    lote          = relationship("Lote", back_populates="contratos")

    # Datos económicos
    precio        = Column(Float, nullable=False)      # Precio total del lote
    separacion    = Column(Float, default=0.0)         # Cuota de separación
    pago          = Column(Float, default=0.0)         # Pago realizado
    # saldo se calcula: precio - separacion - pago

    # Fechas
    fecha         = Column(Date, nullable=False)       # Fecha del contrato
    f_separacion  = Column(Date)                       # Fecha de separación
    f_pago_total  = Column(Date)                       # Fecha de pago total acordada

    # Titular (comprador principal)
    titular       = Column(String(200), nullable=False)
    ocupacion1    = Column(String(100))
    genero1       = Column(String(1))                  # M / F
    estado_civil1 = Column(String(1))                  # S / C / D / V
    dni           = Column(String(20))
    direccion1    = Column(Text)
    distrito1_id  = Column(Integer, ForeignKey("distritos.id"))

    # Copropietario (opcional)
    copropietario  = Column(String(200))
    ocupacion2     = Column(String(100))
    genero2        = Column(String(1))
    estado_civil2  = Column(String(1))
    dni2           = Column(String(20))
    direccion2     = Column(Text)
    distrito2_id   = Column(Integer, ForeignKey("distritos.id"))

    # Control
    creado_en      = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    sincronizado   = Column(Boolean, default=False)    # Para sync offline→nube

    # Relaciones de distritos
    distrito1 = relationship("Distrito", foreign_keys=[distrito1_id])
    distrito2 = relationship("Distrito", foreign_keys=[distrito2_id])

    @property
    def saldo(self) -> float:
        return round(self.precio - (self.separacion or 0) - (self.pago or 0), 2)

    @property
    def estado(self) -> str:
        """Semáforo: VERDE/AMARILLO/AZUL/ROJO"""
        tiene_coprop = bool(self.copropietario and self.copropietario.strip())
        tiene_saldo  = self.saldo > 0
        if not tiene_coprop and not tiene_saldo:
            return "VERDE"
        if not tiene_coprop and tiene_saldo:
            return "AMARILLO"
        if tiene_coprop and not tiene_saldo:
            return "AZUL"
        return "ROJO"
