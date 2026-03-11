"""
app/api/v1/simulations.py — Rutas de simulaciones (Fase 15)
Endpoints públicos (list/get) + autenticados (enroll).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.simulations import SimulationCreate, SimulationUpdate, SimulationOut
from app.schemas.progress import UserSimulationOut, EnrollmentResponse
from app.services.simulation_service import SimulationService
from app.services.progress_service import ProgressService

router = APIRouter()


# ---------------------------------------------------------------------------
# PÚBLICO — listado y detalle
# ---------------------------------------------------------------------------

@router.get("", response_model=List[SimulationOut])
def list_simulations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    company_id: Optional[int] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista simulaciones. Sin filtros devuelve todas; usa state=published para el catálogo público."""
    service = SimulationService(db)
    return service.list_simulations(skip, limit, company_id, state)


@router.get("/{sim_id}", response_model=SimulationOut)
def get_simulation(sim_id: int, db: Session = Depends(get_db)):
    service = SimulationService(db)
    sim = service.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulación no encontrada")
    return sim


# ---------------------------------------------------------------------------
# ADMIN — crear / actualizar / eliminar
# ---------------------------------------------------------------------------

@router.post("", response_model=SimulationOut, status_code=status.HTTP_201_CREATED)
def create_simulation(
    sim_data: SimulationCreate,
    db: Session = Depends(get_db),
):
    service = SimulationService(db)
    return service.create_simulation(sim_data.model_dump())


@router.put("/{sim_id}", response_model=SimulationOut)
def update_simulation(
    sim_id: int,
    sim_data: SimulationUpdate,
    db: Session = Depends(get_db),
):
    service = SimulationService(db)
    return service.update_simulation(sim_id, sim_data.model_dump(exclude_unset=True))


@router.delete("/{sim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_simulation(sim_id: int, db: Session = Depends(get_db)):
    SimulationService(db).delete_simulation(sim_id)


# ---------------------------------------------------------------------------
# AUTENTICADO — inscripción
# ---------------------------------------------------------------------------

@router.post(
    "/{sim_id}/inscribir",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def enroll_current_user(
    sim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Inscribe al usuario autenticado en la simulación.
    Crea un registro en simulaciones_usuario.
    """
    progress_svc = ProgressService(db)
    sim_svc = SimulationService(db)

    enrollment = progress_svc.enroll_user(sim_id, current_user.id)

    # Spots actualizados tras commit
    sim = sim_svc.get_simulation(sim_id)

    return EnrollmentResponse(
        status="enrolled",
        enrollment=enrollment,
        spots_left=sim.available_spots,
    )
