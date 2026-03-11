"""
app/services/b2b_service.py — Servicio de Analítica para Empresas (Fase 17)
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from fastapi import HTTPException, status

from app.models.empresa import Empresa
from app.models.simulations import Simulation
from app.models.progress import UserSimulation
from app.models.user import User

class B2BService:
    def __init__(self, db: Session):
        self.db = db

    def get_company_dashboard(self, company_id: int) -> dict:
        """Calcula todas las métricas clave para el dashboard de una empresa."""
        
        # 1. Verificar existencia de la empresa
        company = self.db.query(Empresa).filter(Empresa.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # 2. Obtener todas las simulaciones de la empresa
        simulations = self.db.query(Simulation).filter(Simulation.company_id == company_id).all()
        sim_ids = [s.id for s in simulations]
        
        total_simulations = len(simulations)
        
        if total_simulations == 0:
            return {
                "company_id": company_id,
                "total_simulations": 0,
                "total_students_enrolled": 0,
                "overall_completion_rate": 0.0,
                "simulations_stats": [],
                "recent_enrollments": []
            }

        # 3. Métricas Globales de Estudiantes
        enrollments = self.db.query(UserSimulation).filter(UserSimulation.simulation_id.in_(sim_ids)).all()
        total_students = len(enrollments)
        
        if total_students > 0:
            overall_rate = sum(float(e.porcentaje_completado) for e in enrollments) / total_students
        else:
            overall_rate = 0.0

        # 4. Estadísticas por Simulación
        sim_stats = []
        for sim in simulations:
            sim_enrollments = [e for e in enrollments if e.simulation_id == sim.id]
            total_enr = len(sim_enrollments)
            active = len([e for e in sim_enrollments if e.estado in ("inscrito", "en_progreso")])
            completed = len([e for e in sim_enrollments if e.estado == "completado"])
            avg_comp = sum(float(e.porcentaje_completado) for e in sim_enrollments) / total_enr if total_enr > 0 else 0.0
            
            sim_stats.append({
                "simulation_id": sim.id,
                "title": sim.title,
                "total_enrollments": total_enr,
                "active_enrollments": active,
                "completed_enrollments": completed,
                "avg_completion_percentage": round(avg_comp, 2)
            })

        # 5. Últimos 5 inscritos
        recent = (
            self.db.query(UserSimulation, User, Simulation)
            .join(User, UserSimulation.user_id == User.id)
            .join(Simulation, UserSimulation.simulation_id == Simulation.id)
            .filter(UserSimulation.simulation_id.in_(sim_ids))
            .order_by(UserSimulation.inscrito_en.desc())
            .limit(5)
            .all()
        )
        
        recent_list = []
        for us_sim, usr, sim in recent:
            recent_list.append({
                "user_id": usr.id,
                "full_name": usr.full_name,
                "email": usr.email,
                "simulation_id": sim.id,
                "simulation_title": sim.title,
                "estado": us_sim.estado,
                "porcentaje_completado": us_sim.porcentaje_completado,
                "tiempo_total_minutos": us_sim.tiempo_total_minutos
            })

        return {
            "company_id": company_id,
            "total_simulations": total_simulations,
            "total_students_enrolled": total_students,
            "overall_completion_rate": round(overall_rate, 2),
            "simulations_stats": sim_stats,
            "recent_enrollments": recent_list
        }
