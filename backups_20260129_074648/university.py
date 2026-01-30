from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class UniversityType(str, enum.Enum):
    public = 'publica'
    private = 'privada'
    cofinanced = 'cofinanciada'

class AccreditationType(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    pending = 'en_proceso'

class University(Base):
    __tablename__ = 'universities'
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    acronym = Column(String(20))
    university_type = Column(SQLEnum(UniversityType), nullable=False)
    accreditation = Column(SQLEnum(AccreditationType))
    description = Column(Text)
    website = Column(String(200))
    logo_url = Column(String(300))
    
    # Ubicación
    city_id = Column(Integer, ForeignKey('cities.id'))
    address = Column(String(300))
    
    # Contacto
    phone = Column(String(50))
    email = Column(String(100))
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Relationships
    careers = relationship('Career', back_populates='university')

class Career(Base):
    __tablename__ = 'careers'
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    duration_semesters = Column(Integer)  # Duración en semestres
    
    university_id = Column(Integer, ForeignKey('universities.id'), nullable=False)
    
    # Modalidad
    modality = Column(String(50))  # presencial, online, hibrida
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    university = relationship('University', back_populates='careers')
