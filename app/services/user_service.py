"""
Servicio para lógica de negocio de usuarios
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, User
from app.core.security import verify_password, hash_password


class UserService:
    """Servicio para operaciones de usuario"""
    
    def __init__(self, db: Session):
        """
        Inicializar el servicio con una sesión de BD
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.repository = UserRepository(db)
    
    def register_user(self, user_create: UserCreate) -> User:
        """
        Registrar un nuevo usuario
        
        Args:
            user_create: Datos del usuario a registrar
            
        Returns:
            Usuario registrado
            
        Raises:
            HTTPException: Si el usuario o email ya existen
        """
        # Verificar que el usuario no exista
        if self.repository.get_user_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya existe"
            )
        
        # Verificar que el email no esté registrado
        if user_create.email and self.repository.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear el usuario
        db_user = self.repository.create_user(user_create)
        return User.from_orm(db_user)
    
    def authenticate_user(self, username: str, password: str) -> User:
        """
        Autenticar un usuario verificando su contraseña
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Usuario autenticado
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        user = self.repository.get_user_by_username(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario deshabilitado. Contacta al administrador."
            )
        
        return User.from_orm(user)
    
    def get_user_by_username(self, username: str) -> User:
        """
        Obtener un usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Usuario encontrado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.repository.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario '{username}' no encontrado"
            )
        return User.from_orm(user)
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        Obtener un usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario encontrado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return User.from_orm(user)
    
    def get_all_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        """
        Obtener todos los usuarios
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de usuarios
        """
        users = self.repository.get_all_users(skip, limit)
        return [User.from_orm(u) for u in users]
    
    def update_user(self, user_id: int, **kwargs) -> User:
        """
        Actualizar un usuario
        
        Args:
            user_id: ID del usuario
            **kwargs: Campos a actualizar
            
        Returns:
            Usuario actualizado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        updated_user = self.repository.update_user(user, **kwargs)
        return User.from_orm(updated_user)
    
    def delete_user(self, user_id: int) -> bool:
        """
        Eliminar un usuario por ID
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return self.repository.delete_user(user)
    
    def delete_user_by_username(self, username: str) -> bool:
        """
        Eliminar un usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.repository.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario '{username}' no encontrado"
            )
        
        return self.repository.delete_user(user)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Cambiar la contraseña de un usuario
        
        Args:
            user_id: ID del usuario
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            True si se cambió exitosamente
            
        Raises:
            HTTPException: Si la contraseña actual es incorrecta o el usuario no existe
        """
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña actual incorrecta"
            )
        
        if len(new_password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe tener al menos 4 caracteres"
            )
        
        hashed_new_password = hash_password(new_password)
        self.repository.update_user(user, hashed_password=hashed_new_password)
        
        return True
