"""
User Service
Business logic layer for User operations
Completely decoupled from FastAPI endpoints
"""
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    Service layer for User business logic
    
    Responsibilities:
    - Password hashing
    - Duplicate validation
    - XP/Level initialization
    - User registration workflow
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with repository injection
        
        Args:
            db: Database session
        """
        self.repository = UserRepository(db)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Stored hash
            
        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def validate_new_user(self, user_data: UserCreate) -> None:
        """
        Validate user data before creation
        Raises HTTPException if validation fails
        
        Args:
            user_data: User creation data
            
        Raises:
            HTTPException: If email or username already exists
        """
        # Check email
        if self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check username
        if self.repository.username_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Register new user (complete workflow)
        
        Business logic:
        1. Validate duplicates
        2. Hash password
        3. Initialize gamification (XP=0, Level=1)
        4. Create user in DB
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user instance
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate
        self.validate_new_user(user_data)
        
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Prepare user data
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['hashed_password'] = hashed_password
        
        # Initialize gamification (already have defaults in model, but explicit is better)
        if 'xp_total' not in user_dict:
            user_dict['xp_total'] = 0
        if 'level_current' not in user_dict:
            user_dict['level_current'] = 1
        
        # Create user object for repository
        from app.schemas.user import UserCreate as UserCreateRepo
        
        # Repository expects UserCreate schema, but we need to pass hashed_password
        # Create a modified version
        class UserCreateWithHash(UserCreate):
            hashed_password: str
        
        user_create = UserCreateWithHash(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            gender=user_data.gender,
            birth_date=user_data.birth_date,
            city_id=user_data.city_id
        )
        
        # Actually, better approach: create User model directly
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            gender=user_data.gender,
            birth_date=user_data.birth_date,
            city_id=user_data.city_id,
            xp_total=0,
            level_current=1,
            is_active=True
        )
        
        # Use repository to save
        self.repository.db.add(db_user)
        self.repository.db.commit()
        self.repository.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User instance or None
        """
        return self.repository.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User instance or None
        """
        return self.repository.get_by_email(email)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        return self.repository.get_by_username(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username/password
        
        Args:
            username: Username or email
            password: Plain password
            
        Returns:
            User if authenticated, None otherwise
        """
        # Try username first
        user = self.get_user_by_username(username)
        
        # If not found, try email
        if not user:
            user = self.get_user_by_email(username)
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update user data
        
        Args:
            user_id: User ID
            user_data: Update data
            
        Returns:
            Updated user or None
        """
        return self.repository.update(user_id, user_data)
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Deactivate user (soft delete)
        
        Args:
            user_id: User ID
            
        Returns:
            Deactivated user or None
        """
        return self.repository.soft_delete(user_id)
    
    def get_active_users(self, skip: int = 0, limit: int = 100):
        """
        Get active users (paginated)
        
        Args:
            skip: Pagination offset
            limit: Max records
            
        Returns:
            List of active users
        """
        return self.repository.get_active_users(skip, limit)
    
    def award_xp(self, user_id: int, xp_amount: int) -> Optional[User]:
        """
        Award XP to user and calculate level
        
        Business logic for leveling:
        - Level 1: 0-99 XP
        - Level 2: 100-299 XP
        - Level 3: 300-599 XP
        - Level N: exponential growth
        
        Args:
            user_id: User ID
            xp_amount: XP to award
            
        Returns:
            Updated user or None
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Add XP
        user.xp_total += xp_amount
        
        # Calculate level (simple formula: level = sqrt(xp / 100))
        import math
        new_level = max(1, int(math.sqrt(user.xp_total / 100)) + 1)
        user.level_current = new_level
        
        self.repository.db.commit()
        self.repository.db.refresh(user)
        
        return user
