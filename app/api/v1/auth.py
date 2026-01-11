import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# Importaciones corregidas
from app.models import User
from app.schemas.user import TokenData, Token, UserCreateWithLocation, UserOut
from app.db.session import get_db
from app.services.user_service import UserService  # IMPORTACIÓN DE UserService CORREGIDA


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña coincida con el hash"""
    try:
        plain_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception as e:
        print(f"[ERROR] verify_password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt de la contraseña"""
    if password is None:
        raise ValueError("password cannot be None")
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: Session, username: str):
    """Busca un usuario en la base de datos"""
    return db.query(User).filter(User.username == username).first()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtiene el usuario actual a partir del token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register-full", response_model=UserOut, status_code=201)
def register_extended(payload: UserCreateWithLocation, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un usuario extendido con ubicación y gamificación.
    
    - **username**: Nombre de usuario único
    - **email**: Correo electrónico único
    - **password**: Contraseña (se guardará hasheada)
    - **full_name**: Nombre completo (opcional)
    - **disabled**: Si el usuario está deshabilitado (opcional, default: False)
    - **city_id, province_id, region_id**: Información de ubicación
    - **accepts_terms**: Aceptación de términos
    - **accepts_privacy**: Aceptación de privacidad
    """
    service = UserService(db)  # Instancia correctamente UserService
    return service.register_user_extended(payload)
