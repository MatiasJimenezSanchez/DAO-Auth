from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importar primero los modelos para registrarlos
from app import schemas
from app.api.v1 import auth
from app.db.base import engine
from app.db.session import get_db
from app.models import User

# Importar modelos para registrar metadatos (no crear tablas aquí)
import app.models.user  # ensures model classes are imported for Alembic autogenerate

app = FastAPI(
    title="DAO API",
    description="API de autenticación con FastAPI y JWT",
    version="1.0.0"
)


@app.get("/")
def root():
    """Endpoint raíz - Verificar que la API está funcionando"""
    return {
        "message": "Bienvenido a Aurum API",
        "status": "online",
        "docs": "/docs"
    }


@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Endpoint para registrar un nuevo usuario"""
    db_user = auth.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    hashed_password = auth.get_password_hash(user.password)
    new_user = User(
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


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint para login y obtener token JWT"""
    user = auth.get_user(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    """Endpoint para obtener información del usuario autenticado"""
    return current_user
