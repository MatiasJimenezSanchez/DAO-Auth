"""
Dashboard Tests - COMPLETE VERSION
All Simulation fixtures include short_description
"""
import pytest
from fastapi import status


@pytest.fixture
def seed_company_data(client, db_session):
    """Create seed data for dashboard tests"""
    from app.models.empresa import Empresa
    from app.models.simulations import Simulation
    from app.models.catalog import ContentCategory
    from app.models.usuarios_empresa import UsuarioEmpresa
    from app.models.user_progress import UserSimulationProgress, ProgressStatus
    from app.models.user import User
    from app.services.user_service import UserService
    
    # Create company
    company = Empresa(
        nombre_empresa="Dashboard Test Co",
        slug="dashboard-test-co",
        industria="Tech",
        pais="Ecuador"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Create category
    category = ContentCategory(name="STEM", slug="stem-dash")
    db_session.add(category)
    db_session.commit()
    
    # CRITICAL FIX: Add short_description to ALL simulations
    sim1 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 1",
        slug="sim-1-dash",
        short_description="Dashboard test simulation 1",  # FIXED
        state="published"
    )
    
    sim2 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 2",
        slug="sim-2-dash",
        short_description="Dashboard test simulation 2",  # FIXED
        state="published"
    )
    
    sim3 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 3",
        slug="sim-3-dash",
        short_description="Dashboard test simulation 3 (draft)",  # FIXED
        state="draft"
    )
    
    db_session.add_all([sim1, sim2, sim3])
    db_session.commit()
    
    # Create users
    service = UserService(db_session)
    
    user1 = User(
        username="admin1_dash",
        email="admin1_dash@test.com",
        hashed_password=service.hash_password("pass"),
        full_name="Admin One"
    )
    
    user2 = User(
        username="admin2_dash",
        email="admin2_dash@test.com",
        hashed_password=service.hash_password("pass"),
        full_name="Admin Two"
    )
    
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    
    # Create company users (use empresa_id)
    company_user1 = UsuarioEmpresa(
        user_id=user1.id,
        empresa_id=company.id,
        role="admin",
        is_active=True
    )
    
    company_user2 = UsuarioEmpresa(
        user_id=user2.id,
        empresa_id=company.id,
        role="editor",
        is_active=True
    )
    
    db_session.add_all([company_user1, company_user2])
    db_session.commit()
    
    # Create students
    students = []
    for i in range(5):
        student = User(
            username=f"student{i}_dash",
            email=f"student{i}_dash@test.com",
            hashed_password=service.hash_password("pass"),
            full_name=f"Student {i}"
        )
        db_session.add(student)
        students.append(student)
    
    db_session.commit()
    
    for student in students:
        db_session.refresh(student)
    
    # Enroll students
    for student in students[:3]:
        progress = UserSimulationProgress(
            user_id=student.id,
            simulation_id=sim1.id,
            status=ProgressStatus.IN_PROGRESS
        )
        db_session.add(progress)
    
    for student in students[3:5]:
        progress = UserSimulationProgress(
            user_id=student.id,
            simulation_id=sim2.id,
            status=ProgressStatus.STARTED
        )
        db_session.add(progress)
    
    db_session.commit()
    
    return {
        "company_id": company.id,
        "expected_simulations": 2,
        "expected_company_users": 2,
        "expected_enrolled_users": 5
    }


class TestDashboardStats:
    """Test dashboard statistics accuracy"""
    
    def test_real_stats_accurate(self, client, seed_company_data):
        """Test: Dashboard shows accurate real-time stats"""
        company_id = seed_company_data["company_id"]
        
        res = client.get(f"/api/v1/empresas/{company_id}/stats")
        
        assert res.status_code == 200, f"Stats failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert data["total_simulaciones"] == seed_company_data["expected_simulations"]
        assert data["total_company_users"] == seed_company_data["expected_company_users"]
        assert data["total_usuarios_inscritos"] == seed_company_data["expected_enrolled_users"]
    
    def test_stats_exclude_inactive(self, client, seed_company_data, db_session):
        """Test: Stats exclude inactive company users"""
        from app.models.usuarios_empresa import UsuarioEmpresa
        
        company_id = seed_company_data["company_id"]
        
        company_user = db_session.query(UsuarioEmpresa).filter(
            UsuarioEmpresa.empresa_id == company_id
        ).first()
        
        company_user.is_active = False
        db_session.commit()
        
        res = client.get(f"/api/v1/empresas/{company_id}/stats")
        assert res.status_code == 200
        data = res.json()
        
        assert data["total_company_users"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
