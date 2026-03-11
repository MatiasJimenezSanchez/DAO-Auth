"""
app/api/v1/progress.py — Rutas de progreso de usuario (Fase 15)
Delega toda la lógica a ProgressService.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.progress import UserSimulationOut, TaskSubmission
from app.services.progress_service import ProgressService

router = APIRouter()


@router.get("/users/me/simulations", response_model=List[UserSimulationOut])
def get_my_simulations(
    estado: Optional[str] = Query(None, description="Filtrar por estado: inscrito, en_progreso, completado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista las simulaciones en las que el usuario autenticado está inscrito."""
    service = ProgressService(db)
    return service.list_user_simulations(current_user.id, estado, skip, limit)


@router.post("/tasks/submit", response_model=dict, status_code=status.HTTP_201_CREATED)
def submit_task(
    submission: TaskSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Registra la respuesta de una tarea para el usuario autenticado."""
    service = ProgressService(db)
    user_task = service.submit_task(
        current_user.id,
        submission.task_id,
        submission.respuesta_texto,
    )
    return {"status": "submitted", "task_id": user_task.task_id, "estado": user_task.estado}
