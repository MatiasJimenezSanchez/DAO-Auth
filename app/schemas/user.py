from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- USER BASE ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    
    # CAMPOS EXTENDIDOS (INGLES)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    region_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None

# --- CREATION SCHEMAS ---
class UserCreate(UserBase):
    password: str

# ESTA CLASE FALTABA Y CAUSABA EL ERROR DE IMPORTACIÓN
class UserCreateWithLocation(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    # Ubicacion (Ingles)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    region_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None

# --- UPDATE/READ SCHEMAS ---
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    city_id: Optional[int] = None

class UserOut(UserBase):
    id: int
    xp_total: int = 0
    current_level: int = 1
    esta_activo: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserOut):
    hashed_password: str
