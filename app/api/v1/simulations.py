"""
Simulations API
Core logic for creating and managing educational simulations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.simulations import (
    Simulation, SimulationModule, ModuleTask, 
    TaskResource, ModelAnswer
)
from app.schemas.simulations import (
    SimulationCreate, SimulationOut, SimulationList, SimulationUpdate
)

router = APIRouter()

# ============================
# HELPER FUNCTIONS
# ============================
def create_nested_structure(db: Session, simulation: Simulation, modules_data: list):
    """Recursively create modules, tasks, resources"""
    for mod_data in modules_data:
        tasks_data = mod_data.pop("tasks", [])
        
        # Create Module
        db_module = SimulationModule(**mod_data, simulation_id=simulation.id)
        db.add(db_module)
        db.commit()
        db.refresh(db_module)
        
        for task_data in tasks_data:
            resources_data = task_data.pop("resources", [])
            answer_data = task_data.pop("model_answer", None)
            
            # Create Task
            db_task = ModuleTask(**task_data, module_id=db_module.id)
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            
            # Create Resources
            for res_data in resources_data:
                db_res = TaskResource(**res_data, task_id=db_task.id)
                db.add(db_res)
            
            # Create Model Answer
            if answer_data:
                db_answer = ModelAnswer(**answer_data, task_id=db_task.id)
                db.add(db_answer)
        
        db.commit()

# ============================
# ENDPOINTS
# ============================

@router.post("", response_model=SimulationOut, status_code=201)
def create_simulation(sim_data: SimulationCreate, db: Session = Depends(get_db)):
    """
    Create a new simulation.
    Can handle nested creation (Modules -> Tasks) if provided.
    """
    # Check slug uniqueness
    if db.query(Simulation).filter(Simulation.slug == sim_data.slug).first():
        raise HTTPException(status_code=400, detail="Slug already exists")

    # Extract nested data
    sim_dict = sim_data.model_dump()
    modules_data = sim_dict.pop("modules", [])
    
    # Create base simulation
    db_sim = Simulation(**sim_dict)
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)
    
    # Handle nested creation
    if modules_data:
        create_nested_structure(db, db_sim, modules_data)
        db.refresh(db_sim)
        
    return db_sim

@router.get("", response_model=List[SimulationList])
def list_simulations(
    company_id: int = None,
    category_id: int = None,
    state: str = None,
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """List simulations with filters"""
    query = db.query(Simulation)
    
    if company_id:
        query = query.filter(Simulation.company_id == company_id)
    if category_id:
        query = query.filter(Simulation.category_id == category_id)
    if state:
        query = query.filter(Simulation.state == state)
        
    return query.offset(skip).limit(limit).all()

@router.get("/{id_or_slug}", response_model=SimulationOut)
def get_simulation(id_or_slug: str, db: Session = Depends(get_db)):
    """Get full simulation details by ID or Slug"""
    query = db.query(Simulation)
    
    if id_or_slug.isdigit():
        sim = query.filter(Simulation.id == int(id_or_slug)).first()
    else:
        sim = query.filter(Simulation.slug == id_or_slug).first()
        
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
        
    return sim

@router.patch("/{id}", response_model=SimulationOut)
def update_simulation(id: int, update_data: SimulationUpdate, db: Session = Depends(get_db)):
    """Update simulation basic info"""
    sim = db.query(Simulation).filter(Simulation.id == id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(sim, key, value)
        
    db.commit()
    db.refresh(sim)
    return sim

@router.delete("/{id}", status_code=204)
def delete_simulation(id: int, db: Session = Depends(get_db)):
    """Delete simulation and all its content (modules, tasks)"""
    sim = db.query(Simulation).filter(Simulation.id == id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
        
    db.delete(sim)
    db.commit()
    return None
