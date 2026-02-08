from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.company_repository import CompanyRepository
from app.services.catalog_service import CatalogService
from app.models.empresa import Empresa as Company
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate


class CompanyService:
    """Servicio de lógica de negocio para empresas"""
    
    def __init__(self, db: Session):
        self.repo = CompanyRepository(db)
        self.catalog_service = CatalogService(db)
        self.db = db
    
    def create_company(self, company_data: EmpresaCreate) -> Company:
        # 1. Validar nombre único
        existing = self.repo.get_by_name(company_data.nombre_empresa)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una empresa con el nombre {company_data.nombre_empresa}"
            )
        
        # 2. Validar slug único
        existing_slug = self.repo.get_by_slug(company_data.slug)
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El slug {company_data.slug} ya está en uso"
            )
        
        # 3. Crear empresa
        return self.repo.create(company_data)
    
    def get_company(self, company_id: int) -> Company:
        company = self.repo.get(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa con ID {company_id} no encontrada"
            )
        return company
    
    def get_company_by_slug(self, slug: str) -> Company:
        company = self.repo.get_by_slug(slug)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa con slug {slug} no encontrada"
            )
        return company
    
    def list_companies(self, skip: int = 0, limit: int = 100,
                      industry: Optional[str] = None,
                      partners_only: bool = False) -> List[Company]:
        if partners_only:
            return self.repo.get_partners(skip, limit)
        if industry:
            return self.repo.get_by_industry(industry, skip, limit)
        return self.repo.get_multi(skip, limit, filters={"esta_activo": True})
    
    def update_company(self, company_id: int, company_data: EmpresaUpdate) -> Company:
        company = self.get_company(company_id)
        return self.repo.update(company_id, company_data)
    
    def delete_company(self, company_id: int) -> None:
        company = self.get_company(company_id)
        company.esta_activo = False
        self.db.commit()
    
    def search_companies(self, query: str, limit: int = 10) -> List[Company]:
        return self.repo.search_by_name(query, limit)
    
    def get_top_companies(self, limit: int = 10) -> List[Company]:
        return self.repo.get_top_rated(limit)
    
    def get_company_stats(self, company_id: int) -> Dict:
        """Obtener estadísticas completas de una empresa"""
        company = self.get_company(company_id)
        return {
            "company_id": company.id,
            "name": company.nombre_empresa,
            "total_simulations": company.total_simulaciones,
            "avg_rating": float(company.calificacion_promedio) if company.calificacion_promedio else 0.0,
            "is_partner": company.es_partner_activo,
            "is_verified": company.verificado,
            "active_users": company.total_usuarios_inscritos
        }
