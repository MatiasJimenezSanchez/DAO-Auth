"""
Users Endpoints
Refactored to use UserService (Service Layer)
NO direct database queries
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.services.user_service import UserService
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all active users (paginated)
    
    Args:
        skip: Records to skip
        limit: Max records
        db: Database session
        
    Returns:
        List of users
    """
    service = UserService(db)
    users = service.get_active_users(skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update user data
    
    Args:
        user_id: User ID
        user_data: Update data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Authorization: users can only update themselves
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    service = UserService(db)
    user = service.update_user(user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Deactivate user (soft delete)
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    # Authorization: users can only deactivate themselves
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deactivate your own account"
        )
    
    service = UserService(db)
    user = service.deactivate_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return None


@router.post("/users/{user_id}/award-xp", response_model=UserOut)
def award_user_xp(
    user_id: int,
    xp_amount: int,
    db: Session = Depends(get_db)
):
    """
    Award XP to user
    
    Business logic handled by UserService
    
    Args:
        user_id: User ID
        xp_amount: XP to award
        db: Database session
        
    Returns:
        Updated user with new XP and level
        
    Raises:
        HTTPException: If user not found
    """
    service = UserService(db)
    user = service.award_xp(user_id, xp_amount)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user
