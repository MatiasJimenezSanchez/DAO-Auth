"""
app/schemas/simulations.py — Schema canónico de Simulaciones (Fase 15)
Consolida simulation.py + simulations.py. simulation.py importa desde aquí.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# =============================================================================
# SIMULATION SCHEMAS
# =============================================================================

class SimulationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    short_description: str = Field(..., min_length=1, max_length=500)
    full_description: Optional[str] = None
    company_id: int
    category_id: int
    difficulty_level: str = Field(default="intermediate")
    estimated_hours: Optional[Decimal] = None
    xp_reward: int = Field(default=500, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_spots: int = Field(default=0)
    state: str = Field(default="draft")


class SimulationCreate(SimulationBase):
    pass


class SimulationUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    difficulty_level: Optional[str] = None


class SimulationOut(SimulationBase):
    id: int
    available_spots: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# MODULE SCHEMAS
# =============================================================================

class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    simulation_id: int
    order: int = Field(..., ge=1)


class ModuleCreate(ModuleBase):
    description: Optional[str] = None


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)


class ModuleOut(ModuleBase):
    id: int
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# TASK SCHEMAS
# =============================================================================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    module_id: int
    order: int = Field(..., ge=1)
    task_type: str = Field(..., pattern="^(video|quiz|pdf|text|code|submission)$")


class TaskCreate(TaskBase):
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    task_type: Optional[str] = None


class TaskOut(TaskBase):
    id: int
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# RESOURCE SCHEMAS
# =============================================================================

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    url: str = Field(..., min_length=1, max_length=500)
    task_id: int

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ResourceCreate(ResourceBase):
    resource_type: Optional[str] = "file"


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None


class ResourceOut(ResourceBase):
    id: int
    resource_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
