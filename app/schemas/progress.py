"""
app/schemas/progress.py — Schemas de progreso de usuario (Fase 15)
Alineado con UserSimulation (tabla: simulaciones_usuario)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class EnrollmentCreate(BaseModel):
    """Body para POST /api/v1/simulaciones/{id}/inscribir"""
    # simulation_id viene de la URL, no del body
    pass


class TaskSubmission(BaseModel):
    task_id: int = Field(..., gt=0)
    respuesta_texto: Optional[str] = Field(None, max_length=10000)


class UserSimulationOut(BaseModel):
    """Respuesta de matrícula o listado de simulaciones del usuario."""
    id: int
    user_id: int
    simulation_id: int
    estado: str
    porcentaje_completado: Decimal
    tiempo_total_minutos: int
    inscrito_en: datetime
    completado_en: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Alias para compatibilidad con progress.py router legacy
UserProgressOut = UserSimulationOut


class EnrollmentResponse(BaseModel):
    """Respuesta enriquecida de inscripción."""
    status: str
    enrollment: UserSimulationOut
    spots_left: int
