"""
Modelo de Empresas Partner (B2B)
Versión corregida sin FK a tabla inexistente
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL
from sqlalchemy.sql import func
from app.db.base import Base


class Empresa(Base):
    """
    Modelo de Empresas Partner estilo Forage/edX
    Representa empresas que crean simulaciones educativas
    """
    __tablename__ = "empresas"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    
    # Clasificación - CORREGIDO: Cambio de FK a String
    tipo_empresa = Column(String(50), nullable=False, default="real_nacional")
    # Cambiado de industria_id (FK) a industria (String)
    industria = Column(String(100), nullable=False, default="Tecnología")
    industria_secundaria = Column(String(100), nullable=True)
    
    # Información pública
    descripcion_corta = Column(String(500))
    descripcion_completa = Column(Text)
    mision = Column(Text)
    vision = Column(Text)
    
    # Branding
    url_logo = Column(String(500))
    url_banner = Column(String(500))
    url_sitio_web = Column(String(500))
    color_primario = Column(String(7))
    
    # Redes sociales
    linkedin_url = Column(String(500))
    twitter_url = Column(String(500))
    
    # Contacto
    email_contacto = Column(String(255))
    telefono = Column(String(20))
    pais = Column(String(100), default="Ecuador")
    ciudad = Column(String(100))
    
    # Partnership
    es_partner_activo = Column(Boolean, default=False, nullable=False)
    tipo_partnership = Column(String(50), default="basico")
    
    # Límites según plan
    max_simulaciones_activas = Column(Integer, default=5)
    max_usuarios_admin = Column(Integer, default=3)
    
    # Verificación
    verificado = Column(Boolean, default=False)
    
    # Métricas agregadas
    total_simulaciones = Column(Integer, default=0)
    total_usuarios_inscritos = Column(Integer, default=0)
    calificacion_promedio = Column(DECIMAL(3, 2), default=0.0)
    
    # Estado
    esta_activo = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Empresa {self.nombre_empresa}>"
    
    class Config:
        orm_mode = True
