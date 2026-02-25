from fastapi import FastAPI
from pydantic import BaseModel

# Imports de Modelos (para inicializar Base)
import app.models.user
import app.models.catalog
import app.models.university
import app.models.empresa
import app.models.usuarios_empresa
import app.models.simulations
import app.models.skill
import app.models.user_progress

# Imports de Routers
from app.api.v1 import content, auth
from app.api.v1 import content, catalogs
from app.api.v1 import content, universities
from app.api.v1 import content, empresas
from app.api.v1 import content, company_users
from app.api.v1 import content, simulations
from app.api.v1 import content, users
from app.api.v1 import content, skills
from app.api.v1 import content, progress

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
# REGISTRO DE ROUTERS
# =============================================================================

# Auth (incluye /register y /token)
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

# Users
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# Empresas
app.include_router(empresas.router, prefix="/api/v1/empresas", tags=["empresas"])

# Universities
app.include_router(universities.router, prefix="/api/v1/universities", tags=["universities"])

# Simulations
app.include_router(simulations.router, prefix="/api/v1/simulaciones", tags=["simulaciones"])

# Catalogs
app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])

# Company Users
app.include_router(company_users.router, prefix="/api/v1", tags=["company-users"])

# Skills (NUEVO)
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])

# Progress (NUEVO)
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])

# NOTA: El endpoint /token está en auth.router (/api/v1/token)
# NO duplicar aquí
