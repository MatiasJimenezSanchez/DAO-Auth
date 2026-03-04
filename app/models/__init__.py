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
from app.models.ai import RecomendacionIA
from app.models.oracle import Archetype, OracleQuestion, QuestionOption, OracleSession, UserOracleAnswer
from app.models.analytics import Candidate, UserEvent

# FASE 9: Gamificación, Progreso Profundo y Mentores IA
from app.models.gamification import (
    UserModule, TaskSkill, XPTransaction,
    Achievement, UserAchievement,
    Mission, UserMission,
    VirtualMentor, MentorConversation, MentorMessage,
    OracleMessage
)

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
    # Progress
    "Skill",
    "UserSimulationProgress",
    # AI
    "RecomendacionIA",
    # Oracle
    "Archetype",
    "OracleQuestion",
    "QuestionOption",
    "OracleSession",
    "UserOracleAnswer",
    # Analytics
    "Candidate",
    "UserEvent",
    # FASE 9: Gamification
    "UserModule",
    "TaskSkill",
    "XPTransaction",
    "Achievement",
    "UserAchievement",
    "Mission",
    "UserMission",
    "VirtualMentor",
    "MentorConversation",
    "MentorMessage",
    "OracleMessage"
]
