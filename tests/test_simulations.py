"""
Tests for Simulations Core
"""
import pytest
from fastapi import status

@pytest.fixture
def core_setup(client):
    """Create dependencies: Company + Category"""
    # 1. Company (Unique slug per run to avoid collisions)
    import uuid
    unique_slug = f"sim-corp-{uuid.uuid4().hex[:6]}"
    
    emp_data = {
        "nombre_empresa": f"Sim Corp {unique_slug}", 
        "slug": unique_slug, 
        "tipo_empresa": "real_nacional"
    }
    emp_res = client.post("/api/v1/empresas", json=emp_data)
    
    if emp_res.status_code == 201:
        emp_id = emp_res.json()["id"]
    else:
        # Fallback: Find existing
        existing = client.get("/api/v1/empresas").json()
        if existing:
            emp_id = existing[0]["id"]
        else:
            pytest.fail("Could not create or find company for test")
        
    # 2. Category
    cat_data = {"name": "Finance", "slug": "finance"}
    cat_res = client.post("/api/v1/categories", json=cat_data)
    if cat_res.status_code == 201 or cat_res.status_code == 200:
        cat_id = cat_res.json()["id"]
    else:
        # Fallback if category slug exists
        # In a real scenario we might search, but catalogs usually persist
        # Assuming ID 1 exists from previous tests or seeds
        cat_id = 1 
        
    return {"company_id": emp_id, "category_id": cat_id}

class TestSimulations:
    
    def test_create_simple_simulation(self, client, core_setup):
        import uuid
        slug = f"intro-banking-{uuid.uuid4().hex[:6]}"
        
        sim_data = {
            "title": "Intro to Banking",
            "slug": slug,
            "short_description": "Learn basics",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"]
        }
        
        response = client.post("/api/v1/simulations", json=sim_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["title"] == "Intro to Banking"

    def test_create_nested_simulation(self, client, core_setup):
        """Test creating Simulation -> Module -> Task in one go"""
        import uuid
        slug = f"adv-audit-{uuid.uuid4().hex[:6]}"
        
        nested_data = {
            "title": "Advanced Audit",
            "slug": slug,
            "short_description": "Full course",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"],
            "modules": [
                {
                    "title": "Module 1: Planning",
                    "order": 1,
                    "tasks": [
                        {
                            "title": "Task 1: Email Client",
                            "order": 1,
                            "task_type": "submission",
                            "resources": [
                                {"name": "Template.docx", "url": "http://file.com"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        response = client.post("/api/v1/simulations", json=nested_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert len(data["modules"]) == 1
        assert data["modules"][0]["title"] == "Module 1: Planning"
        assert len(data["modules"][0]["tasks"]) == 1
        assert data["modules"][0]["tasks"][0]["resources"][0]["name"] == "Template.docx"

    def test_get_simulation(self, client, core_setup):
        # 1. Create it first (AAA pattern: Arrange, Act, Assert)
        import uuid
        slug = f"get-test-{uuid.uuid4().hex[:6]}"
        
        sim_data = {
            "title": "Get Test Sim",
            "slug": slug,
            "short_description": "Testing GET",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"]
        }
        create_res = client.post("/api/v1/simulations", json=sim_data)
        assert create_res.status_code == status.HTTP_201_CREATED
        
        # 2. Now try to get it
        response = client.get(f"/api/v1/simulations/{slug}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["slug"] == slug
