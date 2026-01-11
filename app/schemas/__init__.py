# app/schemas/__init__.py - VERSIÓN MÍNIMA
from app.schemas.user import UserCreate, UserOut
from app.schemas.catalog import RegionOut, ProvinceOut, CityOut

__all__ = [
    "UserCreate",
    "UserOut",
    "RegionOut",
    "ProvinceOut",
    "CityOut",
]