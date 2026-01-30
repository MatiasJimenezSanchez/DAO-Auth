from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.catalog import Region, Province, City
from app.schemas.catalog import RegionOut, ProvinceOut, CityOut

router = APIRouter(prefix="/catalogs", tags=["catalogs"])

@router.get("/regions", response_model=List[RegionOut])
def list_regions(db: Session = Depends(get_db)):
    return db.query(Region).filter(Region.is_active == True).order_by(Region.name).all()

@router.get("/provinces", response_model=List[ProvinceOut])
def list_provinces(region_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Province).filter(Province.is_active == True)
    if region_id:
        q = q.filter(Province.region_id == region_id)
    return q.order_by(Province.name).all()

@router.get("/cities", response_model=List[CityOut])
def list_cities(province_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(City).filter(City.is_active == True)
    if province_id:
        q = q.filter(City.province_id == province_id)
    return q.order_by(City.name).all()