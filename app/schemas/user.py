from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

# --- TOKEN SCHEMAS (Auth) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    
class UserCreate(UserBase):
    password: str
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

class UserOut(UserBase):
    id: int
    is_active: bool
    xp_total: int = 0
    level_current: int = 1
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserOut):
    hashed_password: str
