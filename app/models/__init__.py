"""
Models Package
Importa todos los modelos para que Alembic los detecte
"""
from app.models.user import User
from app.models.catalog import (
    Region, Province, City, 
    Industry, ContentCategory, SkillCatalog
)
from app.models.university import University, Career
from app.models.empresa import Empresa
from app.models.usuarios_empresa import CompanyUser
from app.models.simulations import (
    Simulation, SimulationModule, ModuleTask,
    TaskResource, ModelAnswer
)

__all__ = [
    "User",
    "Region", "Province", "City",
    "Industry", "ContentCategory", "SkillCatalog",
    "University", "Career",
    "Empresa", "CompanyUser",
    "Simulation", "SimulationModule", "ModuleTask"
]
