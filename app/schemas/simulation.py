"""
app/schemas/simulation.py — Re-export desde simulations.py (canónico)
Mantener para compatibilidad con imports existentes en tests legacy.
"""
from app.schemas.simulations import (  # noqa: F401
    SimulationBase,
    SimulationCreate,
    SimulationUpdate,
    SimulationOut,
    ModuleBase,
    ModuleCreate,
    ModuleUpdate,
    ModuleOut,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskOut,
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceOut,
)
