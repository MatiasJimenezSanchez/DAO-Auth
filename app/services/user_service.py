from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
import bcrypt

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def create_user(self, user_in: UserCreate) -> User:
        # 1. Verificar duplicados
        if self.db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        if self.db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        # 2. Hashear password
        hashed_pw = self._hash_password(user_in.password)

        # 3. Preparar datos (excluir password plano)
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_pw

        # 4. Crear instancia unificada
        db_user = User(**user_data)
        
        # 5. Guardar
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
