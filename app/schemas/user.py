"""
Esquemas Pydantic para usuarios
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TokenData(BaseModel):
    """Datos del token JWT"""
    username: Optional[str] = None


class Token(BaseModel):
    """Respuesta de token de autenticación"""
    access_token: str
    token_type: str


class UserBase(BaseModel):
    """Campos base de usuario (compartidos entre crear y leer)"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserCreate(UserBase):
    """Esquema para crear un usuario (incluye contraseña)"""
    password: str


class User(UserBase):
    """Esquema para leer un usuario (sin contraseña, con ID)"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Permite leer desde objetos SQLAlchemy


class UserInDB(User):
    """Usuario con contraseña hasheada (solo para uso interno)"""
    hashed_password: str
    
    class Config:
        from_attributes = True
