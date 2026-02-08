import pytest
from app.services.matching_service import MatchingService
from app.services.simulation_service import SimulationService
from app.services.company_service import CompanyService
from app.models.empresa import Empresa as Company
from app.models.user import User
from app.core.security import get_password_hash

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
        total_simulaciones=25,
        total_usuarios_inscritos=150,
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
    user = User(
        username="logic_user",
        email="logic@test.com",
        hashed_password=get_password_hash("pwd"),
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
        # 1. Match simple
        result = service.calculate_match_score(test_user.id, test_company.id)
        assert result["match_score"] > 0
        assert "breakdown" in result
        
        # 2. Búsqueda de mejores matches
        matches = service.find_best_matches_for_user(test_user.id)
        assert isinstance(matches, list)
        
        # 3. Búsqueda de candidatos
        candidates = service.find_best_candidates_for_company(test_company.id)
        assert isinstance(candidates, list)

class TestSimulationService:
    def test_full_viability_workflow(self, db_session, test_company):
        service = SimulationService(db_session)
        
        # 1. Viabilidad
        viability = service.calculate_viability(test_company.id)
        assert viability["viability_score"] > 0
        assert "factors" in viability
        assert "classification" in viability
        
        # 2. Proyección
        projection = service.project_growth(test_company.id, months=12)
        assert projection["projected_users"] > projection["current_users"]

class TestCompanyService:
    def test_stats(self, db_session, test_company):
        service = CompanyService(db_session)
        stats = service.get_company_stats(test_company.id)
        assert stats["total_simulations"] == 25
