"""
Models Package
Imports all models for Alembic detection
"""
from app.models.user import User
from app.models.catalog import Region, Province, City, Industry, ContentCategory, SkillCatalog
from app.models.university import University, Career
from app.models.empresa import Empresa
from app.models.usuarios_empresa import CompanyUser
from app.models.simulations import Simulation, SimulationModule, ModuleTask, TaskResource, ModelAnswer
from app.models.skill import Skill
from app.models.user_progress import UserSimulationProgress
from app.models.ai import RecomendacionIA
from app.models.oracle import Archetype, OracleQuestion, QuestionOption, OracleSession, UserOracleAnswer
from app.models.analytics import Candidate, UserEvent

# FASE 9
from app.models.gamification import (UserModule, TaskSkill, XPTransaction, Achievement, UserAchievement, Mission, UserMission, VirtualMentor, MentorConversation, MentorMessage, OracleMessage)

# FASE 10
from app.models.b2b_university import AcademicProgram, UniversityStudent, ProgramSimulation, UniversityReport
from app.models.analytics import CandidateEvent, SimulationAnalytics, SimulationCohort, ConversionFunnel

__all__ = [
    "User", "Region", "Province", "City", "Industry", "ContentCategory", "SkillCatalog",
    "University", "Career", "Empresa", "CompanyUser", "Simulation", "SimulationModule", 
    "ModuleTask", "TaskResource", "ModelAnswer", "Skill", "UserSimulationProgress",
    "RecomendacionIA", "Archetype", "OracleQuestion", "QuestionOption", "OracleSession", 
    "UserOracleAnswer", "Candidate", "UserEvent", "UserModule", "TaskSkill", "XPTransaction", 
    "Achievement", "UserAchievement", "Mission", "UserMission", "VirtualMentor", 
    "MentorConversation", "MentorMessage", "OracleMessage",
    "AcademicProgram", "UniversityStudent", "ProgramSimulation", "UniversityReport",
    "CandidateEvent", "SimulationAnalytics", "SimulationCohort", "ConversionFunnel"
]
