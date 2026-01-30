# app/models/catalog.py
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, Numeric
)
from app.db.base import Base
from sqlalchemy.orm import relationship

class Region(Base):
    __tablename__ = "regions"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    code        = Column(String(10),  unique=True, nullable=False)
    description = Column(Text)
    map_color   = Column(String(7))
    order       = Column(Integer, default=1)
    is_active   = Column(Boolean, default=True)

    provinces = relationship("Province", back_populates="region")


class Province(Base):
    __tablename__ = "provinces"

    id          = Column(Integer, primary_key=True, index=True)
    region_id   = Column(Integer, ForeignKey("regions.id"), nullable=False)
    name        = Column(String(100), unique=True, nullable=False)
    code        = Column(String(10),  unique=True, nullable=False)
    capital     = Column(String(100))
    population  = Column(Integer)
    is_active   = Column(Boolean, default=True)

    region = relationship("Region", back_populates="provinces")
    cities = relationship("City",   back_populates="province")


class City(Base):
    __tablename__ = "cities"

    id            = Column(Integer, primary_key=True, index=True)
    province_id   = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    name          = Column(String(100), nullable=False)
    is_capital    = Column(Boolean, default=False)
    population    = Column(Integer)
    latitude      = Column(Numeric(10, 8))
    longitude     = Column(Numeric(11, 8))
    is_active     = Column(Boolean, default=True)

    province = relationship("Province", back_populates="cities")