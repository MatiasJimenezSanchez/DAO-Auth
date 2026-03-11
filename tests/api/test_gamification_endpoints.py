"""
tests/api/test_gamification_endpoints.py — Fase 16
Cubre award-xp, leaderboard, achievements y xp-history.
Incluye tests unitarios de las funciones puras de cálculo de niveles.
"""
import pytest
from fastapi import status


# =============================================================================
# TESTS UNITARIOS — Funciones puras (sin DB, sin fixtures)
# =============================================================================

class TestLevelCalculations:
    """Verifica la fórmula de niveles sin tocar la base de datos."""

    def test_xp_para_nivel_1_es_cero(self):
        from app.services.gamification_service import xp_para_nivel
        assert xp_para_nivel(1) == 0

    def test_xp_para_nivel_2_es_100(self):
        from app.services.gamification_service import xp_para_nivel
        assert xp_para_nivel(2) == 100

    def test_xp_para_nivel_3_es_400(self):
        from app.services.gamification_service import xp_para_nivel
        assert xp_para_nivel(3) == 400

    def test_xp_para_nivel_4_es_900(self):
        from app.services.gamification_service import xp_para_nivel
        assert xp_para_nivel(4) == 900

    def test_nivel_desde_0_xp_es_1(self):
        from app.services.gamification_service import calcular_nivel_desde_xp
        assert calcular_nivel_desde_xp(0) == 1

    def test_nivel_desde_99_xp_es_1(self):
        from app.services.gamification_service import calcular_nivel_desde_xp
        assert calcular_nivel_desde_xp(99) == 1

    def test_nivel_desde_100_xp_es_2(self):
        from app.services.gamification_service import calcular_nivel_desde_xp
        assert calcular_nivel_desde_xp(100) == 2

    def test_nivel_desde_399_xp_es_2(self):
        from app.services.gamification_service import calcular_nivel_desde_xp
        assert calcular_nivel_desde_xp(399) == 2

    def test_nivel_desde_400_xp_es_3(self):
        from app.services.gamification_service import calcular_nivel_desde_xp
        assert calcular_nivel_desde_xp(400) == 3

    def test_nivel_desde_900_xp_es_4(self):
        from app.services.gamification_service import calcular_nivel_desde_xp
        assert calcular_nivel_desde_xp(900) == 4

    def test_xp_para_siguiente_nivel_desde_0(self):
        from app.services.gamification_service import xp_para_siguiente_nivel
        assert xp_para_siguiente_nivel(0) == 100

    def test_xp_para_siguiente_nivel_desde_100(self):
        from app.services.gamification_service import xp_para_siguiente_nivel
        assert xp_para_siguiente_nivel(100) == 300

    def test_xp_para_siguiente_nivel_desde_50(self):
        from app.services.gamification_service import xp_para_siguiente_nivel
        assert xp_para_siguiente_nivel(50) == 50

    def test_formula_es_creciente(self):
        from app.services.gamification_service import xp_para_nivel
        umbrales = [xp_para_nivel(n) for n in range(1, 11)]
        assert umbrales == sorted(umbrales), "Los umbrales deben ser crecientes"


# =============================================================================
# POST /api/v1/gamification/award-xp
# =============================================================================

class TestAwardXP:

    def test_award_xp_requires_auth(self, client, db_session, test_user):
        from app.models.user import User
        user = db_session.query(User).first()
        res = client.post("/api/v1/gamification/award-xp", json={
            "user_id": user.id,
            "cantidad_xp": 100,
            "tipo_fuente": "bonus",
            "descripcion": "Test XP",
        })
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_award_xp_success(self, client, auth_headers, test_user):
        res = client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 100,
                "tipo_fuente": "bonus",
                "descripcion": "Bonus de prueba",
            },
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["xp_nuevo"] == 100
        assert data["xp_anterior"] == 0
        assert data["nivel_nuevo"] == 2
        assert data["subio_de_nivel"] is True
        assert "transaction" in data

    def test_award_xp_updates_user_xp(self, client, auth_headers, test_user, db_session):
        client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 50,
                "tipo_fuente": "tarea",
                "descripcion": "Completó tarea",
            },
            headers=auth_headers,
        )
        from app.models.user import User
        db_session.expire_all()
        updated = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated.xp_total == 50

    def test_award_xp_no_level_up(self, client, auth_headers, test_user):
        """50 XP no alcanza el umbral de nivel 2 (100 XP)."""
        res = client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 50,
                "tipo_fuente": "tarea",
                "descripcion": "Tarea parcial",
            },
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["subio_de_nivel"] is False
        assert data["nivel_nuevo"] == 1

    def test_award_xp_nonexistent_user(self, client, auth_headers):
        res = client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": 999999,
                "cantidad_xp": 100,
                "tipo_fuente": "bonus",
                "descripcion": "No existe",
            },
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_award_xp_invalid_tipo_fuente(self, client, auth_headers, test_user):
        res = client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 100,
                "tipo_fuente": "invalido",
                "descripcion": "Tipo inválido",
            },
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_award_xp_zero_rejected(self, client, auth_headers, test_user):
        """cantidad_xp=0 debe ser rechazado por Pydantic (gt=0)."""
        res = client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 0,
                "tipo_fuente": "bonus",
                "descripcion": "Cero XP",
            },
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_award_xp_accumulates(self, client, auth_headers, test_user):
        """Múltiples awards acumulan correctamente."""
        for i in range(3):
            client.post(
                "/api/v1/gamification/award-xp",
                json={
                    "user_id": test_user.id,
                    "cantidad_xp": 50,
                    "tipo_fuente": "tarea",
                    "descripcion": f"Tarea {i}",
                },
                headers=auth_headers,
            )
        # Último award: 150 XP total → nivel 2
        res = client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 50,
                "tipo_fuente": "tarea",
                "descripcion": "Tarea final",
            },
            headers=auth_headers,
        )
        data = res.json()
        assert data["xp_nuevo"] == 200
        assert data["nivel_nuevo"] == 2

    def test_award_xp_transaction_recorded(self, client, auth_headers, test_user, db_session):
        """Verifica que la transacción queda en la tabla transacciones_xp."""
        client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 75,
                "tipo_fuente": "logro",
                "descripcion": "Logro desbloqueado",
                "fuente_id": 1,
            },
            headers=auth_headers,
        )
        from app.models.gamification import XPTransaction
        tx = db_session.query(XPTransaction).filter(
            XPTransaction.user_id == test_user.id
        ).first()
        assert tx is not None
        assert tx.cantidad_xp == 75
        assert tx.xp_nuevo == 75


# =============================================================================
# GET /api/v1/gamification/leaderboard
# =============================================================================

class TestLeaderboard:

    def test_leaderboard_public(self, client):
        """El leaderboard no requiere autenticación."""
        res = client.get("/api/v1/gamification/leaderboard")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert "entries" in data
        assert "total" in data

    def test_leaderboard_returns_list(self, client):
        res = client.get("/api/v1/gamification/leaderboard")
        assert isinstance(res.json()["entries"], list)

    def test_leaderboard_ordered_by_xp_desc(self, client, auth_headers, test_user, db_session):
        """Usuarios con más XP aparecen primero."""
        import uuid
        from app.models.user import User
        from app.core.security import get_password_hash

        # Crear segundo usuario con más XP
        uid = uuid.uuid4().hex[:6]
        user2 = User(
            username=f"highxp_{uid}",
            email=f"highxp_{uid}@test.com",
            hashed_password=get_password_hash("pass"),
            full_name="High XP User",
            is_active=True,
            xp_total=9999,
            level_current=10,
        )
        db_session.add(user2)
        db_session.commit()

        res = client.get("/api/v1/gamification/leaderboard")
        entries = res.json()["entries"]
        assert len(entries) >= 2
        # El primero debe tener mayor o igual XP que el segundo
        xps = [e["xp_total"] for e in entries]
        assert xps == sorted(xps, reverse=True)

    def test_leaderboard_entry_fields(self, client):
        res = client.get("/api/v1/gamification/leaderboard")
        entries = res.json()["entries"]
        if entries:
            entry = entries[0]
            for field in ("rank", "user_id", "username", "full_name", "xp_total", "level_current"):
                assert field in entry, f"Campo '{field}' ausente en leaderboard entry"

    def test_leaderboard_rank_starts_at_1(self, client):
        res = client.get("/api/v1/gamification/leaderboard")
        entries = res.json()["entries"]
        if entries:
            assert entries[0]["rank"] == 1

    def test_leaderboard_pagination_limit(self, client, auth_headers, test_user, db_session):
        import uuid
        from app.models.user import User
        from app.core.security import get_password_hash

        # Crear 5 usuarios extra
        for i in range(5):
            uid = uuid.uuid4().hex[:6]
            u = User(
                username=f"paguser_{uid}",
                email=f"paguser_{uid}@test.com",
                hashed_password=get_password_hash("pass"),
                full_name=f"Pag User {i}",
                is_active=True,
                xp_total=i * 10,
            )
            db_session.add(u)
        db_session.commit()

        res = client.get("/api/v1/gamification/leaderboard?limit=3")
        assert res.status_code == status.HTTP_200_OK
        assert len(res.json()["entries"]) <= 3

    def test_leaderboard_skip(self, client):
        res_full = client.get("/api/v1/gamification/leaderboard?skip=0&limit=10")
        res_skip = client.get("/api/v1/gamification/leaderboard?skip=1&limit=10")
        full = res_full.json()["entries"]
        skipped = res_skip.json()["entries"]
        if len(full) > 1:
            assert full[1]["user_id"] == skipped[0]["user_id"]


# =============================================================================
# GET /api/v1/users/me/achievements
# =============================================================================

class TestMyAchievements:

    def test_requires_auth(self, client):
        res = client.get("/api/v1/users/me/achievements")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_achievements(self, client, auth_headers):
        """Usuario sin logros devuelve lista vacía."""
        res = client.get("/api/v1/users/me/achievements", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == []

    def test_returns_unlocked_achievements(self, client, auth_headers, test_user, db_session):
        """Logro desbloqueado aparece en la lista."""
        from app.models.gamification import Achievement, UserAchievement, TipoLogroEnum

        logro = Achievement(
            titulo="Primer Paso",
            descripcion="Completó su primera tarea",
            tipo_logro=TipoLogroEnum.BRONCE,
            recompensa_xp=50,
            is_active=True,
        )
        db_session.add(logro)
        db_session.flush()

        ua = UserAchievement(
            user_id=test_user.id,
            logro_id=logro.id,
            desbloqueado=True,
        )
        db_session.add(ua)
        db_session.commit()

        res = client.get("/api/v1/users/me/achievements", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["logro_id"] == logro.id
        assert data[0]["desbloqueado"] is True

    def test_solo_desbloqueados_false(self, client, auth_headers, test_user, db_session):
        """Con solo_desbloqueados=false devuelve todos los logros (incluso no desbloqueados)."""
        from app.models.gamification import Achievement, UserAchievement, TipoLogroEnum

        logro = Achievement(
            titulo="Logro Secreto",
            descripcion="No desbloqueado aún",
            tipo_logro=TipoLogroEnum.PLATINO,
            recompensa_xp=500,
            is_active=True,
        )
        db_session.add(logro)
        db_session.flush()

        ua = UserAchievement(
            user_id=test_user.id,
            logro_id=logro.id,
            desbloqueado=False,
        )
        db_session.add(ua)
        db_session.commit()

        res_default = client.get("/api/v1/users/me/achievements", headers=auth_headers)
        assert len(res_default.json()) == 0

        res_all = client.get(
            "/api/v1/users/me/achievements?solo_desbloqueados=false",
            headers=auth_headers,
        )
        assert len(res_all.json()) == 1


# =============================================================================
# GET /api/v1/gamification/xp-history
# =============================================================================

class TestXPHistory:

    def test_requires_auth(self, client):
        res = client.get("/api/v1/gamification/xp-history")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_history(self, client, auth_headers):
        res = client.get("/api/v1/gamification/xp-history", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == []

    def test_history_after_award(self, client, auth_headers, test_user):
        client.post(
            "/api/v1/gamification/award-xp",
            json={
                "user_id": test_user.id,
                "cantidad_xp": 200,
                "tipo_fuente": "mision",
                "descripcion": "Misión completada",
            },
            headers=auth_headers,
        )
        res = client.get("/api/v1/gamification/xp-history", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["cantidad_xp"] == 200
        assert data[0]["tipo_fuente"] == "mision"

    def test_history_ordered_desc(self, client, auth_headers, test_user):
        """El historial más reciente aparece primero."""
        import time
        for xp in [10, 20, 30]:
            time.sleep(0.1)  # Forzar diferencia de tiempo para ordenamiento DESC
            client.post(

                "/api/v1/gamification/award-xp",
                json={
                    "user_id": test_user.id,
                    "cantidad_xp": xp,
                    "tipo_fuente": "bonus",
                    "descripcion": f"Award {xp}",
                },
                headers=auth_headers,
            )
        res = client.get("/api/v1/gamification/xp-history", headers=auth_headers)
        data = res.json()
        # El más reciente (30 XP) debe ser el primero
        assert data[0]["cantidad_xp"] == 30
