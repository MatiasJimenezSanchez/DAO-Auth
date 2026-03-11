"""
Oracle API Router - El Oráculo (Test Vocacional)
Endpoints para iniciar sesión, responder preguntas y obtener resultados
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.oracle_service import OracleService
from app.schemas.oracle import SessionOut, QuestionOut, AnswerCreate

router = APIRouter()


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def start_oracle_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Iniciar nueva sesión del Oráculo
    
    - Valida que no haya sesión activa
    - Crea sesión en estado 'iniciada'
    """
    service = OracleService(db)
    session = service.start_session(current_user.id)
    return session


@router.get("/sessions/{session_id}/questions", response_model=List[QuestionOut])
def get_next_questions(
    session_id: int,
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener siguientes preguntas para responder
    
    - Retorna preguntas no respondidas
    - Incluye opciones de cada pregunta
    """
    service = OracleService(db)
    
    # Validar que la sesión pertenece al usuario
    from app.repositories.oracle_repository import OracleRepository
    repo = OracleRepository(None, db)
    session = repo.get_session_by_id(db, session_id)
    
    if not session or session.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    questions = service.get_next_questions(session_id, limit)
    return questions


@router.post("/sessions/{session_id}/answers")
def submit_answer(
    session_id: int,
    answer: AnswerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enviar respuesta a una pregunta
    
    - Valida sesión activa
    - Registra respuesta
    - Acumula skills inferidos
    """
    service = OracleService(db)
    
    # Validar que la sesión pertenece al usuario
    from app.repositories.oracle_repository import OracleRepository
    repo = OracleRepository(None, db)
    session = repo.get_session_by_id(db, session_id)
    
    if not session or session.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    result = service.submit_answer(
        session_id,
        answer.pregunta_id,
        answer.opcion_id,
        answer.tiempo_respuesta_segundos
    )
    
    return result


@router.get("/sessions/{session_id}/results")
def get_session_results(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener resultados del test vocacional
    
    - Requiere al menos 5 respuestas
    - Calcula arquetipo psicológico
    - Retorna skills inferidos
    """
    service = OracleService(db)
    
    # Validar que la sesión pertenece al usuario
    from app.repositories.oracle_repository import OracleRepository
    repo = OracleRepository(None, db)
    session = repo.get_session_by_id(db, session_id)
    
    if not session or session.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    results = service.get_results(session_id)
    return results
