# schemas.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

# Esquema para CREAR un usuario (lo que envía el frontend al registrarse)
class UserCreate(UserBase):
    password: str

# Esquema para LEER un usuario (lo que devuelve la API)
class User(UserBase):
    id: int # El ID lo genera la DB, así que va aquí

    class Config:
        from_attributes = True # ¡Crucial! Permite leer datos de SQLAlchemy

class UserInDB(User):
    hashed_password: str