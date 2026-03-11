"""
Catalogs API Router - Read-only endpoints
Regiones, Provincias, Ciudades, Industrias, Skills
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.catalog_service import CatalogService
from app.schemas.catalog import (
    RegionOut,
    ProvinceOut,
    CityOut,
    IndustryOut,
    SkillCatalogOut
)

router = APIRouter()


# ============================================
# GEOGRAPHIC CATALOGS
# ============================================

@router.get("/regions", response_model=List[RegionOut])
def get_regions(db: Session = Depends(get_db)):
    """Obtener todas las regiones del Ecuador (Costa, Sierra, Amazonía, Insular)"""
    service = CatalogService(db)
    regions = service.get_all_regions(db)
    return regions


@router.get("/regions/{region_id}/provinces", response_model=List[ProvinceOut])
def get_provinces_by_region(
    region_id: int,
    db: Session = Depends(get_db)
):
    """Obtener provincias de una región específica"""
    service = CatalogService(db)
    provinces = service.get_provinces_by_region(db, region_id)
    return provinces


@router.get("/provinces/{province_id}/cities", response_model=List[CityOut])
def get_cities_by_province(
    province_id: int,
    db: Session = Depends(get_db)
):
    """Obtener ciudades de una provincia específica"""
    service = CatalogService(db)
    cities = service.get_cities_by_province(db, province_id)
    return cities


# ============================================
# INDUSTRIES
# ============================================

@router.get("/industries", response_model=List[IndustryOut])
def get_industries(db: Session = Depends(get_db)):
    """Obtener todas las industrias activas"""
    service = CatalogService(db)
    industries = service.get_all_industries(db)
    return industries


# ============================================
# SKILLS CATALOG
# ============================================

@router.get("/skills-catalog", response_model=List[SkillCatalogOut])
def get_skills_catalog(
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    Obtener catálogo de habilidades
    
    - category (opcional): technical, soft, language, tool
    """
    service = CatalogService(db)
    
    if category:
        # Si hay categoría, filtrar
        skills = [s for s in service.get_all_skills(db) if s.category == category]
    else:
        skills = service.get_all_skills(db)
    
    return skills
