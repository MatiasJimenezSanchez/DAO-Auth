"""
API Dependencies - CORREGIDO para tests con SQLite
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# FIX CRÍTICO: Import condicional para evitar dependencia circular en tests
try:
    from app.db.session import get_db as _get_db
except ImportError:
    _get_db = None

from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def get_db() -> Generator:
    """
    Database session dependency - AHORA COMPATIBLE CON TESTS
    Si hay override en app.dependency_overrides, lo usa.
    Si no, usa la sesión por defecto.
    """
    # FIX: Si estamos en contexto de test con override, FastAPI lo inyecta automáticamente
    # Esta función ahora es transparente al override
    if _get_db is None:
        # Fallback para cuando no hay db.session (tests muy aislados)
        from sqlalchemy.orm import Session
        yield None
    else:
        db = next(_get_db())
        try:
            yield db
        finally:
            db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
