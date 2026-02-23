"""
Dashboard Tests - FIXED VERSION
Business logic tests for company dashboard statistics
CRITICAL FIX: empresa_id (not company_id) in UsuarioEmpresa
"""
import pytest
from fastapi import status


@pytest.fixture
def seed_company_data(client, db_session):
    """Create seed data for dashboard tests"""
    from app.models.empresa import Empresa
    from app.models.simulations import Simulation
    from app.models.catalog import ContentCategory
    from app.models.usuarios_empresa import UsuarioEmpresa  # Spanish model name
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
    category = ContentCategory(name="STEM", slug="stem")
    db_session.add(category)
    db_session.commit()
    
    # Create 3 simulations (2 published, 1 draft)
    sim1 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 1",
        slug="sim-1-dash",
        short_description="Test",
        state="published"
    )
    
    sim2 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 2",
        slug="sim-2-dash",
        short_description="Test",
        state="published"
    )
    
    sim3 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 3",
        slug="sim-3-dash",
        short_description="Test",
        state="draft"  # Not counted
    )
    
    db_session.add_all([sim1, sim2, sim3])
    db_session.commit()
    
    # Create 2 regular users first (for User table)
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
    
    # CRITICAL FIX: Use empresa_id (Spanish) not company_id
    company_user1 = UsuarioEmpresa(
        user_id=user1.id,
        empresa_id=company.id,  # FIXED: was company_id
        role="admin",
        is_active=True
    )
    
    company_user2 = UsuarioEmpresa(
        user_id=user2.id,
        empresa_id=company.id,  # FIXED: was company_id
        role="editor",
        is_active=True
    )
    
    db_session.add_all([company_user1, company_user2])
    db_session.commit()
    
    # Create 5 students who enrolled
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
    
    # Refresh to get IDs
    for student in students:
        db_session.refresh(student)
    
    # Enroll students in simulations
    # Student 0,1,2 -> Sim 1
    # Student 3,4 -> Sim 2
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
        "expected_simulations": 2,  # Only published
        "expected_company_users": 2,
        "expected_enrolled_users": 5  # Unique students
    }


class TestDashboardStats:
    """Test dashboard statistics accuracy"""
    
    def test_real_stats_accurate(self, client, seed_company_data):
        """Test: Dashboard shows accurate real-time stats"""
        company_id = seed_company_data["company_id"]
        
        # Get stats
        res = client.get(f"/api/v1/empresas/{company_id}/stats")
        
        # DEBUG: Print if not 200
        if res.status_code != 200:
            print(f"ERROR: Stats endpoint returned {res.status_code}")
            print(f"Response: {res.text}")
        
        assert res.status_code == 200, f"Stats failed: {res.status_code} - {res.text}"
        
        data = res.json()
        
        # Verify counts match seeded data
        assert data["total_simulaciones"] == seed_company_data["expected_simulations"], \
            f"Expected {seed_company_data['expected_simulations']} simulations, got {data['total_simulaciones']}"
        
        assert data["total_company_users"] == seed_company_data["expected_company_users"], \
            f"Expected {seed_company_data['expected_company_users']} company users, got {data['total_company_users']}"
        
        assert data["total_usuarios_inscritos"] == seed_company_data["expected_enrolled_users"], \
            f"Expected {seed_company_data['expected_enrolled_users']} enrolled users, got {data['total_usuarios_inscritos']}"
    
    def test_stats_exclude_inactive(self, client, seed_company_data, db_session):
        """Test: Stats exclude inactive company users"""
        from app.models.usuarios_empresa import UsuarioEmpresa
        
        company_id = seed_company_data["company_id"]
        
        # Deactivate one company user
        company_user = db_session.query(UsuarioEmpresa).filter(
            UsuarioEmpresa.empresa_id == company_id
        ).first()
        
        company_user.is_active = False
        db_session.commit()
        
        # Get stats
        res = client.get(f"/api/v1/empresas/{company_id}/stats")
        assert res.status_code == 200
        data = res.json()
        
        # Should now show 1 instead of 2
        assert data["total_company_users"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
