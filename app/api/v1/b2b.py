"""
app/api/v1/b2b.py — Endpoints del Portal B2B para Empresas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.usuarios_empresa import CompanyUser
from app.schemas.b2b import B2BDashboardOut
from app.services.b2b_service import B2BService

router = APIRouter()

def verify_company_access(user_id: int, company_id: int, db: Session):
    """Middleware lógico para verificar que el usuario pertenece a la empresa."""
    membership = db.query(CompanyUser).filter(
        CompanyUser.user_id == user_id,
        CompanyUser.empresa_id == company_id,
        CompanyUser.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a los datos de esta empresa"
        )
    return membership

@router.get("/companies/{company_id}/dashboard", response_model=B2BDashboardOut)
def get_company_dashboard(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene las métricas consolidadas de la empresa (Dashboard).
    Requiere que el usuario autenticado sea parte de 'usuarios_empresa'.
    """
    # 1. Verificar acceso B2B
    verify_company_access(current_user.id, company_id, db)
    
    # 2. Generar analíticas
    service = B2BService(db)
    return service.get_company_dashboard(company_id)
