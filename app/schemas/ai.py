"""
AI Schemas - Mentores Virtuales de IA
Schemas para chat conversacional con LLMs
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


# ============================================
# CHAT REQUEST & RESPONSE
# ============================================

class ChatRequest(BaseModel):
    """Request para enviar mensaje al mentor"""
    mensaje: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    contexto_adicional: Optional[str] = Field(None, max_length=1000, description="Contexto opcional de la simulación")


class MentorMessageDetail(BaseModel):
    """Detalle de un mensaje en la conversación"""
    id: int
    rol: str  # 'user' o 'assistant'
    contenido: str
    created_at: datetime
    tokens_usados: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """Response después de enviar mensaje"""
    conversacion_id: int
    mensaje_usuario_id: int
    mensaje_asistente_id: int
    respuesta: str
    tokens_usados: int
    modelo_usado: str


class ConversationDetail(BaseModel):
    """Detalle completo de una conversación"""
    id: int
    mentor_id: int
    mentor_nombre: str
    simulation_id: Optional[int]
    estado: str
    total_mensajes: int
    fecha_inicio: datetime
    fecha_ultimo_mensaje: datetime
    mensajes: List[MentorMessageDetail] = []
    
    model_config = ConfigDict(from_attributes=True)


class ConversationListItem(BaseModel):
    """Item en lista de conversaciones"""
    id: int
    mentor_id: int
    mentor_nombre: str
    estado: str
    total_mensajes: int
    ultimo_mensaje_preview: Optional[str] = None
    fecha_ultimo_mensaje: datetime
    
    model_config = ConfigDict(from_attributes=True)
