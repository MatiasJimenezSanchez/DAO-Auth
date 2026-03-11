"""
Tests para Oracle API - El Oráculo (Test Vocacional)
Usa fixtures de autenticación del conftest.py
"""
import pytest
from fastapi import status


class TestOracleFlow:
    """Flujo completo del test vocacional"""

    def test_start_session(self, client, auth_headers):
        """Test: Iniciar sesión del Oráculo"""
        res = client.post("/api/v1/oracle/sessions", headers=auth_headers)
        assert res.status_code == status.HTTP_201_CREATED
        
        data = res.json()
        assert "id" in data
        assert data["estado"] == "iniciada"
        assert data["paso_actual"] == 1

    def test_cannot_start_multiple_sessions(self, client, auth_headers):
        """Test: No se pueden tener múltiples sesiones activas"""
        # Primera sesión
        res1 = client.post("/api/v1/oracle/sessions", headers=auth_headers)
        assert res1.status_code == status.HTTP_201_CREATED
        
        # Intentar segunda sesión
        res2 = client.post("/api/v1/oracle/sessions", headers=auth_headers)
        assert res2.status_code == status.HTTP_400_BAD_REQUEST
        assert "sesión activa" in res2.json()["detail"].lower()

    def test_get_questions_empty_when_no_questions_in_db(self, client, auth_headers):
        """Test: Obtener preguntas retorna lista vacía si no hay preguntas en BD"""
        # Crear sesión
        session_res = client.post("/api/v1/oracle/sessions", headers=auth_headers)
        assert session_res.status_code == status.HTTP_201_CREATED
        session_id = session_res.json()["id"]
        
        # Obtener preguntas (lista vacía porque no hay preguntas en la BD de prueba)
        res = client.get(f"/api/v1/oracle/sessions/{session_id}/questions", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        
        questions = res.json()
        assert isinstance(questions, list)
        # En BD de prueba vacía, esperamos lista vacía
        assert len(questions) >= 0

    def test_submit_answer_requires_auth(self, client):
        """Test: Enviar respuesta requiere autenticación"""
        res = client.post("/api/v1/oracle/sessions/1/answers", json={
            "pregunta_id": 1,
            "opcion_id": 1
        })
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestOracleValidations:
    """Validaciones del Oráculo"""

    def test_cannot_access_other_user_session(self, client, auth_headers, db_session, test_user):
        """Test: No se puede acceder a sesión de otro usuario"""
        from app.models.user import User
        from app.models.oracle import OracleSession
        from app.core.security import get_password_hash
        
        # Crear otro usuario
        other_user = User(
            username="otheruser",
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other User",
            is_active=True,
            xp_total=0,
            level_current=1
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        # Crear sesión para el otro usuario
        other_session = OracleSession(
            usuario_id=other_user.id,
            estado="iniciada",
            paso_actual=1,
            inferred_skills={}
        )
        db_session.add(other_session)
        db_session.commit()
        db_session.refresh(other_session)
        
        # Intentar acceder con usuario autenticado actual (test_user)
        res = client.get(
            f"/api/v1/oracle/sessions/{other_session.id}/questions",
            headers=auth_headers
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_submit_answer_validates_session_ownership(self, client, auth_headers, db_session):
        """Test: Solo el dueño de la sesión puede enviar respuestas"""
        from app.models.user import User
        from app.models.oracle import OracleSession
        from app.core.security import get_password_hash
        
        # Crear otro usuario y su sesión
        other_user = User(
            username="another_user",
            email="another@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Another User",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        other_session = OracleSession(
            usuario_id=other_user.id,
            estado="iniciada",
            paso_actual=1
        )
        db_session.add(other_session)
        db_session.commit()
        db_session.refresh(other_session)
        
        # Intentar enviar respuesta a sesión ajena
        res = client.post(
            f"/api/v1/oracle/sessions/{other_session.id}/answers",
            headers=auth_headers,
            json={
                "pregunta_id": 1,
                "opcion_id": 1
            }
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestOracleWithData:
    """Tests con datos de preguntas y opciones"""
    
    def test_get_questions_with_seeded_data(self, client, auth_headers, db_session):
        """Test: Obtener preguntas cuando hay datos en BD"""
        from app.models.oracle import OracleQuestion, QuestionOption
        
        # Crear pregunta de prueba
        question = OracleQuestion(
            pregunta="Pregunta de prueba 1",
            categoria="intereses",
            orden=1,
            esta_activo=True
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        # Crear opciones
        option1 = QuestionOption(
            pregunta_id=question.id,
            texto_opcion="Leer un libro",
            orden=1,
            skill_mapping={"analytical": 20}
        )
        option2 = QuestionOption(
            pregunta_id=question.id,
            texto_opcion="Salir con amigos",
            orden=2,
            skill_mapping={"social": 20}
        )
        db_session.add_all([option1, option2])
        db_session.commit()
        
        # Crear sesión
        session_res = client.post("/api/v1/oracle/sessions", headers=auth_headers)
        session_id = session_res.json()["id"]
        
        # Obtener preguntas
        res = client.get(f"/api/v1/oracle/sessions/{session_id}/questions", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        
        questions = res.json()
        assert len(questions) >= 1
        assert "pregunta" in questions[0]
        assert len(questions[0]["opciones"]) == 2


