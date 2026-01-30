"""
Simulation Schemas (Pydantic V2)
Nested schemas for creating/reading simulations
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

# ===========================
# RESOURCE SCHEMAS
# ===========================
class TaskResourceBase(BaseModel):
    name: str
    resource_type: str = "file"
    url: str

class TaskResourceCreate(TaskResourceBase):
    pass

class TaskResourceOut(TaskResourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ===========================
# MODEL ANSWER SCHEMAS
# ===========================
class ModelAnswerBase(BaseModel):
    description: Optional[str] = None
    video_explanation_url: Optional[str] = None
    resource_url: Optional[str] = None
    key_learnings: Optional[List[str]] = []

class ModelAnswerCreate(ModelAnswerBase):
    pass

class ModelAnswerOut(ModelAnswerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ===========================
# TASK SCHEMAS
# ===========================
class ModuleTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    task_type: str = "submission"
    instructor_name: Optional[str] = None
    instructor_role: Optional[str] = None
    instructor_video_url: Optional[str] = None
    estimated_minutes: Optional[int] = 30
    xp_reward: int = 50

class ModuleTaskCreate(ModuleTaskBase):
    # Optional nested creation
    resources: Optional[List[TaskResourceCreate]] = []
    model_answer: Optional[ModelAnswerCreate] = None

class ModuleTaskOut(ModuleTaskBase):
    id: int
    resources: List[TaskResourceOut] = []
    # Model answer is usually hidden until completion, but for admins/creators we show it
    model_answer: Optional[ModelAnswerOut] = None
    model_config = ConfigDict(from_attributes=True)

# ===========================
# MODULE SCHEMAS
# ===========================
class SimulationModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    intro_video_url: Optional[str] = None
    estimated_hours: Optional[float] = 1.0

class SimulationModuleCreate(SimulationModuleBase):
    tasks: Optional[List[ModuleTaskCreate]] = []

class SimulationModuleOut(SimulationModuleBase):
    id: int
    tasks: List[ModuleTaskOut] = []
    model_config = ConfigDict(from_attributes=True)

# ===========================
# SIMULATION SCHEMAS
# ===========================
class SimulationBase(BaseModel):
    title: str
    slug: str
    short_description: str
    full_description: Optional[str] = None
    intro_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    difficulty_level: str = "intermediate"
    estimated_hours: Optional[float] = 5.0
    is_premium: bool = False
    state: str = "draft"

class SimulationCreate(SimulationBase):
    company_id: int
    category_id: int
    # Allow creating full structure at once
    modules: Optional[List[SimulationModuleCreate]] = []

class SimulationUpdate(BaseModel):
    title: Optional[str] = None
    state: Optional[str] = None
    short_description: Optional[str] = None

class SimulationOut(SimulationBase):
    id: int
    company_id: int
    category_id: int
    created_at: datetime
    modules: List[SimulationModuleOut] = []
    
    model_config = ConfigDict(from_attributes=True)

class SimulationList(BaseModel):
    id: int
    title: str
    slug: str
    short_description: str
    thumbnail_url: Optional[str] = None
    company_id: int
    category_id: int
    state: str
    
    model_config = ConfigDict(from_attributes=True)
