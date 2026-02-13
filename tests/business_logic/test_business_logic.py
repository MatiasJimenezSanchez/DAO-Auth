import pytest
from app.services.matching_service import MatchingService
from app.services.simulation_service import SimulationService
from app.services.company_service import CompanyService
from app.models.empresa import Empresa as Company
from app.models.user import User
from app.core.security import get_password_hash # Usar la función real, no contexto directo

@pytest.fixture
def test_company(db_session):
    """Empresa con campos en ESPAÑOL"""
    company = Company(
        nombre_empresa="TechCorp Test Logic",
        slug="techcorp-test-logic",
        tipo_empresa="real_nacional",
        industria="Tecnología",
        pais="Ecuador",
        ciudad="Quito",
        calificacion_promedio=4.5,
        es_partner_activo=True,
        verificado=True,
        esta_activo=True
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_user(db_session):
    """Usuario con campos en INGLÉS"""
    hashed = get_password_hash("pwd") # Usa PBKDF2 automáticamente
    
    user = User(
        username="logic_user",
        email="logic@test.com",
        hashed_password=hashed,
        full_name="Logic User",
        xp_total=500,
        level_current=5,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

class TestMatchingService:
    def test_full_matching_workflow(self, db_session, test_user, test_company):
        service = MatchingService(db_session)
        result = service.calculate_match_score(test_user.id, test_company.id)
        assert result["match_score"] > 0
        
        matches = service.find_best_matches_for_user(test_user.id)
        assert isinstance(matches, list)
        
        candidates = service.find_best_candidates_for_company(test_company.id)
        assert isinstance(candidates, list)

class TestSimulationService:
    def test_full_viability_workflow(self, db_session, test_company):
        service = SimulationService(db_session)
        viability = service.calculate_viability(test_company.id)
        assert viability["viability_score"] > 0
        
        projection = service.project_growth(test_company.id, months=12)
        assert "projected_users" in projection

class TestCompanyService:
    def test_stats(self, db_session, test_company):
        service = CompanyService(db_session)
        stats = service.get_company_stats(test_company.id)
        assert stats["total_simulaciones"] == 25
