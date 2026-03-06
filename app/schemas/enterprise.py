from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

# A: Feed Social
class FeedPostCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    contenido: str = Field(..., min_length=1)
    imagen_url: Optional[str] = Field(None, max_length=500)

class PostLikeCreate(BaseModel):
    post_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)

class PostCommentCreate(BaseModel):
    post_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    contenido: str = Field(..., min_length=1)

# B: Notificaciones
class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=1, max_length=200)
    mensaje: str = Field(..., min_length=1)
    tipo: str = Field(default="sistema", pattern="^(sistema|social|simulacion)$")

class NotificationPreferenceCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    email_marketing: bool = True
    email_alertas: bool = True
    push_social: bool = True

# C: Soporte
class SupportTicketCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    asunto: str = Field(..., min_length=3, max_length=300)
    descripcion: str = Field(..., min_length=10)
    prioridad: str = Field(default="media", pattern="^(baja|media|alta|critica)$")

class TicketMessageCreate(BaseModel):
    ticket_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    mensaje: str = Field(..., min_length=1)

class GeneralFeedbackCreate(BaseModel):
    tipo: str = Field(default="idea", pattern="^(bug|idea)$")
    mensaje: str = Field(..., min_length=5)
    calificacion: Optional[int] = Field(None, ge=1, le=5)

# D: Monetización y Seguridad
class SubscriptionPlanCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    precio_mensual: Decimal = Field(..., ge=0)
    caracteristicas: Optional[Dict[str, Any]] = None

class UserSubscriptionCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    plan_id: int = Field(..., gt=0)
    estado: str = Field(default="activa", pattern="^(activa|cancelada|vencida|trial)$")

class PaymentTransactionCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    plan_id: int = Field(..., gt=0)
    monto: Decimal = Field(..., gt=0)
    estado: str = Field(default="pendiente", pattern="^(pendiente|completado|fallido|reembolsado)$")

class AdminDaoCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    rol: str = Field(default="moderador", pattern="^(superadmin|moderador)$")

class FraudAttemptCreate(BaseModel):
    ip_address: str = Field(..., min_length=7, max_length=45)
    tipo_intento: str = Field(..., min_length=3, max_length=100)
