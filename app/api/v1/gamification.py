"""
app/api/v1/gamification.py — Endpoints de Gamificación (Fase 16)

Endpoints:
  POST /gamification/award-xp          — Otorgar XP (protegido, uso interno/admin)
  GET  /gamification/leaderboard       — Ranking público por XP
  GET  /users/me/achievements          — Logros del usuario autenticado
  GET  /gamification/xp-history        — Historial XP del usuario autenticado
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.gamification import (
    AwardXPRequest,
    AwardXPResponse,
    LeaderboardResponse,
    UserAchievementOut,
    XPTransactionOut,
)
from app.services.gamification_service import GamificationService

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /gamification/award-xp
# ---------------------------------------------------------------------------

@router.post(
    "/award-xp",
    response_model=AwardXPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Otorgar XP a un usuario",
)
def award_xp(
    body: AwardXPRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Otorga XP a un usuario y calcula subida de nivel automáticamente.
    Requiere autenticación. En producción se limitaría a rol admin/sistema.
    """
    service = GamificationService(db)
    result = service.award_xp(
        user_id=body.user_id,
        cantidad_xp=body.cantidad_xp,
        tipo_fuente=body.tipo_fuente,
        descripcion=body.descripcion,
        fuente_id=body.fuente_id,
    )
    return result


# ---------------------------------------------------------------------------
# GET /gamification/leaderboard
# ---------------------------------------------------------------------------

@router.get(
    "/leaderboard",
    response_model=LeaderboardResponse,
    summary="Ranking de usuarios por XP",
)
def get_leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Devuelve el ranking de usuarios ordenados por XP total descendente.
    Endpoint público — no requiere autenticación.
    """
    service = GamificationService(db)
    return service.get_leaderboard(skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# GET /users/me/achievements  (registrado en este router para evitar
# conflicto con el prefix /gamification — se monta en /api/v1)
# ---------------------------------------------------------------------------

@router.get(
    "/me/achievements",
    response_model=List[UserAchievementOut],
    summary="Logros del usuario autenticado",
)
def get_my_achievements(
    solo_desbloqueados: bool = Query(True, description="Si True, solo muestra logros desbloqueados"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista los logros del usuario autenticado."""
    service = GamificationService(db)
    return service.get_user_achievements(current_user.id, solo_desbloqueados)


# ---------------------------------------------------------------------------
# GET /gamification/xp-history
# ---------------------------------------------------------------------------

@router.get(
    "/xp-history",
    response_model=List[XPTransactionOut],
    summary="Historial de XP del usuario autenticado",
)
def get_xp_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Devuelve el historial de transacciones XP del usuario autenticado."""
    service = GamificationService(db)
    return service.get_xp_history(current_user.id, limit=limit)
