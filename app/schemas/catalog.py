# app/schemas/catalog.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class RegionOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class ProvinceOut(BaseModel):
    id: int
    code: str
    name: str
    region_id: int
    is_active: bool

    class Config:
        from_attributes = True

class CityOut(BaseModel):
    id: int
    name: str  # ← SIN 'code' porque la tabla no lo tiene
    province_id: int
    is_capital: Optional[bool] = None
    population: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True