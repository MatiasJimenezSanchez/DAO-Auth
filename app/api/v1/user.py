"""
Endpoints para operaciones de usuario (CRUD)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.services.user_service import UserService
from app.api.v1.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """
    Endpoint para registrar un nuevo usuario
    
    - **username**: Nombre de usuario único
    - **email**: Correo electrónico único
    - **password**: Contraseña (se guardará hasheada)
    - **full_name**: Nombre completo (opcional)
    - **disabled**: Si el usuario está deshabilitado (opcional, default: False)
    """
    service = UserService(db)
    return service.register_user(user)


@router.get("/", response_model=list[User])
def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[User]:
    """
    Obtener lista de usuarios (paginada)
    
    Requiere autenticación
    """
    service = UserService(db)
    return service.get_all_users(skip, limit)


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Endpoint para obtener información del usuario autenticado
    
    Requiere: Header Authorization: Bearer {token}
    """
    return current_user


@router.get("/{username}", response_model=User)
def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Endpoint para obtener información de un usuario específico
    
    Requiere autenticación
    """
    service = UserService(db)
    return service.get_user_by_username(username)


@router.put("/me/update", response_model=User)
async def update_user_me(
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Endpoint para actualizar información del usuario autenticado
    
    Requiere: Header Authorization: Bearer {token}
    """
    service = UserService(db)
    
    # Actualizar solo los campos no-contraseña
    return service.update_user(
        current_user.id,
        email=user_update.email,
        full_name=user_update.full_name,
        disabled=user_update.disabled
    )


@router.post("/me/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Endpoint para cambiar la contraseña del usuario autenticado
    
    Requiere: Header Authorization: Bearer {token}
    """
    service = UserService(db)
    service.change_password(current_user.id, old_password, new_password)
    
    return {"message": "Contraseña actualizada exitosamente"}


@router.delete("/{username}")
def delete_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Endpoint para eliminar un usuario
    
    Solo para desarrollo - Implementar roles/permisos en producción
    """
    service = UserService(db)
    
    # No permitir que un usuario se elimine a sí mismo
    if current_user.username == username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )
    
    service.delete_user_by_username(username)
    
    return {"message": f"Usuario '{username}' eliminado exitosamente"}


# Health check
@router.get("/health", tags=["health"])
def health_check() -> dict:
    """Endpoint de salud para monitoreo"""
    return {"status": "healthy"}
