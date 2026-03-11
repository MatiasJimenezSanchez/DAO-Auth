"""
AI API Router - Mentores Virtuales de IA
Endpoints para chat conversacional con LLMs
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.ai_service import AIService
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationListItem
)

router = APIRouter()


@router.post("/mentors/{mentor_id}/chat", response_model=ChatResponse)
def send_chat_message(
    mentor_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enviar mensaje al mentor virtual y recibir respuesta
    
    Flujo:
    1. Validar mentor existe
    2. Obtener o crear conversación activa
    3. Guardar mensaje del usuario
    4. Generar respuesta del LLM (mock)
    5. Guardar respuesta del asistente
    6. Retornar respuesta completa
    """
    service = AIService(db)
    
    try:
        result = service.send_message_and_get_response(
            user=current_user,
            mentor_id=mentor_id,
            mensaje=request.mensaje,
            contexto_adicional=request.contexto_adicional
        )
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando mensaje: {str(e)}"
        )


@router.get("/mentors/{mentor_id}/conversations", response_model=ConversationDetail)
def get_conversation_history(
    mentor_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial completo de conversación activa con un mentor
    
    Incluye:
    - Metadata de la conversación
    - Todos los mensajes ordenados cronológicamente
    - Información del mentor
    """
    service = AIService(db)
    
    try:
        conversation = service.get_conversation_history(
            user_id=current_user.id,
            mentor_id=mentor_id
        )
        
        return ConversationDetail(**conversation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo conversación: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationListItem])
def list_all_conversations(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Listar todas las conversaciones del usuario
    
    Retorna lista resumida con:
    - Último mensaje preview
    - Fecha último mensaje
    - Total de mensajes
    - Estado de la conversación
    """
    service = AIService(db)
    
    try:
        conversations = service.get_all_conversations(
            user_id=current_user.id,
            limit=limit
        )
        
        return [ConversationListItem(**conv) for conv in conversations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando conversaciones: {str(e)}"
        )
