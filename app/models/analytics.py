from app.db.base import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Candidate(Base):
    """
    Pipeline de reclutamiento (ATS) para empresas.
    """
    __tablename__ = "candidatos_empresa"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    origen = Column(String(50), nullable=False, comment="simulacion_completada, top_performer, etc.")
    simulacion_origen_id = Column(Integer, ForeignKey("simulations.id", ondelete="SET NULL"), nullable=True)
    
    estado_candidato = Column(String(50), default="nuevo", nullable=False, index=True)
    
    # Evaluación y notas
    puntuacion_total = Column(Integer, nullable=True, comment="0-100")
    notas_internas = Column(Text, nullable=True)
    etiquetas = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    
    contactado = Column(Boolean, default=False)
    fecha_contacto = Column(DateTime(timezone=True), nullable=True)
    
    fecha_agregado = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('empresa_id', 'usuario_id', name='uq_empresa_candidato'),)

class UserEvent(Base):
    """
    Telemetría y Clickstream (Data Lake inicial para ML).
    """
    __tablename__ = "eventos_usuario"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    evento = Column(String(100), nullable=False, index=True, comment="page_view, button_click, video_play")
    categoria = Column(String(50), nullable=False, index=True, comment="navegacion, progreso, etc.")
    
    referencia_id = Column(Integer, nullable=True)
    referencia_tipo = Column(String(50), nullable=True)
    
    # OJO: Se usa 'metadata_evento' en Python para no chocar con Base.metadata de SQLAlchemy
    metadata_evento = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True, comment="JSON con data flexible del evento")
    
    sesion_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    plataforma = Column(String(50), nullable=True)
    
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
