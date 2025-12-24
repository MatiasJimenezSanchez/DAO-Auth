"""
Funciones de seguridad y autenticación
"""
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña en texto plano coincide con una hasheada
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada almacenada en BD
        
    Returns:
        True si la contraseña es válida, False en caso contrario
    """
    try:
        # Truncar a 72 bytes (límite de bcrypt)
        plain_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        result = bcrypt.checkpw(plain_bytes, hashed_bytes)
        return result
    except Exception as e:
        print(f"[ERROR] verify_password: {e}")
        return False


def hash_password(password: str) -> str:
    """
    Hashear una contraseña usando bcrypt
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Contraseña hasheada como string
        
    Raises:
        ValueError: Si la contraseña es None
    """
    if password is None:
        raise ValueError("password cannot be None")
    
    # Truncar a 72 bytes (límite de bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crear un token JWT de acceso
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": username})
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodificar y validar un token JWT
    
    Args:
        token: Token JWT
        
    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
