from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.university import University, Career
from app.schemas.university import UniversityOut, CareerOut, UniversityWithCareers

router = APIRouter(prefix='/universities', tags=['universities'])

@router.get('/', response_model=List[UniversityOut])
def list_universities(
    city_id: Optional[int] = None,
    university_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(University).filter(University.is_active == True)
    
    if city_id:
        query = query.filter(University.city_id == city_id)
    if university_type:
        query = query.filter(University.university_type == university_type)
    
    return query.offset(skip).limit(limit).all()

@router.get('/{university_id}', response_model=UniversityWithCareers)
def get_university(university_id: int, db: Session = Depends(get_db)):
    university = db.query(University).filter(University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail='Universidad no encontrada')
    return university

@router.get('/{university_id}/careers', response_model=List[CareerOut])
def list_careers_by_university(
    university_id: int,
    db: Session = Depends(get_db)
):
    careers = db.query(Career).filter(
        Career.university_id == university_id,
        Career.is_active == True
    ).all()
    return careers
