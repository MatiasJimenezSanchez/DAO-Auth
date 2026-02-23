"""
Dashboard Tests
Business logic tests for company dashboard statistics
"""
import pytest
from fastapi import status


@pytest.fixture
def seed_company_data(client, db_session):
    """Create seed data for dashboard tests"""
    from app.models.empresa import Empresa
    from app.models.simulations import Simulation
    from app.models.catalog import ContentCategory
    from app.models.usuarios_empresa import CompanyUser
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
        slug="sim-1",
        short_description="Test",
        state="published"
    )
    
    sim2 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 2",
        slug="sim-2",
        short_description="Test",
        state="published"
    )
    
    sim3 = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Sim 3",
        slug="sim-3",
        short_description="Test",
        state="draft"  # Not counted
    )
    
    db_session.add_all([sim1, sim2, sim3])
    db_session.commit()
    
    # Create 2 company users (admins)
    service = UserService(db_session)
    
    user1 = User(
        username="admin1",
        email="admin1@test.com",
        hashed_password=service.hash_password("pass"),
        full_name="Admin One"
    )
    
    user2 = User(
        username="admin2",
        email="admin2@test.com",
        hashed_password=service.hash_password("pass"),
        full_name="Admin Two"
    )
    
    db_session.add_all([user1, user2])
    db_session.commit()
    
    company_user1 = CompanyUser(
        company_id=company.id,
        email="admin1@test.com",
        password_hash=service.hash_password("pass"),
        full_name="Admin One",
        role="admin",
        is_active=True
    )
    
    company_user2 = CompanyUser(
        company_id=company.id,
        email="admin2@test.com",
        password_hash=service.hash_password("pass"),
        full_name="Admin Two",
        role="editor",
        is_active=True
    )
    
    db_session.add_all([company_user1, company_user2])
    db_session.commit()
    
    # Create 5 students who enrolled
    students = []
    for i in range(5):
        student = User(
            username=f"student{i}",
            email=f"student{i}@test.com",
            hashed_password=service.hash_password("pass"),
            full_name=f"Student {i}"
        )
        db_session.add(student)
        students.append(student)
    
    db_session.commit()
    
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
        assert res.status_code == 200
        
        data = res.json()
        
        # Verify counts match seeded data
        assert data["total_simulaciones"] == seed_company_data["expected_simulations"]
        assert data["total_company_users"] == seed_company_data["expected_company_users"]
        assert data["total_usuarios_inscritos"] == seed_company_data["expected_enrolled_users"]
    
    def test_stats_exclude_inactive(self, client, seed_company_data, db_session):
        """Test: Stats exclude inactive company users"""
        from app.models.usuarios_empresa import CompanyUser
        
        company_id = seed_company_data["company_id"]
        
        # Deactivate one company user
        company_user = db_session.query(CompanyUser).filter(
            CompanyUser.company_id == company_id
        ).first()
        
        company_user.is_active = False
        db_session.commit()
        
        # Get stats
        res = client.get(f"/api/v1/empresas/{company_id}/stats")
        data = res.json()
        
        # Should now show 1 instead of 2
        assert data["total_company_users"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
