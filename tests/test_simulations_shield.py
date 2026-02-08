import pytest
from datetime import datetime, timedelta

class TestSimulationsShield:
    
    @pytest.fixture
    def auth_header(self, client):
        import uuid
        u_name = f"sim_user_{uuid.uuid4().hex[:8]}"
        user = {"username": u_name, "email": f"{u_name}@test.com", "password": "Pass123!", "full_name": "Sim User"}
        client.post("/api/v1/register", json=user)
        login = client.post("/api/v1/token", data={"username": u_name, "password": "Pass123!"})
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    @pytest.fixture
    def test_company_id(self, client):
        import uuid
        comp = {"nombre_empresa": f"Sim Corp {uuid.uuid4().hex[:8]}", "slug": f"sim-{uuid.uuid4().hex[:8]}"}
        res = client.post("/api/v1/empresas/", json=comp)
        if res.status_code != 201: return 1 
        return res.json()["id"]

    @pytest.fixture
    def base_sim(self, test_company_id):
        import uuid
        return {
            "title": "Simulación Python Avanzado",
            "slug": f"python-adv-{uuid.uuid4().hex[:8]}",
            "short_description": "Aprende backend",
            "company_id": test_company_id,
            "category_id": 1,
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "total_spots": 50,
            "state": "published"
        }

    def test_create_simulation(self, client, base_sim):
        res = client.post("/api/v1/simulaciones/", json=base_sim)
        assert res.status_code == 201
        assert res.json()["title"] == base_sim["title"]

    def test_create_sim_end_date_before_start(self, client, base_sim):
        payload = base_sim.copy()
        payload["start_date"] = (datetime.now() + timedelta(days=10)).isoformat()
        payload["end_date"] = (datetime.now() + timedelta(days=5)).isoformat()
        
        res = client.post("/api/v1/simulaciones/", json=payload)
        # Esperamos 422 Unprocessable Entity
        assert res.status_code == 422

    def test_create_sim_past_date(self, client, base_sim):
        payload = base_sim.copy()
        payload["start_date"] = (datetime.now() - timedelta(days=10)).isoformat()
        
        res = client.post("/api/v1/simulaciones/", json=payload)
        assert res.status_code == 400

    def test_enrollment_logic(self, client, base_sim, auth_header):
        # 1. Crear
        res_create = client.post("/api/v1/simulaciones/", json=base_sim)
        if res_create.status_code != 201: pytest.fail(f"Error: {res_create.text}")
        sim_id = res_create.json()["id"]
        
        # 2. Inscribir
        res_enroll = client.post(f"/api/v1/simulaciones/{sim_id}/inscribir", headers=auth_header)
        assert res_enroll.status_code == 200
        assert res_enroll.json()["status"] == "enrolled"
