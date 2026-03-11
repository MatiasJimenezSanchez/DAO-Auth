"""
app/services/progress_service.py — Lógica de progreso de usuario (Fase 15)

Responsabilidades:
  - Inscribir usuario en simulación (crea UserSimulation)
  - Listar simulaciones del usuario
  - Actualizar progreso de tareas
  - Verificar existencia de padres antes de insertar (programación defensiva)
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.progress import UserSimulation, UserTask
from app.models.simulations import Simulation
from app.models.user import User


class ProgressService:
    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # ENROLL — POST /api/v1/simulaciones/{id}/inscribir
    # -------------------------------------------------------------------------
    def enroll_user(self, simulation_id: int, user_id: int) -> UserSimulation:
        """
        Inscribe al usuario en una simulación.
        - Verifica que la simulación exista y esté publicada
        - Verifica que el usuario exista
        - Verifica que no esté ya inscrito
        - Verifica disponibilidad de cupos
        - Decrementa available_spots si aplica
        """
        # 1. Verificar simulación
        sim = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not sim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Simulación {simulation_id} no encontrada",
            )

        if sim.state not in ("published", "activa"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La simulación debe estar publicada para inscribirse",
            )

        # 2. Verificar usuario
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )

        # 3. Verificar inscripción duplicada
        existing = (
            self.db.query(UserSimulation)
            .filter(
                UserSimulation.user_id == user_id,
                UserSimulation.simulation_id == simulation_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya está inscrito en esta simulación",
            )

        # 4. Verificar cupos
        if sim.total_spots > 0 and sim.available_spots <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay cupos disponibles",
            )

        # 5. Crear inscripción
        enrollment = UserSimulation(
            user_id=user_id,
            simulation_id=simulation_id,
            estado="inscrito",
        )
        self.db.add(enrollment)

        # 6. Decrementar cupos si aplica
        if sim.total_spots > 0:
            sim.available_spots -= 1

        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    # -------------------------------------------------------------------------
    # LIST USER SIMULATIONS — GET /api/v1/users/me/simulations
    # -------------------------------------------------------------------------
    def list_user_simulations(
        self,
        user_id: int,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[UserSimulation]:
        """Lista las simulaciones en las que el usuario está inscrito."""
        query = self.db.query(UserSimulation).filter(
            UserSimulation.user_id == user_id
        )
        if estado:
            query = query.filter(UserSimulation.estado == estado)
        return query.offset(skip).limit(limit).all()

    # -------------------------------------------------------------------------
    # GET SINGLE ENROLLMENT
    # -------------------------------------------------------------------------
    def get_enrollment(self, user_id: int, simulation_id: int) -> Optional[UserSimulation]:
        return (
            self.db.query(UserSimulation)
            .filter(
                UserSimulation.user_id == user_id,
                UserSimulation.simulation_id == simulation_id,
            )
            .first()
        )

    # -------------------------------------------------------------------------
    # SUBMIT TASK
    # -------------------------------------------------------------------------
    def submit_task(self, user_id: int, task_id: int, respuesta_texto: Optional[str]) -> UserTask:
        """Registra o actualiza la respuesta de una tarea."""
        from app.models.simulations import ModuleTask

        # Verificar que la tarea exista
        task = self.db.query(ModuleTask).filter(ModuleTask.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea {task_id} no encontrada",
            )

        existing = (
            self.db.query(UserTask)
            .filter(UserTask.user_id == user_id, UserTask.task_id == task_id)
            .first()
        )

        if existing:
            existing.respuesta_texto = respuesta_texto
            existing.estado = "completada"
            existing.intentos += 1
            self.db.commit()
            self.db.refresh(existing)
            return existing

        user_task = UserTask(
            user_id=user_id,
            task_id=task_id,
            respuesta_texto=respuesta_texto,
            estado="completada",
        )
        self.db.add(user_task)
        self.db.commit()
        self.db.refresh(user_task)
        return user_task
