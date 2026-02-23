from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Imports de Modelos (para inicializar Base)
import app.models.user
import app.models.catalog
import app.models.university
import app.models.empresa
import app.models.usuarios_empresa  # IMPORTAR NUEVO MODELO
import app.models.simulations
import app.models.skill
import app.models.user_progress

# Imports de Routers
from app.api.v1 import auth
from app.api.v1 import catalogs
from app.api.v1 import universities
from app.api.v1 import empresas
from app.api.v1 import company_users
from app.api.v1 import simulations
from app.api.v1 import users
from app.api.v1 import skills
from app.api.v1 import progress

from app.db.session import get_db

class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(
    title="Aurum API", 
    version="1.0.0",
    description="Backend para simulaciones educativas empresariales"
)

@app.get("/")
def root():
    return {"status": "online", "message": "Aurum API v1.0"}

# =============================================================================
# REGISTRO DE ROUTERS - CONFIGURACIÓN CANÓNICA CORREGIDA
# =============================================================================
# IMPORTANTE: 
# - Los routers usan @router.get("") sin slash
# - El prefix aquí define la ruta completa
# - Para /me: está en users router → /api/v1/users/me

# Auth (sin subrutas específicas)
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

# Users (IMPORTANTE: /me está aquí → /api/v1/users/me)
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# Empresas (español)
app.include_router(empresas.router, prefix="/api/v1/empresas", tags=["empresas"])

# Universities (inglés)
app.include_router(universities.router, prefix="/api/v1/universities", tags=["universities"])

# Simulations (español: simulaciones)
app.include_router(simulations.router, prefix="/api/v1/simulaciones", tags=["simulaciones"])

# Catalogs (sin subrutas específicas)
app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])

# Company Users (sin subrutas específicas)
app.include_router(company_users.router, prefix="/api/v1", tags=["company-users"])

# =============================================================================
# ENDPOINT DE LOGIN (Token OAuth2)
# =============================================================================
app.include_router(skills.router, prefix="/api/v1", tags=["skills"])

app.include_router(progress.router, prefix="/api/v1", tags=["progress"])

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """Endpoint de autenticación OAuth2"""
    user = auth.get_user(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
