"""
Simulations Tests - v2.0 Compatible con Global Seeder
"""
import pytest
import uuid


class TestSimulations:
    """
    Tests de simulaciones que usan los datos del Global Seeder.
    company_id=1 y category_id=1 siempre existen gracias a seed_base_data.
    """
    
    def test_create_simple_simulation(self, client):
        """Test: Create simple simulation usando datos del seeder"""
        sim_data = {
            "title": f"Simple Sim {uuid.uuid4().hex[:6]}",
            "slug": f"simple-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "A simple test simulation",
            "company_id": 1,  # Del Global Seeder
            "category_id": 1,  # Del Global Seeder
            "state": "draft"
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code == 201, f"Failed: {res.text}"

    def test_create_nested_simulation(self, client):
        """Test: Create simulation con state published"""
        sim_data = {
            "title": f"Nested Sim {uuid.uuid4().hex[:6]}",
            "slug": f"nested-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "Simulation with nested content",
            "company_id": 1,
            "category_id": 1,
            "state": "published"
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code == 201, f"Failed: {res.text}"

    def test_get_simulation(self, client):
        """Test: Get simulation by ID"""
        # Crear primero
        sim_data = {
            "title": f"Get Test Sim {uuid.uuid4().hex[:6]}",
            "slug": f"get-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "Test get endpoint",
            "company_id": 1,
            "category_id": 1,
            "state": "published"
        }
        create_res = client.post("/api/v1/simulaciones", json=sim_data)
        assert create_res.status_code == 201
        
        sim_id = create_res.json()["id"]
        get_res = client.get(f"/api/v1/simulaciones/{sim_id}")
        assert get_res.status_code == 200
        assert get_res.json()["title"] == sim_data["title"]
