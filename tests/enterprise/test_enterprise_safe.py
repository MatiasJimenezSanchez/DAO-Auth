import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.models.enterprise import FeedPost, Notification, SupportTicket, SubscriptionPlan, FraudAttempt
from app.schemas.enterprise import FeedPostCreate, NotificationCreate, SupportTicketCreate, SubscriptionPlanCreate, FraudAttemptCreate

class TestEnterpriseSafe:
    def test_model_feedpost(self):
        post = FeedPost(user_id=1, contenido="Test", esta_activo=True)
        assert post.contenido == "Test"

    def test_schema_feedpost_vacio(self):
        with pytest.raises(ValidationError):
            FeedPostCreate(user_id=1, contenido="")

    def test_schema_notification_tipo(self):
        with pytest.raises(ValidationError):
            NotificationCreate(user_id=1, titulo="A", mensaje="B", tipo="error")

    def test_schema_ticket_prioridad(self):
        with pytest.raises(ValidationError):
            SupportTicketCreate(user_id=1, asunto="abc", descripcion="abcdefghijk", prioridad="urgente")

    def test_model_subscription_plan(self):
        plan = SubscriptionPlan(nombre="Pro", precio_mensual=29.99, caracteristicas={"certificados": True})
        assert plan.caracteristicas["certificados"] is True

    def test_schema_fraud_ip(self):
        with pytest.raises(ValidationError):
            FraudAttemptCreate(ip_address="1.1", tipo_intento="hack")
