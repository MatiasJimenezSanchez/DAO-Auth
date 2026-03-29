"""
tests/api/test_simulations_endpoints.py — Fase 15
Cubre los 4 endpoints core + casos de error.
Usa conftest.py con Global Seeder (category_id=1, company_id=1 ya existen).
"""
import uuid
import pytest
from fastapi import status


# =============================================================================
# HELPERS
# =============================================================================

def make_sim_data(company_id: int, category_id: int, state: str = "published") -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "title": f"Sim {uid}",
        "slug": f"sim-{uid}",
        "short_description": "Simulación de prueba",
        "company_id": company_id,
        "category_id": category_id,
        "state": state,
    }


def create_sim(client, company_id: int, category_id: int, state: str = "published") -> dict:
    """Crea una simulación y devuelve el JSON de respuesta."""
    res = client.post("/api/v1/simulaciones", json=make_sim_data(company_id, category_id, state))
    assert res.status_code == status.HTTP_201_CREATED, f"create_sim falló: {res.text}"
    return res.json()


# =============================================================================
# GET /api/v1/simulaciones
# =============================================================================

class TestListSimulations:

    def test_list_returns_200(self, client):
        res = client.get("/api/v1/simulaciones")
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(res.json(), list)

    def test_list_includes_created_sim(self, client, db_session):
        """La simulación recién creada aparece en el listado."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id)
        res = client.get("/api/v1/simulaciones")
        ids = [s["id"] for s in res.json()]
        assert sim["id"] in ids

    def test_list_filter_by_state(self, client, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        create_sim(client, empresa.id, cat.id, state="published")
        create_sim(client, empresa.id, cat.id, state="draft")

        res = client.get("/api/v1/simulaciones?state=published")
        assert res.status_code == status.HTTP_200_OK
        for s in res.json():
            assert s["state"] == "published"

    def test_list_filter_by_company(self, client, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        create_sim(client, empresa.id, cat.id)
        res = client.get(f"/api/v1/simulaciones?company_id={empresa.id}")
        assert res.status_code == status.HTTP_200_OK
        for s in res.json():
            assert s["company_id"] == empresa.id

    def test_list_pagination_limit(self, client, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        for _ in range(5):
            create_sim(client, empresa.id, cat.id)

        res = client.get("/api/v1/simulaciones?limit=2")
        assert res.status_code == status.HTTP_200_OK
        assert len(res.json()) <= 2

    def test_list_empty_when_no_sims(self, client):
        res = client.get("/api/v1/simulaciones?state=archived")
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == []


# =============================================================================
# GET /api/v1/simulaciones/{id}
# =============================================================================

class TestGetSimulation:

    def test_get_existing_sim(self, client, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id)
        res = client.get(f"/api/v1/simulaciones/{sim['id']}")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["id"] == sim["id"]
        assert res.json()["title"] == sim["title"]

    def test_get_nonexistent_returns_404(self, client):
        res = client.get("/api/v1/simulaciones/999999")
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_get_returns_correct_fields(self, client, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id)
        data = client.get(f"/api/v1/simulaciones/{sim['id']}").json()
        for field in ("id", "title", "slug", "state", "company_id", "category_id", "created_at"):
            assert field in data, f"Campo '{field}' ausente en respuesta"


# =============================================================================
# POST /api/v1/simulaciones/{id}/inscribir
# =============================================================================

class TestEnrollSimulation:

    def test_enroll_requires_auth(self, client, db_session):
        """Sin token → 401."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id, state="published")
        res = client.post(f"/api/v1/simulaciones/{sim['id']}/inscribir")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_enroll_published_sim_success(self, client, auth_headers, db_session):
        """Usuario autenticado puede inscribirse en simulación publicada."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id, state="published")
        res = client.post(
            f"/api/v1/simulaciones/{sim['id']}/inscribir",
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["status"] == "enrolled"
        assert "enrollment" in data
        assert data["enrollment"]["simulation_id"] == sim["id"]

    def test_enroll_draft_sim_rejected(self, client, auth_headers, db_session):
        """No se puede inscribir en una simulación en borrador."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id, state="draft")
        res = client.post(
            f"/api/v1/simulaciones/{sim['id']}/inscribir",
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_enroll_nonexistent_sim_404(self, client, auth_headers):
        res = client.post("/api/v1/simulaciones/999999/inscribir", headers=auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_enroll_duplicate_rejected(self, client, auth_headers, db_session):
        """Inscripción duplicada devuelve 400."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id, state="published")
        # Primera inscripción — OK
        res1 = client.post(
            f"/api/v1/simulaciones/{sim['id']}/inscribir",
            headers=auth_headers,
        )
        assert res1.status_code == status.HTTP_201_CREATED
        # Segunda inscripción — duplicado
        res2 = client.post(
            f"/api/v1/simulaciones/{sim['id']}/inscribir",
            headers=auth_headers,
        )
        assert res2.status_code == status.HTTP_400_BAD_REQUEST

    def test_enroll_spots_decrement(self, client, auth_headers, db_session):
        """Los cupos disponibles disminuyen tras inscripción."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        uid = uuid.uuid4().hex[:8]
        res_create = client.post("/api/v1/simulaciones", json={
            "title": f"Limited Sim {uid}",
            "slug": f"limited-{uid}",
            "short_description": "Cupos limitados",
            "company_id": empresa.id,
            "category_id": cat.id,
            "state": "published",
            "total_spots": 5,
        })
        assert res_create.status_code == status.HTTP_201_CREATED
        sim_id = res_create.json()["id"]

        res_enroll = client.post(
            f"/api/v1/simulaciones/{sim_id}/inscribir",
            headers=auth_headers,
        )
        assert res_enroll.status_code == status.HTTP_201_CREATED
        assert res_enroll.json()["spots_left"] == 4


# =============================================================================
# GET /api/v1/users/me/simulations
# =============================================================================

class TestMySimulations:

    def test_requires_auth(self, client):
        res = client.get("/api/v1/users/me/simulations")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_empty_before_enroll(self, client, auth_headers):
        res = client.get("/api/v1/users/me/simulations", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == []

    def test_returns_enrolled_simulation(self, client, auth_headers, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id, state="published")
        client.post(f"/api/v1/simulaciones/{sim['id']}/inscribir", headers=auth_headers)

        res = client.get("/api/v1/users/me/simulations", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        sim_ids = [s["simulation_id"] for s in res.json()]
        assert sim["id"] in sim_ids

    def test_filter_by_estado(self, client, auth_headers, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        sim = create_sim(client, empresa.id, cat.id, state="published")
        client.post(f"/api/v1/simulaciones/{sim['id']}/inscribir", headers=auth_headers)

        res = client.get("/api/v1/users/me/simulations?estado=inscrito", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        for s in res.json():
            assert s["estado"] == "inscrito"

    def test_isolation_between_users(self, client, db_session):
        """Las simulaciones de un usuario no aparecen en las de otro."""
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token

        empresa = db_session.query(Empresa).first()
        cat = db_session.query(ContentCategory).first()

        # Usuario 2
        uid = uuid.uuid4().hex[:6]
        user2 = User(
            username=f"user2_{uid}",
            email=f"user2_{uid}@test.com",
            hashed_password=get_password_hash("pass"),
            full_name="User Two",
            is_active=True,
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)
        token2 = create_access_token(data={"sub": user2.email})
        headers2 = {"Authorization": f"Bearer {token2}"}

        sim = create_sim(client, empresa.id, cat.id, state="published")

        # user2 se inscribe
        client.post(f"/api/v1/simulaciones/{sim['id']}/inscribir", headers=headers2)

        # testuser (auth_headers) NO debe ver esa inscripción
        from app.core.security import create_access_token as cat_
        # Creamos testuser para auth_headers
        user1 = User(
            username=f"user1_{uid}",
            email=f"user1_{uid}@test.com",
            hashed_password=get_password_hash("pass"),
            full_name="User One",
            is_active=True,
        )
        db_session.add(user1)
        db_session.commit()
        db_session.refresh(user1)
        token1 = create_access_token(data={"sub": user1.email})
        headers1 = {"Authorization": f"Bearer {token1}"}

        res = client.get("/api/v1/users/me/simulations", headers=headers1)
        assert res.status_code == status.HTTP_200_OK
        sim_ids = [s["simulation_id"] for s in res.json()]
        assert sim["id"] not in sim_ids
