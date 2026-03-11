"""
Oracle Service - Business Logic para El Oráculo
Gestiona flujo completo del test vocacional
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.repositories.oracle_repository import OracleRepository
from app.models.oracle import OracleSession, OracleQuestion, QuestionOption, Archetype


class OracleService:
    """Servicio de lógica de negocio para El Oráculo"""

    def __init__(self, db: Session):
        self.repo = OracleRepository(OracleSession, db)
        self.db = db

    def start_session(self, user_id: int) -> OracleSession:
        """
        Iniciar nueva sesión del Oráculo
        - Valida que no haya sesión activa
        - Crea sesión nueva
        """
        # Validar que no haya sesión activa
        active_sessions = self.db.query(OracleSession).filter(
            OracleSession.usuario_id == user_id,
            OracleSession.estado.in_(["iniciada", "en_progreso"])
        ).first()
        
        if active_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya tienes una sesión activa. Complétala primero."
            )
        
        return self.repo.create_session(self.db, user_id)

    def get_next_questions(self, session_id: int, limit: int = 5) -> List[OracleQuestion]:
        """
        Obtener siguientes preguntas para la sesión
        - Valida que sesión exista y esté activa
        - Retorna preguntas no respondidas
        """
        session = self.repo.get_session_by_id(self.db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión no encontrada"
            )
        
        if session.estado == "completada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sesión ya completada"
            )
        
        # Obtener IDs de preguntas ya respondidas
        answered_questions = self.repo.get_session_answers(self.db, session_id)
        answered_ids = {ans.pregunta_id for ans in answered_questions}
        
        # Obtener todas las preguntas activas
        all_questions = self.repo.get_all_active_questions(self.db)
        
        # Filtrar no respondidas
        pending_questions = [q for q in all_questions if q.id not in answered_ids]
        
        return pending_questions[:limit]

    def submit_answer(
        self, 
        session_id: int, 
        question_id: int, 
        option_id: int,
        tiempo_respuesta: Optional[int] = None
    ) -> Dict:
        """
        Registrar respuesta del usuario
        - Valida sesión activa
        - Valida pregunta y opción válidas
        - Acumula skills inferidos
        - Avanza paso actual
        """
        session = self.repo.get_session_by_id(self.db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión no encontrada"
            )
        
        if session.estado == "completada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes responder en sesión completada"
            )
        
        # Validar pregunta existe
        question = self.repo.get_question_by_id(self.db, question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregunta no encontrada"
            )
        
        # Validar opción existe y pertenece a la pregunta
        option = self.repo.get_option_by_id(self.db, option_id)
        if not option or option.pregunta_id != question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opción inválida para esta pregunta"
            )
        
        # Guardar respuesta
        answer = self.repo.save_user_answer(
            self.db, session_id, question_id, option_id, tiempo_respuesta
        )
        
        # Actualizar skills inferidos acumulados
        current_skills = session.inferred_skills or {}
        option_skills = option.skill_mapping or {}
        
        for skill, points in option_skills.items():
            current_skills[skill] = current_skills.get(skill, 0) + points
        
        # Avanzar paso y actualizar estado
        new_state = "en_progreso" if session.estado == "iniciada" else session.estado
        self.repo.update_session_state(
            self.db,
            session_id,
            estado=new_state,
            paso_actual=session.paso_actual + 1,
            inferred_skills=current_skills
        )
        
        return {
            "message": "Respuesta registrada",
            "paso_actual": session.paso_actual + 1,
            "skills_acumulados": current_skills
        }

    def get_results(self, session_id: int) -> Dict:
        """
        Obtener resultados del test
        - Calcula arquetipo basado en skills acumulados
        - Actualiza sesión a completada
        - Retorna arquetipo y habilidades
        """
        session = self.repo.get_session_by_id(self.db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión no encontrada"
            )
        
        # Validar que haya respondido al menos 5 preguntas
        answers = self.repo.get_session_answers(self.db, session_id)
        if len(answers) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Debes responder al menos 5 preguntas. Llevas {len(answers)}."
            )
        
        # Obtener skills acumulados
        inferred_skills = session.inferred_skills or {}
        
        # Encontrar arquetipo que mejor coincide
        archetypes = self.repo.get_all_archetypes(self.db)
        best_match = self._match_archetype(inferred_skills, archetypes)
        
        if best_match:
            # Asignar arquetipo y marcar como completada
            self.repo.assign_archetype_to_session(self.db, session_id, best_match.id)
        
        return {
            "session_id": session_id,
            "estado": "completada",
            "arquetipo": {
                "id": best_match.id if best_match else None,
                "nombre": best_match.nombre if best_match else "Sin clasificar",
                "descripcion": best_match.descripcion if best_match else None,
                "color": best_match.color_hex if best_match else None
            },
            "skills_inferidos": inferred_skills,
            "total_respuestas": len(answers)
        }

    def _match_archetype(self, skills: Dict, archetypes: List[Archetype]) -> Optional[Archetype]:
        """
        Algoritmo simple de matching:
        - Compara skills del usuario vs min_skills de cada arquetipo
        - Retorna arquetipo con mayor coincidencia
        """
        if not archetypes:
            return None
        
        best_archetype = None
        best_score = -1
        
        for archetype in archetypes:
            min_skills = archetype.min_skills or {}
            score = 0
            
            for skill, min_value in min_skills.items():
                user_value = skills.get(skill, 0)
                if user_value >= min_value:
                    score += user_value
            
            if score > best_score:
                best_score = score
                best_archetype = archetype
        
        return best_archetype
