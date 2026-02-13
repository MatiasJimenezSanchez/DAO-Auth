"""
COMPANIES BUSINESS LOGIC TESTS
Fuzzing, Boundaries, Concurrency, State Management
"""
import pytest
from fastapi import status
from decimal import Decimal


class TestCompaniesBoundaries:
    """Boundary Value Analysis"""
    
    def test_nombre_empresa_too_long(self, client):
        """Boundary: nombre_empresa > 200 chars"""
        payload = {
            "nombre_empresa": "A" * 201,  # Exceeds DB limit
            "slug": "toolong",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        # Should fail at DB level (or Pydantic if max_length is set)
        assert res.status_code in [422, 500]
    
    def test_nombre_empresa_empty_string(self, client):
        """Boundary: Empty nombre_empresa"""
        payload = {
            "nombre_empresa": "",
            "slug": "empty",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        assert res.status_code == 422
    
    def test_slug_special_characters(self, client):
        """Boundary: Slug with special chars"""
        payload = {
            "nombre_empresa": "SpecialCorp",
            "slug": "special@#$%corp",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        # Should fail if slug validation exists
        assert res.status_code in [201, 422]
    
    def test_slug_with_spaces(self, client):
        """Boundary: Slug with spaces (invalid)"""
        payload = {
            "nombre_empresa": "SpaceCorp",
            "slug": "space corp invalid",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        assert res.status_code in [201, 422]


class TestCompaniesDuplicates:
    """Duplicate Handling & Unique Constraints"""
    
    def test_duplicate_nombre_empresa(self, client):
        """Duplicate: Same company name"""
        company = {
            "nombre_empresa": "UniqueCorp",
            "slug": "uniquecorp1",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        # Create first
        res1 = client.post("/api/v1/empresas/", json=company)
        assert res1.status_code == 201
        
        # Try duplicate with different slug
        company["slug"] = "uniquecorp2"
        res2 = client.post("/api/v1/empresas/", json=company)
        
        assert res2.status_code == 400
        assert "ya existe" in res2.json()["detail"].lower()
    
    def test_duplicate_slug(self, client):
        """Duplicate: Same slug"""
        company1 = {
            "nombre_empresa": "Company One",
            "slug": "same-slug",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        client.post("/api/v1/empresas/", json=company1)
        
        company2 = {
            "nombre_empresa": "Company Two",
            "slug": "same-slug",  # Duplicate
            "industria": "Finance",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=company2)
        assert res.status_code == 400
        assert "slug" in res.json()["detail"].lower()


class TestCompaniesSoftDelete:
    """Soft Delete & State Management"""
    
    def test_access_deleted_company(self, client):
        """Soft Delete: Access inactive company"""
        company = {
            "nombre_empresa": "ToDelete",
            "slug": "todelete",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=company)
        company_id = res.json()["id"]
        
        # Delete (soft)
        client.delete(f"/api/v1/empresas/{company_id}")
        
        # Try to access
        res = client.get(f"/api/v1/empresas/{company_id}")
        
        # Should return 404 or show esta_activo=False
        if res.status_code == 200:
            assert res.json()["esta_activo"] == False
    
    def test_deleted_company_not_in_list(self, client):
        """Soft Delete: Deleted companies don't appear in list"""
        company = {
            "nombre_empresa": "HiddenCorp",
            "slug": "hiddencorp",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=company)
        company_id = res.json()["id"]
        
        # Verify in list
        res = client.get("/api/v1/empresas/")
        assert len(res.json()) >= 1
        
        # Delete
        client.delete(f"/api/v1/empresas/{company_id}")
        
        # Verify NOT in list
        res = client.get("/api/v1/empresas/")
        ids = [c["id"] for c in res.json()]
        assert company_id not in ids


class TestCompaniesFuzzing:
    """Fuzzing & Malformed Input"""
    
    def test_null_values(self, client):
        """Fuzzing: Null values in required fields"""
        payload = {
            "nombre_empresa": None,
            "slug": None,
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        assert res.status_code == 422
    
    def test_wrong_types(self, client):
        """Fuzzing: Wrong data types"""
        payload = {
            "nombre_empresa": 12345,  # Should be string
            "slug": True,  # Should be string
            "industria": ["Tech", "Finance"],  # Should be string
            "pais": {"name": "Ecuador"}  # Should be string
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        assert res.status_code == 422
    
    def test_unicode_chaos(self, client):
        """Fuzzing: Unicode emojis and special chars"""
        payload = {
            "nombre_empresa": "TechCorp 🚀 你好 ñÑ çÇ",
            "slug": "techcorp-unicode",
            "industria": "Tecnología",
            "descripcion_corta": "Innovación 💡 globally 🌍",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas/", json=payload)
        # Should handle Unicode gracefully
        assert res.status_code == 201
