"""
Tests para AI Endpoints - Mentores Virtuales
"""
import pytest
from fastapi import status


class TestAIChatFlow:
    """Tests del flujo completo de chat con mentor"""

    def test_send_first_message_creates_conversation(self, client, auth_headers, db_session):
        """Test: Primer mensaje crea conversación automáticamente"""
        from app.models.gamification import VirtualMentor
        
        # Obtener mentor del seeder
        mentor = db_session.query(VirtualMentor).filter(
            VirtualMentor.is_active == True
        ).first()
        
        assert mentor is not None, "El seeder debe crear un VirtualMentor"
        
        # Enviar primer mensaje
        res = client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": "Hola, necesito ayuda"}
        )
        
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        
        assert "conversacion_id" in data
        assert "respuesta" in data
        assert "tokens_usados" in data
        assert data["modelo_usado"] == "gpt-4"

    def test_second_message_reuses_conversation(self, client, auth_headers, db_session):
        """Test: Segundo mensaje reutiliza conversación existente"""
        from app.models.gamification import VirtualMentor
        
        mentor = db_session.query(VirtualMentor).first()
        
        # Primer mensaje
        res1 = client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": "Primer mensaje"}
        )
        conv_id_1 = res1.json()["conversacion_id"]
        
        # Segundo mensaje
        res2 = client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": "Segundo mensaje"}
        )
        conv_id_2 = res2.json()["conversacion_id"]
        
        # Debe ser la misma conversación
        assert conv_id_1 == conv_id_2

    def test_get_conversation_history(self, client, auth_headers, db_session):
        """Test: Obtener historial completo de conversación"""
        from app.models.gamification import VirtualMentor
        
        mentor = db_session.query(VirtualMentor).first()
        
        # Enviar dos mensajes
        client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": "Mensaje 1"}
        )
        client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": "Mensaje 2"}
        )
        
        # Obtener historial
        res = client.get(
            f"/api/v1/ai/mentors/{mentor.id}/conversations",
            headers=auth_headers
        )
        
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        
        assert "mensajes" in data
        assert data["total_mensajes"] == 4  # 2 usuario + 2 asistente
        assert len(data["mensajes"]) == 4
        
        # Verificar orden cronológico
        assert data["mensajes"][0]["rol"] == "user"
        assert data["mensajes"][1]["rol"] == "assistant"
        assert data["mensajes"][2]["rol"] == "user"
        assert data["mensajes"][3]["rol"] == "assistant"


class TestAIValidations:
    """Tests de validaciones"""

    def test_chat_requires_authentication(self, client):
        """Test: Chat requiere autenticación"""
        res = client.post(
            "/api/v1/ai/mentors/1/chat",
            json={"mensaje": "Hola"}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_chat_with_nonexistent_mentor(self, client, auth_headers):
        """Test: Chat con mentor inexistente retorna 404"""
        res = client.post(
            "/api/v1/ai/mentors/999999/chat",
            headers=auth_headers,
            json={"mensaje": "Hola"}
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrado" in res.json()["detail"].lower()

    def test_empty_message_rejected(self, client, auth_headers, db_session):
        """Test: Mensaje vacío es rechazado por Pydantic"""
        from app.models.gamification import VirtualMentor
        
        mentor = db_session.query(VirtualMentor).first()
        
        res = client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": ""}
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_conversation_without_messages_returns_404(self, client, auth_headers, db_session):
        """Test: Obtener conversación sin mensajes previos retorna 404"""
        from app.models.gamification import VirtualMentor
        
        # Crear un mentor adicional sin conversación
        mentor_sin_conv = VirtualMentor(
            empresa_id=1,
            nombre="Mentor Sin Conversación",
            personalidad="profesional",
            prompt_sistema="Test",
            modelo_ia="gpt-4",
            is_active=True
        )
        db_session.add(mentor_sin_conv)
        db_session.commit()
        db_session.refresh(mentor_sin_conv)
        
        res = client.get(
            f"/api/v1/ai/mentors/{mentor_sin_conv.id}/conversations",
            headers=auth_headers
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestAIListConversations:
    """Tests de listado de conversaciones"""

    def test_list_all_conversations(self, client, auth_headers, db_session):
        """Test: Listar todas las conversaciones del usuario"""
        from app.models.gamification import VirtualMentor
        
        mentor = db_session.query(VirtualMentor).first()
        
        # Crear conversación
        client.post(
            f"/api/v1/ai/mentors/{mentor.id}/chat",
            headers=auth_headers,
            json={"mensaje": "Test"}
        )
        
        # Listar conversaciones
        res = client.get("/api/v1/ai/conversations", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        
        conversations = res.json()
        assert len(conversations) >= 1
        assert "mentor_nombre" in conversations[0]
        assert "ultimo_mensaje_preview" in conversations[0]
