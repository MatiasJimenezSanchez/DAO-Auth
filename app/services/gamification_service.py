"""
app/services/gamification_service.py — Motor de Gamificación (Fase 16)

Fórmula de niveles (estándar RPG):
  xp_umbral(nivel) = nivel^2 * 100
  Nivel 1 →  0 XP acumulados
  Nivel 2 →  100 XP acumulados
  Nivel 3 →  400 XP acumulados
  Nivel 4 →  900 XP acumulados
  Nivel N →  (N-1)^2 * 100 XP acumulados

Responsabilidades:
  - Otorgar XP y registrar transacción en transacciones_xp
  - Calcular y actualizar nivel del usuario automáticamente
  - Leaderboard ordenado por xp_total DESC
  - Listado de logros del usuario
"""
from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.gamification import (
    XPTransaction,
    TipoFuenteXPEnum,
    Achievement,
    UserAchievement,
)


# =============================================================================
# FUNCIONES PURAS DE CÁLCULO (testables sin DB)
# =============================================================================

def xp_para_nivel(nivel: int) -> int:
    """
    XP acumulado necesario para ALCANZAR el nivel dado.
    xp_para_nivel(1) = 0
    xp_para_nivel(2) = 100
    xp_para_nivel(3) = 400
    xp_para_nivel(n) = (n-1)^2 * 100
    """
    if nivel <= 1:
        return 0
    return (nivel - 1) ** 2 * 100


def calcular_nivel_desde_xp(xp_total: int) -> int:
    """
    Dado un total de XP, devuelve el nivel correspondiente.
    Busca el mayor nivel N tal que xp_para_nivel(N) <= xp_total.
    Nivel mínimo: 1. Sin techo definido (escala automáticamente).
    """
    nivel = 1
    while xp_para_nivel(nivel + 1) <= xp_total:
        nivel += 1
    return nivel


def xp_para_siguiente_nivel(xp_total: int) -> int:
    """XP adicional necesario para subir al siguiente nivel."""
    nivel_actual = calcular_nivel_desde_xp(xp_total)
    return xp_para_nivel(nivel_actual + 1) - xp_total


# =============================================================================
# SERVICIO
# =============================================================================

class GamificationService:
    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # AWARD XP — POST /gamification/award-xp
    # -------------------------------------------------------------------------
    def award_xp(
        self,
        user_id: int,
        cantidad_xp: int,
        tipo_fuente: str,
        descripcion: str,
        fuente_id: int | None = None,
    ) -> dict:
        """
        Otorga XP a un usuario.
        1. Verifica que el usuario exista (FK defensiva)
        2. Registra transacción en transacciones_xp
        3. Actualiza xp_total y level_current en users
        4. Devuelve info de nivel completa
        """
        # 1. Verificar usuario
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )

        if cantidad_xp <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cantidad_xp debe ser mayor que 0",
            )

        # 2. Capturar estado anterior
        xp_anterior = user.xp_total or 0
        nivel_anterior = user.level_current or 1

        # 3. Calcular nuevo estado
        xp_nuevo = xp_anterior + cantidad_xp
        nivel_nuevo = calcular_nivel_desde_xp(xp_nuevo)

        # 4. Registrar transacción
        try:
            tipo_enum = TipoFuenteXPEnum(tipo_fuente)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"tipo_fuente inválido: {tipo_fuente}",
            )

        transaction = XPTransaction(
            user_id=user_id,
            cantidad_xp=cantidad_xp,
            tipo_fuente=tipo_enum,
            fuente_id=fuente_id,
            descripcion=descripcion,
            xp_anterior=xp_anterior,
            xp_nuevo=xp_nuevo,
        )
        self.db.add(transaction)

        # 5. Actualizar usuario
        user.xp_total = xp_nuevo
        user.level_current = nivel_nuevo

        self.db.commit()
        self.db.refresh(transaction)
        self.db.refresh(user)

        return {
            "transaction": transaction,
            "xp_anterior": xp_anterior,
            "xp_nuevo": xp_nuevo,
            "nivel_anterior": nivel_anterior,
            "nivel_nuevo": nivel_nuevo,
            "subio_de_nivel": nivel_nuevo > nivel_anterior,
            "xp_para_siguiente_nivel": xp_para_siguiente_nivel(xp_nuevo),
        }

    # -------------------------------------------------------------------------
    # LEADERBOARD — GET /gamification/leaderboard
    # -------------------------------------------------------------------------
    def get_leaderboard(self, skip: int = 0, limit: int = 20) -> dict:
        """
        Lista usuarios ordenados por xp_total DESC.
        Devuelve total + lista con rank calculado.
        """
        total = self.db.query(User).filter(User.is_active == True).count()

        users = (
            self.db.query(User)
            .filter(User.is_active == True)
            .order_by(User.xp_total.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        entries = [
            {
                "rank": skip + idx + 1,
                "user_id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "xp_total": u.xp_total or 0,
                "level_current": u.level_current or 1,
                "avatar_url": u.avatar_url,
            }
            for idx, u in enumerate(users)
        ]

        return {"total": total, "entries": entries}

    # -------------------------------------------------------------------------
    # USER ACHIEVEMENTS — GET /users/me/achievements
    # -------------------------------------------------------------------------
    def get_user_achievements(
        self,
        user_id: int,
        solo_desbloqueados: bool = True,
    ) -> List[UserAchievement]:
        """Lista los logros del usuario."""
        # FK defensiva
        if not self.db.query(User).filter(User.id == user_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )

        query = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        )
        if solo_desbloqueados:
            query = query.filter(UserAchievement.desbloqueado == True)

        return query.all()

    # -------------------------------------------------------------------------
    # HELPERS INTERNOS
    # -------------------------------------------------------------------------
    def get_xp_history(self, user_id: int, limit: int = 50) -> List[XPTransaction]:
        """Historial de transacciones XP de un usuario."""
        if not self.db.query(User).filter(User.id == user_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )
        return (
            self.db.query(XPTransaction)
            .filter(XPTransaction.user_id == user_id)
            .order_by(XPTransaction.created_at.desc(), XPTransaction.id.desc())
            .limit(limit)
            .all()
        )
