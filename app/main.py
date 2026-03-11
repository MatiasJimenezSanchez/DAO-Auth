"""
Delphos API - main.py v2.0
Fase 14: Catálogos + Oráculo + Infrastructure
"""
from fastapi import FastAPI
from pydantic import BaseModel

# =============================================================================
# IMPORTAR TODOS LOS MODELOS (registro en Base.metadata)
# Orden: base → catálogos → entidades → features
# =============================================================================
import app.models.user
import app.models.catalog
import app.models.university
import app.models.empresa
import app.models.usuarios_empresa
import app.models.simulations
import app.models.skill
import app.models.user_progress
import app.models.ai
import app.models.oracle
import app.models.analytics
import app.models.gamification
import app.models.b2b_university
import app.models.enterprise
import app.models.progress
import app.models.infrastructure

# =============================================================================
# IMPORTAR ROUTERS (orden alfabético)
# =============================================================================
from app.api.v1 import (
    auth,
    catalogs,
    company_users,
    content,
    empresas,
    oracle,
    progress,
    simulations,
    skills,
    universities,
    users,
)

from app.db.session import get_db


class Token(BaseModel):
    access_token: str
    token_type: str


# =============================================================================
# APP
# =============================================================================
app = FastAPI(
    title="Delphos API",
    version="1.4.0",
    description="Backend para simulaciones educativas empresariales - Fase 14"
)


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Delphos API v1.4.0",
        "phase": "14 - Catálogos + Oráculo + Infrastructure"
    }


# =============================================================================
# REGISTRO DE ROUTERS
# =============================================================================
app.include_router(auth.router,          prefix="/api/v1",              tags=["auth"])
app.include_router(catalogs.router,      prefix="/api/v1",              tags=["catalogs"])
app.include_router(company_users.router, prefix="/api/v1",              tags=["company-users"])
app.include_router(content.router,       prefix="/api/v1",              tags=["content"])
app.include_router(empresas.router,      prefix="/api/v1/empresas",     tags=["empresas"])
app.include_router(oracle.router,        prefix="/api/v1/oracle",       tags=["oracle"])
app.include_router(progress.router,      prefix="/api/v1",              tags=["progress"])
app.include_router(simulations.router,   prefix="/api/v1/simulaciones", tags=["simulaciones"])
app.include_router(skills.router,        prefix="/api/v1/skills",       tags=["skills"])
app.include_router(universities.router,  prefix="/api/v1/universities", tags=["universities"])
app.include_router(users.router,         prefix="/api/v1/users",        tags=["users"])
