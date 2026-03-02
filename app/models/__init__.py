"""
Models Package
Imports all models for Alembic detection
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
from app.models.skill import Skill
from app.models.user_progress import UserSimulationProgress

__all__ = [
    "User",
    # Geographic
    "Region",
    "Province",
    "City",
    # Business
    "Industry",
    "ContentCategory",
    "SkillCatalog",
    # Education
    "University",
    "Career",
    # B2B
    "Empresa",
    "CompanyUser",
    # Simulations
    "Simulation",
    "SimulationModule",
    "ModuleTask",
    "TaskResource",
    "ModelAnswer",
    # NEW
    "Skill",
    "UserSimulationProgress"
]

from .ai import RecomendacionIA
