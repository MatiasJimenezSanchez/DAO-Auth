"""
Repositorio para operaciones de usuario en base de datos
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


class UserRepository:
    """Clase para gestionar operaciones de usuario en BD"""
    
    def __init__(self, db: Session):
        """
        Inicializar el repositorio con una sesión de BD
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
    
    def get_user_by_username(self, username: str) -> User | None:
        """
        Obtener un usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Usuario encontrado o None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> User | None:
        """
        Obtener un usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario encontrado o None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Obtener un usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario encontrado o None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        """
        Obtener todos los usuarios con paginación
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de usuarios
        """
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, user_create: UserCreate) -> User:
        """
        Crear un nuevo usuario
        
        Args:
            user_create: Datos del usuario a crear
            
        Returns:
            Usuario creado
        """
        hashed_password = hash_password(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            disabled=user_create.disabled if user_create.disabled is not None else False
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user: User, **kwargs) -> User:
        """
        Actualizar un usuario
        
        Args:
            user: Usuario a actualizar
            **kwargs: Campos a actualizar
            
        Returns:
            Usuario actualizado
        """
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user: User) -> bool:
        """
        Eliminar un usuario
        
        Args:
            user: Usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        self.db.delete(user)
        self.db.commit()
        return True
    
    def user_exists(self, username: str = None, email: str = None) -> bool:
        """
        Verificar si un usuario existe por nombre de usuario o email
        
        Args:
            username: Nombre de usuario (opcional)
            email: Email (opcional)
            
        Returns:
            True si el usuario existe, False en caso contrario
        """
        if username:
            return self.db.query(User).filter(User.username == username).first() is not None
        if email:
            return self.db.query(User).filter(User.email == email).first() is not None
        return False
