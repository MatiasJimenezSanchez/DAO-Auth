"""
tests/api/test_b2b_endpoints.py — Pruebas de integración del Dashboard B2B
"""
import pytest
from fastapi import status

class TestB2BDashboard:

    def test_b2b_requires_auth(self, client):
        res = client.get("/api/v1/b2b/companies/1/dashboard")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_b2b_access_denied_for_normal_user(self, client, auth_headers, db_session):
        """Un usuario normal (sin membresía en usuarios_empresa) no puede ver el dashboard."""
        from app.models.empresa import Empresa
        empresa = db_session.query(Empresa).first()
        
        res = client.get(f"/api/v1/b2b/companies/{empresa.id}/dashboard", headers=auth_headers)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_b2b_access_granted_for_company_user(self, client, auth_headers, test_user, db_session):
        """Un usuario asignado a la empresa sí puede ver el dashboard."""
        from app.models.empresa import Empresa
        from app.models.usuarios_empresa import CompanyUser
        
        empresa = db_session.query(Empresa).first()
        
        # Le damos permisos B2B al test_user
        membership = CompanyUser(
            user_id=test_user.id,
            empresa_id=empresa.id,
            role="admin",
            permissions=["read"]
        )
        db_session.add(membership)
        db_session.commit()
        
        res = client.get(f"/api/v1/b2b/companies/{empresa.id}/dashboard", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        
        data = res.json()
        assert "total_simulations" in data
        assert "overall_completion_rate" in data
        assert data["company_id"] == empresa.id
