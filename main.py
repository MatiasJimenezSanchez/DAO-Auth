# main.py
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import auth, models, schemas
from database import engine, get_db

# ESTO CREA LAS TABLAS FÍSICAMENTE EN EL ARCHIVO .db
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- NUEVO ENDPOINT: REGISTRO (SIGN UP) ---
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # --- ZONA DE DEBUG ---
    print("--- INICIO DEBUG ---")
    print(f"Tipo de dato recibido: {type(user)}")
    print(f"Contenido del password (raw): '{user.password}'")
    print("--- FIN DEBUG ---")
    
    # 1. Verificar si existe
    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # 2. HASHING (truncar a 72 bytes para bcrypt)
    safe_password = user.password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    hashed_password = auth.get_password_hash(safe_password)
    
    # 3. Crear usuario
    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=user.disabled
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Pasamos la DB al autenticador
    user = auth.get_user(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Asegúrate de importar create_access_token correctamente o definirla
    # Aquí asumo que auth.create_access_token está disponible
    access_token = auth.create_access_token(
        data={"sub": user.username} #, expires_delta=access_token_expires 
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user