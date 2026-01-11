from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime
from typing import Literal


# Esquema para crear un usuario con gamificación y ubicación
class UserCreateWithLocation(BaseModel):
    """Esquema para crear un usuario extendido con ubicación y gamificación"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    disabled: bool = False
    city_id: Optional[int] = None
    province_id: Optional[int] = None
    region_id: Optional[int] = None
    birth_date: Optional[date] = None
    gender: Optional[Literal["masculino", "femenino", "otro", "prefiero_no_decir"]] = None
    accepts_terms: bool = False
    accepts_privacy: bool = False
    current_level: int = 1  # Nivel inicial
    xp_total: int = 0  # Puntos totales de experiencia
    streak_days: int = 0  # Días de racha


# Esquema base para los usuarios
class UserBase(BaseModel):
    """Campos base de usuario (compartidos entre crear y leer)"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    # Nuevos campos opcionales
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    region_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None


# Esquema para leer un usuario
class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    current_level: int = 1
    xp_total: int = 0
    streak_days: int = 0
    region_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Esquema para el usuario con la contraseña hasheada (interno)
class UserInDB(UserOut):
    """Usuario con contraseña hasheada (solo para uso interno)"""
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)



# Esquema para la creación de usuario
class UserCreate(BaseModel):
    """Esquema para crear un usuario"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    disabled: bool = False
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    region_id: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None

    model_config = ConfigDict()
