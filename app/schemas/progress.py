"""
Progress Schemas
Pydantic V2 validation for user progress
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class ProgressStatusEnum(str):
    """Progress status values"""
    NOT_STARTED = "not_started"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ProgressCreate(BaseModel):
    """Schema for starting a simulation"""
    user_id: int
    simulation_id: int


class ProgressUpdate(BaseModel):
    """Schema for updating progress"""
    status: Optional[Literal["started", "in_progress", "completed", "abandoned"]] = None
    score: Optional[Decimal] = Field(None, ge=0, le=100)
    completion_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    current_module_id: Optional[int] = None
    current_task_id: Optional[int] = None
    total_time_minutes: Optional[int] = Field(None, ge=0)


class ProgressOut(BaseModel):
    """Schema for progress response"""
    id: int
    user_id: int
    simulation_id: int
    status: str
    score: Decimal
    completion_percentage: Decimal
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    total_time_minutes: int
    current_module_id: Optional[int] = None
    current_task_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
