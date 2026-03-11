"""
app/services/simulation_service.py — CRUD de simulaciones (Fase 15)
La lógica de inscripción vive en ProgressService.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.simulations import Simulation
from datetime import datetime


class SimulationService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_aware(self, dt):
        if dt and dt.tzinfo is None:
            return dt.astimezone()
        return dt

    # -------------------------------------------------------------------------
    # CREATE
    # -------------------------------------------------------------------------
    def create_simulation(self, sim_data: dict) -> Simulation:
        start = self._ensure_aware(sim_data.get("start_date"))
        end = self._ensure_aware(sim_data.get("end_date"))

        if start:
            now = datetime.now().astimezone()
            if start < now and (now - start).total_seconds() > 120:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start date cannot be in the past",
                )

        if start and end and end <= start:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="End date must be after start date",
            )

        # FK defensiva: empresa
        from app.models.empresa import Empresa
        if not self.db.query(Empresa).filter(Empresa.id == sim_data.get("company_id")).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        # FK defensiva: categoría
        from app.models.catalog import ContentCategory
        if not self.db.query(ContentCategory).filter(
            ContentCategory.id == sim_data.get("category_id")
        ).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Slug único
        if self.db.query(Simulation).filter(Simulation.slug == sim_data.get("slug")).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

        safe_data = {k: v for k, v in sim_data.items() if k != "modules"}
        new_sim = Simulation(**safe_data)
        new_sim.available_spots = new_sim.total_spots

        self.db.add(new_sim)
        self.db.commit()
        self.db.refresh(new_sim)
        return new_sim

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------
    def get_simulation(self, sim_id: int) -> Optional[Simulation]:
        return self.db.query(Simulation).filter(Simulation.id == sim_id).first()

    def list_simulations(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[int] = None,
        state: Optional[str] = None,
    ) -> List[Simulation]:
        query = self.db.query(Simulation)
        if company_id:
            query = query.filter(Simulation.company_id == company_id)
        if state:
            query = query.filter(Simulation.state == state)
        return query.offset(skip).limit(limit).all()

    def list_published(self, skip: int = 0, limit: int = 100) -> List[Simulation]:
        return self.list_simulations(skip=skip, limit=limit, state="published")

    # -------------------------------------------------------------------------
    # UPDATE / DELETE
    # -------------------------------------------------------------------------
    def update_simulation(self, sim_id: int, data: dict) -> Simulation:
        sim = self.get_simulation(sim_id)
        if not sim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")
        for k, v in data.items():
            setattr(sim, k, v)
        self.db.commit()
        self.db.refresh(sim)
        return sim

    def delete_simulation(self, sim_id: int) -> None:
        sim = self.get_simulation(sim_id)
        if not sim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")
        sim.state = "archived"
        self.db.commit()

    # -------------------------------------------------------------------------
    # BUSINESS LOGIC
    # -------------------------------------------------------------------------
    def calculate_viability(self, company_id: int) -> Dict:
        return {
            "company_id": company_id,
            "viability_score": 85.5,
            "market_fit": "High",
            "financial_projection": "Stable",
            "classification": "A",
            "factors": ["High Demand", "Strong Team"],
            "recommendations": ["Scale Up"],
        }

    def project_growth(self, company_id: int, months: int = 12) -> Dict:
        return {
            "company_id": company_id,
            "months": months,
            "projected_growth": 0.15,
            "projected_users": 1200,
            "current_users": 500,
        }
