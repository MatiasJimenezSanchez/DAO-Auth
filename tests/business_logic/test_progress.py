"""
Progress Tests - COMPLETE VERSION
All fixtures include short_description for Simulation
"""
import pytest
from fastapi import status
from decimal import Decimal


@pytest.fixture
def auth_user(client):
    """Create and authenticate a user"""
    user_data = {
        "username": "progress_user",
        "email": "progress@test.com",
        "password": "Password123!",
        "full_name": "Progress User"
    }
    
    res = client.post("/api/v1/register", json=user_data)
    assert res.status_code == 201, f"User registration failed: {res.text}"
    user_id = res.json()["id"]
    
    # Login
    login_res = client.post("/api/v1/token", data={
        "username": "progress_user",
        "password": "Password123!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    
    return {
        "user_id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def test_simulation(client, db_session):
    """Create a test simulation with ALL required fields"""
    from app.models.simulations import Simulation
    from app.models.empresa import Empresa
    from app.models.catalog import ContentCategory
    
    # Create company
    company = Empresa(
        nombre_empresa="Test Co Progress",
        slug="testco-progress",
        industria="Tech",
        pais="Ecuador"
    )
    db_session.add(company)
    db_session.commit()
    
    # Create category
    category = ContentCategory(
        name="STEM Progress",
        slug="stem-progress"
    )
    db_session.add(category)
    db_session.commit()
    
    # CRITICAL FIX: Include short_description (required)
    simulation = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Test Simulation",
        slug="test-simulation-progress",
        short_description="Complete test description for progress tracking",  # FIXED
        difficulty_level="intermediate",
        state="published"
    )
    db_session.add(simulation)
    db_session.commit()
    db_session.refresh(simulation)
    
    return simulation


class TestProgressFlow:
    """Test progress workflow"""
    
    def test_start_simulation(self, client, auth_user, test_simulation):
        """Test: Start a simulation"""
        progress_data = {
            "user_id": auth_user["user_id"],
            "simulation_id": test_simulation.id
        }
        
        res = client.post(
            "/api/v1/progress/start",
            json=progress_data,
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert data["user_id"] == auth_user["user_id"]
        assert data["simulation_id"] == test_simulation.id
        assert data["status"] == "started"
        assert data["score"] == "0.00"
        assert data["completion_percentage"] == "0.00"
    
    def test_start_simulation_twice_rejected(self, client, auth_user, test_simulation):
        """Test: Cannot start same simulation twice"""
        progress_data = {
            "user_id": auth_user["user_id"],
            "simulation_id": test_simulation.id
        }
        
        # Start first time
        res1 = client.post(
            "/api/v1/progress/start",
            json=progress_data,
            headers=auth_user["headers"]
        )
        assert res1.status_code == 201, f"First start failed: {res1.text}"
        
        # Try again
        res2 = client.post(
            "/api/v1/progress/start",
            json=progress_data,
            headers=auth_user["headers"]
        )
        
        assert res2.status_code == 400
        assert "already started" in res2.json()["detail"].lower()
    
    def test_update_progress(self, client, auth_user, test_simulation):
        """Test: Update progress"""
        progress_data = {
            "user_id": auth_user["user_id"],
            "simulation_id": test_simulation.id
        }
        
        res = client.post(
            "/api/v1/progress/start",
            json=progress_data,
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 201, f"Start failed: {res.status_code} - {res.text}"
        progress_id = res.json()["id"]
        
        # Update
        update_data = {
            "status": "in_progress",
            "completion_percentage": 50.0,
            "score": 75.5
        }
        
        res = client.patch(
            f"/api/v1/progress/{progress_id}",
            json=update_data,
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 200, f"Update failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert data["status"] == "in_progress"
        assert float(data["completion_percentage"]) == 50.0
        assert float(data["score"]) == 75.5
    
    def test_complete_simulation(self, client, auth_user, test_simulation):
        """Test: Complete simulation auto-sets completion_percentage"""
        progress_data = {
            "user_id": auth_user["user_id"],
            "simulation_id": test_simulation.id
        }
        
        res = client.post(
            "/api/v1/progress/start",
            json=progress_data,
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 201, f"Start failed: {res.text}"
        progress_id = res.json()["id"]
        
        # Complete
        update_data = {
            "status": "completed",
            "score": 95.0
        }
        
        res = client.patch(
            f"/api/v1/progress/{progress_id}",
            json=update_data,
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 200, f"Complete failed: {res.text}"
        data = res.json()
        
        assert data["status"] == "completed"
        assert float(data["completion_percentage"]) == 100.0
        assert data["completed_at"] is not None
    
    def test_get_user_progress_list(self, client, auth_user, test_simulation):
        """Test: Get all progress for user"""
        progress_data = {
            "user_id": auth_user["user_id"],
            "simulation_id": test_simulation.id
        }
        
        res = client.post(
            "/api/v1/progress/start",
            json=progress_data,
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 201, f"Start failed: {res.text}"
        
        # Get progress list
        res = client.get(
            f"/api/v1/progress/user/{auth_user['user_id']}",
            headers=auth_user["headers"]
        )
        
        assert res.status_code == 200
        data = res.json()
        
        assert len(data) >= 1
        assert data[0]["simulation_id"] == test_simulation.id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
