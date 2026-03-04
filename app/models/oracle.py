from app.db.base import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Archetype(Base):
    __tablename__ = "arquetipos_psicologicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    color_hex = Column(String(7), nullable=True)
    
    # Pesos base o mínimos para clasificar en este arquetipo
    min_analytical = Column(Integer, default=0)
    min_creative = Column(Integer, default=0)
    min_social = Column(Integer, default=0)
    min_linguistic = Column(Integer, default=0)
    min_hands_on = Column(Integer, default=0)
    
    esta_activo = Column(Boolean, default=True)

class OracleQuestion(Base):
    __tablename__ = "preguntas_oraculo"

    id = Column(Integer, primary_key=True, index=True)
    pregunta = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False)
    orden = Column(Integer, nullable=False)
    dificultad = Column(Integer, default=1)
    esta_activo = Column(Boolean, default=True)

class QuestionOption(Base):
    __tablename__ = "opciones_respuesta"

    id = Column(Integer, primary_key=True, index=True)
    pregunta_id = Column(Integer, ForeignKey("preguntas_oraculo.id", ondelete="CASCADE"), nullable=False)
    texto_opcion = Column(Text, nullable=False)
    orden = Column(Integer, default=1)
    
    # Impacto de esta respuesta en el vector del usuario (-10 a +10)
    peso_analytical = Column(Integer, default=0)
    peso_creative = Column(Integer, default=0)
    peso_social = Column(Integer, default=0)
    peso_linguistic = Column(Integer, default=0)
    peso_hands_on = Column(Integer, default=0)
    
    explicacion = Column(Text, nullable=True)
    
    pregunta = relationship("OracleQuestion", backref="opciones")

class OracleSession(Base):
    __tablename__ = "sesiones_oraculo"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(50), default="iniciada", nullable=False) # iniciada, en_progreso, completada
    paso_actual = Column(Integer, default=1)
    
    # Acumuladores temporales de la sesión
    score_analytical = Column(Integer, default=0)
    score_creative = Column(Integer, default=0)
    score_social = Column(Integer, default=0)
    score_linguistic = Column(Integer, default=0)
    score_hands_on = Column(Integer, default=0)
    
    arquetipo_resultante_id = Column(Integer, ForeignKey("arquetipos_psicologicos.id"), nullable=True)
    
    iniciado_en = Column(DateTime(timezone=True), server_default=func.now())
    completado_en = Column(DateTime(timezone=True), nullable=True)
    
    arquetipo = relationship("Archetype")

class UserOracleAnswer(Base):
    __tablename__ = "respuestas_usuario_oraculo"

    id = Column(Integer, primary_key=True, index=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_oraculo.id", ondelete="CASCADE"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas_oraculo.id", ondelete="CASCADE"), nullable=False)
    opcion_id = Column(Integer, ForeignKey("opciones_respuesta.id", ondelete="CASCADE"), nullable=False)
    tiempo_respuesta_segundos = Column(Integer, nullable=True)
    
    __table_args__ = (UniqueConstraint('sesion_id', 'pregunta_id', name='uq_sesion_pregunta'),)
