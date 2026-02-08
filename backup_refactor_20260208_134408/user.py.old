# app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    # Campos extendidos
    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    # Ubicación (FK a catálogos)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)

    # Gamificación
    xp_total = Column(Integer, default=0)
    current_level = Column(Integer, default=1)

    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())