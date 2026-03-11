"""
AI Service - Motor Conversacional
Lógica de negocio para chat con mentores virtuales
"""
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.gamification import (
    VirtualMentor,
    MentorConversation,
    MentorMessage,
    EstadoConversacionEnum,
    RolMensajeEnum
)
from app.models.user import User


class AIService:
    """Servicio para gestión de conversaciones con mentores IA"""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation(
        self,
        user_id: int,
        mentor_id: int,
        simulation_id: Optional[int] = None
    ) -> MentorConversation:
        """
        Obtener conversación activa o crear nueva
        
        Lógica:
        1. Buscar conversación activa del usuario con ese mentor
        2. Si existe, retornarla
        3. Si no existe, crear nueva
        """
        # Buscar conversación activa existente
        conversation = self.db.query(MentorConversation).filter(
            MentorConversation.user_id == user_id,
            MentorConversation.mentor_id == mentor_id,
            MentorConversation.estado == EstadoConversacionEnum.ACTIVA
        ).first()
        
        if conversation:
            return conversation
        
        # Crear nueva conversación
        new_conversation = MentorConversation(
            user_id=user_id,
            mentor_id=mentor_id,
            simulation_id=simulation_id,
            estado=EstadoConversacionEnum.ACTIVA,
            total_mensajes=0
        )
        
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)
        
        return new_conversation

    def send_message_and_get_response(
        self,
        user: User,
        mentor_id: int,
        mensaje: str,
        simulation_id: Optional[int] = None,
        contexto_adicional: Optional[str] = None
    ) -> Dict:
        """
        Enviar mensaje del usuario y obtener respuesta del mentor IA
        
        Flujo completo:
        1. Validar que el mentor existe
        2. Obtener o crear conversación
        3. Guardar mensaje del usuario
        4. Generar respuesta del LLM (MOCK por ahora)
        5. Guardar respuesta del asistente
        6. Actualizar contadores de conversación
        """
        # Validar mentor existe y está activo
        mentor = self.db.query(VirtualMentor).filter(
            VirtualMentor.id == mentor_id,
            VirtualMentor.is_active == True
        ).first()
        
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mentor virtual con ID {mentor_id} no encontrado o inactivo"
            )
        
        # Obtener o crear conversación
        conversation = self.get_or_create_conversation(
            user_id=user.id,
            mentor_id=mentor_id,
            simulation_id=simulation_id
        )
        
        # Guardar mensaje del usuario
        user_message = MentorMessage(
            conversacion_id=conversation.id,
            user_id=user.id,
            mentor_id=mentor_id,
            rol=RolMensajeEnum.USER,
            contenido=mensaje,
            tokens_usados=0
        )
        
        self.db.add(user_message)
        self.db.flush()
        
        # Generar respuesta del LLM (MOCK - en producción llamaría a OpenAI/Claude)
        assistant_response = self._generate_mock_response(
            mentor=mentor,
            user_message=mensaje,
            contexto=contexto_adicional
        )
        
        # Guardar respuesta del asistente
        assistant_message = MentorMessage(
            conversacion_id=conversation.id,
            user_id=user.id,
            mentor_id=mentor_id,
            rol=RolMensajeEnum.ASSISTANT,
            contenido=assistant_response["contenido"],
            modelo_usado=mentor.modelo_ia,
            tokens_usados=assistant_response["tokens"]
        )
        
        self.db.add(assistant_message)
        
        # Actualizar conversación
        conversation.total_mensajes += 2  # Usuario + Asistente
        conversation.fecha_ultimo_mensaje = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        
        return {
            "conversacion_id": conversation.id,
            "mensaje_usuario_id": user_message.id,
            "mensaje_asistente_id": assistant_message.id,
            "respuesta": assistant_response["contenido"],
            "tokens_usados": assistant_response["tokens"],
            "modelo_usado": mentor.modelo_ia
        }

    def get_conversation_history(
        self,
        user_id: int,
        mentor_id: int
    ) -> Optional[Dict]:
        """
        Obtener historial completo de conversación activa
        Incluye todos los mensajes ordenados cronológicamente
        """
        # Buscar conversación activa
        conversation = self.db.query(MentorConversation).filter(
            MentorConversation.user_id == user_id,
            MentorConversation.mentor_id == mentor_id,
            MentorConversation.estado == EstadoConversacionEnum.ACTIVA
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe conversación activa con este mentor"
            )
        
        # Obtener mentor para el nombre
        mentor = self.db.query(VirtualMentor).filter(
            VirtualMentor.id == mentor_id
        ).first()
        
        # Obtener mensajes ordenados
        messages = self.db.query(MentorMessage).filter(
            MentorMessage.conversacion_id == conversation.id
        ).order_by(MentorMessage.created_at.asc()).all()
        
        return {
            "id": conversation.id,
            "mentor_id": mentor_id,
            "mentor_nombre": mentor.nombre if mentor else "Mentor Virtual",
            "simulation_id": conversation.simulation_id,
            "estado": conversation.estado.value,
            "total_mensajes": conversation.total_mensajes,
            "fecha_inicio": conversation.fecha_inicio,
            "fecha_ultimo_mensaje": conversation.fecha_ultimo_mensaje,
            "mensajes": messages
        }

    def get_all_conversations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        Obtener todas las conversaciones del usuario
        Retorna lista resumida con preview del último mensaje
        """
        conversations = self.db.query(MentorConversation).filter(
            MentorConversation.user_id == user_id
        ).order_by(
            MentorConversation.fecha_ultimo_mensaje.desc()
        ).limit(limit).all()
        
        result = []
        for conv in conversations:
            # Obtener mentor
            mentor = self.db.query(VirtualMentor).filter(
                VirtualMentor.id == conv.mentor_id
            ).first()
            
            # Obtener último mensaje
            last_message = self.db.query(MentorMessage).filter(
                MentorMessage.conversacion_id == conv.id
            ).order_by(
                MentorMessage.created_at.desc()
            ).first()
            
            preview = None
            if last_message:
                preview = last_message.contenido[:100] + "..." if len(last_message.contenido) > 100 else last_message.contenido
            
            result.append({
                "id": conv.id,
                "mentor_id": conv.mentor_id,
                "mentor_nombre": mentor.nombre if mentor else "Mentor",
                "estado": conv.estado.value,
                "total_mensajes": conv.total_mensajes,
                "ultimo_mensaje_preview": preview,
                "fecha_ultimo_mensaje": conv.fecha_ultimo_mensaje
            })
        
        return result

    def _generate_mock_response(
        self,
        mentor: VirtualMentor,
        user_message: str,
        contexto: Optional[str] = None
    ) -> Dict:
        """
        Generador MOCK de respuestas del LLM
        
        En producción, aquí iría:
        - Llamada a OpenAI/Claude API
        - Construcción del prompt con personalidad del mentor
        - Manejo de errores de la API
        - Conteo real de tokens
        
        Por ahora retorna respuesta hardcodeada para tests
        """
        # Respuesta base según personalidad
        if mentor.personalidad == "profesional":
            base_response = f"¡Hola! Soy {mentor.nombre}, tu mentor virtual profesional. "
        elif mentor.personalidad == "motivador":
            base_response = f"¡Excelente pregunta! Soy {mentor.nombre} y estoy aquí para motivarte. "
        elif mentor.personalidad == "técnico":
            base_response = f"Entiendo tu consulta. Soy {mentor.nombre}, especialista técnico. "
        else:
            base_response = f"¡Hola! Soy {mentor.nombre}. "
        
        # Agregar respuesta contextual
        if "ayuda" in user_message.lower() or "help" in user_message.lower():
            response = base_response + "¿En qué te puedo ayudar hoy? Estoy aquí para guiarte en tu proceso de aprendizaje."
        elif "gracias" in user_message.lower() or "thanks" in user_message.lower():
            response = base_response + "¡De nada! Es un placer ayudarte. ¿Hay algo más en lo que pueda asistirte?"
        else:
            response = base_response + f"He recibido tu mensaje: '{user_message[:50]}...'. Estoy procesando tu consulta y pronto tendrás una respuesta detallada."
        
        # Mock de tokens (en producción vendría del LLM)
        mock_tokens = len(response.split()) + len(user_message.split())
        
        return {
            "contenido": response,
            "tokens": mock_tokens
        }
