"""
app/schemas/b2b.py — Schemas para el Dashboard de Empresas (Fase 17)
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from decimal import Decimal

class UserEnrollmentDetail(BaseModel):
    user_id: int
    full_name: str
    email: str
    simulation_id: int
    simulation_title: str
    estado: str
    porcentaje_completado: Decimal
    tiempo_total_minutos: int
    
    model_config = ConfigDict(from_attributes=True)

class SimulationStats(BaseModel):
    simulation_id: int
    title: str
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    avg_completion_percentage: float

class B2BDashboardOut(BaseModel):
    company_id: int
    total_simulations: int
    total_students_enrolled: int
    overall_completion_rate: float
    simulations_stats: List[SimulationStats]
    recent_enrollments: List[UserEnrollmentDetail]
