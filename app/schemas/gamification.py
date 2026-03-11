"""
app/schemas/gamification.py — Schemas de Gamificación (Fase 16)
Mantiene todos los schemas existentes + agrega los de Fase 16.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# =============================================================================
# PROGRESO Y ECONOMÍA (existentes)
# =============================================================================

class UserModuleOut(BaseModel):
    id: int
    user_id: int
    module_id: int
    estado: str
    porcentaje_completado: Decimal = Field(ge=0, le=100)
    tiempo_dedicado_minutos: int = Field(ge=0)
    fecha_inicio: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskSkillCreate(BaseModel):
    task_id: int
    skill_id: int
    xp_ganado: int = Field(default=10, ge=0)
    peso: Decimal = Field(default=1.0, ge=0, le=2.0)


class TaskSkillOut(BaseModel):
    id: int
    task_id: int
    skill_id: int
    xp_ganado: int
    peso: Decimal
    model_config = ConfigDict(from_attributes=True)


class XPTransactionCreate(BaseModel):
    user_id: int
    cantidad_xp: int
    tipo_fuente: str = Field(pattern="^(tarea|logro|mision|bonus|penalizacion)$")
    fuente_id: Optional[int] = None
    descripcion: str = Field(min_length=1, max_length=500)


class XPTransactionOut(BaseModel):
    id: int
    user_id: int
    cantidad_xp: int
    tipo_fuente: str
    descripcion: str
    xp_anterior: int
    xp_nuevo: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AchievementCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str = Field(min_length=1)
    tipo_logro: str = Field(pattern="^(bronce|plata|oro|platino)$")
    recompensa_xp: int = Field(default=0, ge=0)


class AchievementOut(BaseModel):
    id: int
    titulo: str
    descripcion: str
    tipo_logro: str
    recompensa_xp: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserAchievementOut(BaseModel):
    id: int
    user_id: int
    logro_id: int
    desbloqueado: bool
    fecha_desbloqueo: datetime
    model_config = ConfigDict(from_attributes=True)


class MissionCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str = Field(min_length=1)
    objetivo_tipo: str = Field(min_length=1, max_length=100)
    objetivo_cantidad: int = Field(ge=1)
    recompensa_xp: int = Field(default=0, ge=0)


class MissionOut(BaseModel):
    id: int
    titulo: str
    descripcion: str
    objetivo_tipo: str
    objetivo_cantidad: int
    recompensa_xp: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserMissionOut(BaseModel):
    id: int
    user_id: int
    mision_id: int
    progreso_actual: int
    estado: str
    fecha_inicio: datetime
    model_config = ConfigDict(from_attributes=True)


class VirtualMentorCreate(BaseModel):
    empresa_id: int
    nombre: str = Field(min_length=1, max_length=200)
    personalidad: str = Field(default="profesional")
    prompt_sistema: str = Field(min_length=1)
    modelo_ia: str = Field(default="gpt-4")


class VirtualMentorOut(BaseModel):
    id: int
    empresa_id: int
    nombre: str
    personalidad: str
    modelo_ia: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class MentorMessageCreate(BaseModel):
    conversacion_id: int
    rol: str = Field(pattern="^(user|assistant|system)$")
    contenido: str = Field(min_length=1)


class MentorMessageOut(BaseModel):
    id: int
    conversacion_id: int
    rol: str
    contenido: str
    tokens_usados: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OracleMessageCreate(BaseModel):
    sesion_id: int
    rol: str = Field(pattern="^(user|assistant|system)$")
    contenido: str = Field(min_length=1)


class OracleMessageOut(BaseModel):
    id: int
    sesion_id: int
    rol: str
    contenido: str
    tokens_usados: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# FASE 16 — NUEVOS SCHEMAS
# =============================================================================

class AwardXPRequest(BaseModel):
    """Body para POST /gamification/award-xp"""
    user_id: int = Field(..., gt=0)
    cantidad_xp: int = Field(..., gt=0, description="XP a otorgar (debe ser positivo)")
    tipo_fuente: str = Field(
        default="bonus",
        pattern="^(tarea|logro|mision|bonus|penalizacion)$",
    )
    fuente_id: Optional[int] = Field(None, description="ID de la tarea/logro/misión origen")
    descripcion: str = Field(..., min_length=1, max_length=500)


class AwardXPResponse(BaseModel):
    """Respuesta de otorgamiento de XP con info de nivel."""
    transaction: XPTransactionOut
    xp_anterior: int
    xp_nuevo: int
    nivel_anterior: int
    nivel_nuevo: int
    subio_de_nivel: bool
    xp_para_siguiente_nivel: int


class LeaderboardEntry(BaseModel):
    """Entrada en el leaderboard."""
    rank: int
    user_id: int
    username: str
    full_name: str
    xp_total: int
    level_current: int
    avatar_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class LeaderboardResponse(BaseModel):
    """Respuesta del leaderboard con paginación."""
    total: int
    entries: List[LeaderboardEntry]
