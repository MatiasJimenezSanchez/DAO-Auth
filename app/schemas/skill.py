"""
Skill Schemas
Pydantic V2 validation for Skills
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SkillBase(BaseModel):
    """Base skill schema"""
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    category: str = Field(default='technical', pattern='^(technical|soft|language|tool)$')


class SkillCreate(SkillBase):
    """Schema for creating skill"""
    catalog_skill_id: Optional[int] = None


class SkillUpdate(BaseModel):
    """Schema for updating skill"""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    category: Optional[str] = Field(None, pattern='^(technical|soft|language|tool)$')
    is_active: Optional[bool] = None


class SkillOut(SkillBase):
    """Schema for skill response"""
    id: int
    catalog_skill_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
