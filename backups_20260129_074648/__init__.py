"""
Models Package
Importa todos los modelos para que Alembic los detecte
VERSIÓN: NOMBRES EN INGLÉS
"""
from app.models.user import User
from app.models.catalog import Region, Province, City
from app.models.university import Universidad, Carrera
from app.models.empresa import Empresa

__all__ = [
    "User",
    "Region",
    "Province",
    "City",
    "Universidad",
    "Carrera",
    "Empresa"
]
