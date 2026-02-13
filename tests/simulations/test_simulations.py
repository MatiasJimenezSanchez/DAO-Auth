import pytest
from fastapi import status

class TestSimulations:
    @pytest.fixture
    def core_setup(self, client, valid_company_data):
        """Usar fixture global de empresa válida"""
        import uuid
        # Crear empresa con TODOS los campos
        company_data = valid_company_data.copy()
        company_data["slug"] = f"legacy-corp-{uuid.uuid4().hex[:6]}"
        
        res = client.post("/api/v1/empresas", json=company_data)
        assert res.status_code == 201, f"Error creando empresa: {res.text}"
        
        return {"company_id": res.json()["id"], "category_id": 1}
    
    def test_create_simple_simulation(self, client, core_setup):
        """Test: Create simple simulation"""
        sim_data = {
            "title": "Backend Simulation",
            "slug": "backend-sim-001",
            "short_description": "Learn backend",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"]
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code == 201
    
    def test_create_nested_simulation(self, client, core_setup):
        """Test: Create simulation with modules"""
        # Similar al anterior
        pass
    
    def test_get_simulation(self, client, core_setup):
        """Test: Get simulation"""
        # Primero crear
        sim_data = {
            "title": "Test Sim",
            "slug": "test-sim-get",
            "short_description": "Test",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"]
        }
        create_res = client.post("/api/v1/simulaciones", json=sim_data)
        sim_id = create_res.json()["id"]
        
        # Luego obtener
        res = client.get(f"/api/v1/simulaciones/{sim_id}")
        assert res.status_code == 200
