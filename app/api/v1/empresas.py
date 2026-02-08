from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut
from app.services.company_service import CompanyService

router = APIRouter()

# Doble decorador para soportar /api/v1/empresas y /api/v1/empresas/
@router.post("", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_company(
    company_data: EmpresaCreate,
    db: Session = Depends(get_db)
):
    service = CompanyService(db)
    return service.create_company(company_data)

@router.get("", response_model=List[EmpresaOut])
@router.get("/", response_model=List[EmpresaOut], include_in_schema=False)
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    industry: Optional[str] = None,
    partners_only: bool = False,
    db: Session = Depends(get_db)
):
    service = CompanyService(db)
    return service.list_companies(skip, limit, industry, partners_only)

@router.get("/search", response_model=List[EmpresaOut])
def search_companies(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    service = CompanyService(db)
    return service.search_companies(q, limit)

@router.get("/top", response_model=List[EmpresaOut])
def get_top_companies(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    service = CompanyService(db)
    return service.get_top_companies(limit)

@router.get("/slug/{slug}", response_model=EmpresaOut)
def get_company_by_slug(slug: str, db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.get_company_by_slug(slug)

@router.get("/{company_id}", response_model=EmpresaOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.get_company(company_id)

@router.put("/{company_id}", response_model=EmpresaOut)
def update_company(
    company_id: int,
    company_data: EmpresaUpdate,
    db: Session = Depends(get_db)
):
    service = CompanyService(db)
    return service.update_company(company_id, company_data)

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    service = CompanyService(db)
    service.delete_company(company_id)
    return None

@router.get("/{company_id}/stats")
def get_company_stats(company_id: int, db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.get_company_stats(company_id)
