from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Imports de Schemas y Modelos
from app.schemas.user import UserOut
from app.models.user import User as UserModel
import app.models.user
import app.models.catalog
import app.models.university

# Imports de Routers (Explicitos para evitar confusion)
from app.api.v1 import auth
from app.api.v1 import catalogs
from app.api.v1 import universities
from app.api.v1 import empresas
from app.api.v1.users import router as users_router # IMPORTACION DIRECTA DEL ARCHIVO

from app.db.session import get_db

class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(title="Aurum API", version="1.0.0")

@app.get("/")
def root():
    return {"status": "online"}

# Registro de Routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])
app.include_router(universities.router, prefix="/api/v1", tags=["universities"])
app.include_router(empresas.router, prefix="/api/v1/empresas", tags=["empresas"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"]) # Usamos el router importado explícitamente

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
