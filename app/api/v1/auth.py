"""
Authentication Router
Handles user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.user import Token, TokenRefresh, UserCreate, UserOut
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    
    Authenticates user credentials and returns JWT access token
    
    Args:
        form_data: OAuth2 form with username and password
        db: Database session
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    service = UserService(db)
    user = service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(subject=user.email)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user
    
    Creates a new user account with hashed password
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserOut: Created user data (without password)
        
    Raises:
        HTTPException: 400 if email or username already exists
    """
    service = UserService(db)
    return service.create_user(user_data)


@router.get("/users/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile
    
    Returns the profile of the currently logged-in user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserOut: Current user profile
    """
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Obtiene un nuevo Access Token enviando un Refresh Token válido.
    """
    from jose import jwt, JWTError
    from app.core.security import SECRET_KEY, ALGORITHM, create_access_token, create_refresh_token
    from fastapi import HTTPException, status
    from app.models.user import User
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        # Verificar que efectivamente sea un refresh token
        if email is None or payload.get("type") != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise credentials_exception
        
    # Generar nuevo par de tokens
    new_access_token = create_access_token(subject=user.email)
    new_refresh_token = create_refresh_token(subject=user.email)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
