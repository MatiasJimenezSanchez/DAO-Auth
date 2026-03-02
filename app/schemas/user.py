from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    city_id: Optional[int] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city_id: Optional[int] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


    # --- Validaciones Estrictas IA (0-100) ---
    analytical_score: int = Field(default=0, ge=0, le=100, description="Score analítico")
    creative_score: int = Field(default=0, ge=0, le=100, description="Score creativo")
    social_score: int = Field(default=0, ge=0, le=100, description="Score social")
    linguistic_score: int = Field(default=0, ge=0, le=100, description="Score lingüístico")
    hands_on_score: int = Field(default=0, ge=0, le=100, description="Score práctico")

class UserOut(UserBase):
    id: int
    is_active: bool
    xp_total: int = 0
    level_current: int = 1
    created_at: datetime
    # CRITICAL: Include ALL optional profile fields
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    city_id: Optional[int] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserOut):
    hashed_password: str
