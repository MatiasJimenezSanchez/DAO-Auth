# app/main.py - VERSIÓN SIN Token
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Imports simplificados
from app.schemas.user import UserCreate, UserOut
from app.schemas.catalog import RegionOut, ProvinceOut, CityOut

from app.api.v1 import auth
from app.api.v1 import catalogs

from app.db.session import get_db
from app.models.user import User as UserModel

import app.models.user
import app.models.catalog

# Definir Token aquí directamente
class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(
    title="Aurum API",
    description="API de autenticación y catálogos geográficos",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Bienvenido a Aurum API", "status": "online", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(catalogs.router, prefix="/api/v1")

@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = UserModel(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=user.disabled if user.disabled is not None else False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = auth.get_user(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: UserModel = Depends(auth.get_current_user)):
    return current_user