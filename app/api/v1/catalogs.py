"""
Catalogs API Endpoints
Complete CRUD for all catalog tables
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.catalog import (
    Region, Province, City, 
    Industry, ContentCategory, SkillCatalog
)
from app.schemas.catalog import (
    RegionOut, ProvinceOut, CityOut,
    IndustryOut, ContentCategoryOut, SkillCatalogOut,
    RegionCreate, ProvinceCreate, CityCreate,
    IndustryCreate, ContentCategoryCreate, SkillCatalogCreate
)

router = APIRouter()


# ============================================
# REGIONS ENDPOINTS
# ============================================

@router.get("/regions", response_model=List[RegionOut])
def get_regions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all regions"""
    regions = db.query(Region).filter(Region.is_active == True).offset(skip).limit(limit).all()
    return regions


@router.post("/regions", response_model=RegionOut)
def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    """Create new region"""
    db_region = Region(**region.dict())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region


@router.get("/regions/{region_id}", response_model=RegionOut)
def get_region(region_id: int, db: Session = Depends(get_db)):
    """Get region by ID"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


# ============================================
# PROVINCES ENDPOINTS
# ============================================

@router.get("/provinces", response_model=List[ProvinceOut])
def get_provinces(
    region_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all provinces, optionally filtered by region"""
    query = db.query(Province).filter(Province.is_active == True)
    
    if region_id:
        query = query.filter(Province.region_id == region_id)
    
    provinces = query.offset(skip).limit(limit).all()
    return provinces


@router.post("/provinces", response_model=ProvinceOut)
def create_province(province: ProvinceCreate, db: Session = Depends(get_db)):
    """Create new province"""
    db_province = Province(**province.dict())
    db.add(db_province)
    db.commit()
    db.refresh(db_province)
    return db_province


@router.get("/provinces/{province_id}", response_model=ProvinceOut)
def get_province(province_id: int, db: Session = Depends(get_db)):
    """Get province by ID"""
    province = db.query(Province).filter(Province.id == province_id).first()
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    return province


# ============================================
# CITIES ENDPOINTS
# ============================================

@router.get("/cities", response_model=List[CityOut])
def get_cities(
    province_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all cities, optionally filtered by province"""
    query = db.query(City).filter(City.is_active == True)
    
    if province_id:
        query = query.filter(City.province_id == province_id)
    
    cities = query.offset(skip).limit(limit).all()
    return cities


@router.post("/cities", response_model=CityOut)
def create_city(city: CityCreate, db: Session = Depends(get_db)):
    """Create new city"""
    db_city = City(**city.dict())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


@router.get("/cities/{city_id}", response_model=CityOut)
def get_city(city_id: int, db: Session = Depends(get_db)):
    """Get city by ID"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


# ============================================
# INDUSTRIES ENDPOINTS
# ============================================

@router.get("/industries", response_model=List[IndustryOut])
def get_industries(
    parent_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all industries, optionally filtered by parent"""
    query = db.query(Industry).filter(Industry.is_active == True)
    
    if parent_id is not None:
        query = query.filter(Industry.parent_industry_id == parent_id)
    
    industries = query.order_by(Industry.order).offset(skip).limit(limit).all()
    return industries


@router.post("/industries", response_model=IndustryOut)
def create_industry(industry: IndustryCreate, db: Session = Depends(get_db)):
    """Create new industry"""
    db_industry = Industry(**industry.dict())
    db.add(db_industry)
    db.commit()
    db.refresh(db_industry)
    return db_industry


@router.get("/industries/{industry_id}", response_model=IndustryOut)
def get_industry(industry_id: int, db: Session = Depends(get_db)):
    """Get industry by ID"""
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    return industry


# ============================================
# CONTENT CATEGORIES ENDPOINTS
# ============================================

@router.get("/categories", response_model=List[ContentCategoryOut])
def get_categories(
    parent_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all content categories, optionally filtered by parent"""
    query = db.query(ContentCategory).filter(ContentCategory.is_active == True)
    
    if parent_id is not None:
        query = query.filter(ContentCategory.parent_category_id == parent_id)
    
    categories = query.order_by(ContentCategory.order).offset(skip).limit(limit).all()
    return categories


@router.post("/categories", response_model=ContentCategoryOut)
def create_category(category: ContentCategoryCreate, db: Session = Depends(get_db)):
    """Create new content category"""
    db_category = ContentCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/{category_id}", response_model=ContentCategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get content category by ID"""
    category = db.query(ContentCategory).filter(ContentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Content category not found")
    return category


# ============================================
# SKILLS CATALOG ENDPOINTS
# ============================================

@router.get("/skills", response_model=List[SkillCatalogOut])
def get_skills(
    category: str = None,
    parent_id: int = None,
    market_demand: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all skills, with multiple filters"""
    query = db.query(SkillCatalog).filter(SkillCatalog.is_active == True)
    
    if category:
        query = query.filter(SkillCatalog.category == category)
    
    if parent_id is not None:
        query = query.filter(SkillCatalog.parent_skill_id == parent_id)
    
    if market_demand:
        query = query.filter(SkillCatalog.market_demand == market_demand)
    
    skills = query.offset(skip).limit(limit).all()
    return skills


@router.post("/skills", response_model=SkillCatalogOut)
def create_skill(skill: SkillCatalogCreate, db: Session = Depends(get_db)):
    """Create new skill"""
    db_skill = SkillCatalog(**skill.dict())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@router.get("/skills/{skill_id}", response_model=SkillCatalogOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get skill by ID"""
    skill = db.query(SkillCatalog).filter(SkillCatalog.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill
