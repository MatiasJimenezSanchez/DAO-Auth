from typing import Dict, List
from sqlalchemy.orm import Session
from app.repositories.company_repository import CompanyRepository


class SimulationService:
    """
    Servicio para cálculos de simulaciones y proyecciones de negocio
    """
    
    def __init__(self, db: Session):
        self.company_repo = CompanyRepository(db)
    
    def calculate_viability(self, company_id: int) -> Dict:
        """Calcula viabilidad basada en métricas de la empresa"""
        company = self.company_repo.get(company_id)
        if not company:
            return {"error": "Empresa no encontrada"}
        
        viability_score = 0
        max_score = 100
        factors = []
        
        # Factor 1: Calificación (30 pts)
        rating = float(company.calificacion_promedio) if company.calificacion_promedio else 0.0
        r_score = (rating / 5.0) * 30
        viability_score += r_score
        factors.append({"factor": "rating", "value": rating, "score": round(r_score, 1)})
        
        # Factor 2: Actividad (25 pts)
        sim_score = min(25, (company.total_simulaciones / 50) * 25)
        viability_score += sim_score
        factors.append({"factor": "simulations", "value": company.total_simulaciones, "score": round(sim_score, 1)})
        
        # Factor 3: Partnership (15 pts)
        if company.es_partner_activo:
            viability_score += 15
            factors.append({"factor": "partner", "value": True, "score": 15})
            
        # Factor 4: Verificación (10 pts)
        if company.verificado:
            viability_score += 10
            factors.append({"factor": "verified", "value": True, "score": 10})
            
        return {
            "company_id": company_id,
            "company_name": company.nombre_empresa,
            "viability_score": round(viability_score, 2),
            "max_score": max_score,
            "factors": factors,
            "classification": self._classify_viability(viability_score),
            "recommendations": self._generate_recommendations(company, viability_score)
        }
    
    def _classify_viability(self, score: float) -> str:
        if score >= 80: return "Excelente"
        elif score >= 60: return "Buena"
        elif score >= 40: return "Regular"
        else: return "Crítica"

    def _generate_recommendations(self, company, score: float) -> List[str]:
        recs = []
        if not company.verificado: recs.append("Verificar empresa")
        if not company.es_partner_activo: recs.append("Activar Partnership")
        if company.total_simulaciones < 10: recs.append("Crear más simulaciones")
        return recs
    
    def project_growth(self, company_id: int, months: int = 6) -> Dict:
        """Proyección de crecimiento de usuarios"""
        company = self.company_repo.get(company_id)
        if not company:
            return {"error": "Empresa no encontrada"}
        
        growth_rate = 0.05 if company.es_partner_activo else 0.02
        current = company.total_usuarios_inscritos
        projected = current * ((1 + growth_rate) ** months)
        
        return {
            "company_id": company_id,
            "months": months,
            "current_users": current,
            "projected_users": int(projected),
            "growth_rate": f"{growth_rate*100}%"
        }
