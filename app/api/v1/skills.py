"""
Skills API Endpoints
CRUD operations for skills
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate, SkillOut

router = APIRouter()


@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db)
):
    """Create new skill"""
    # Check duplicate BEFORE inserting (more efficient)
    existing = db.query(Skill).filter(Skill.name == skill_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill with name '{skill_data.name}' already exists"
        )
    
    db_skill = Skill(**skill_data.model_dump())
    db.add(db_skill)
    
    try:
        db.commit()
        db.refresh(db_skill)
    except IntegrityError as e:
        db.rollback()
        # Catch race condition (duplicate inserted between check and commit)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill with name '{skill_data.name}' already exists"
        )
    
    return db_skill


@router.get("/skills", response_model=List[SkillOut])
def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all active skills"""
    query = db.query(Skill).filter(Skill.is_active == True)
    
    if category:
        query = query.filter(Skill.category == category)
    
    skills = query.offset(skip).limit(limit).all()
    return skills


@router.get("/skills/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get skill by ID"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found"
        )
    
    return skill


@router.patch("/skills/{skill_id}", response_model=SkillOut)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db)
):
    """Update skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found"
        )
    
    update_data = skill_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(skill, field, value)
    
    try:
        db.commit()
        db.refresh(skill)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed - possibly duplicate name"
        )
    
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    """Soft delete skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found"
        )
    
    skill.is_active = False
    db.commit()
    
    return None
