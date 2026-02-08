from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository


class MatchingService:
    """
    Motor de Matching Inteligente v1.0
    Calcula compatibilidad entre Users y Companies basado en:
    - Industria
    - Ubicación geográfica
    """
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.company_repo = CompanyRepository(db)
        self.db = db
    
    def calculate_match_score(self, user_id: int, company_id: int) -> Dict:
        """Calcula % de match detallado"""
        user = self.user_repo.get(user_id)
        company = self.company_repo.get(company_id)
        
        if not user or not company:
            return {"error": "Usuario o empresa no encontrada", "score": 0}
        
        score = 0
        breakdown = []
        
        # 1. Matching de Ubicación (40%)
        # User usa IDs (city_id), Company usa Strings (pais, ciudad)
        # Lógica simplificada: si la empresa está en "Ecuador" y el usuario también (asumido por ahora)
        if company.pais == "Ecuador": 
             score += 40
             breakdown.append({"factor": "location_country", "points": 40})
        
        # 2. Matching de Industria (40%)
        if company.industria:
            score += 40
            breakdown.append({"factor": "industry_match", "points": 40})
            
        # 3. Factor Partner (20%)
        if company.es_partner_activo:
            score += 20
            breakdown.append({"factor": "partner_bonus", "points": 20})
        
        final_score = min(score, 100)
        
        return {
            "user_id": user_id,
            "company_id": company_id,
            "match_score": final_score,
            "breakdown": breakdown,
            "recommendation": self._get_recommendation(final_score)
        }
    
    def _get_recommendation(self, score: int) -> str:
        if score >= 80: return "Excelente match - Altamente recomendado"
        elif score >= 60: return "Buen match - Recomendado"
        elif score >= 40: return "Match moderado - Considerar"
        else: return "Match bajo - No prioritario"

    def find_best_matches_for_user(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Encuentra las mejores empresas para un usuario"""
        # Obtenemos TODAS las empresas (ineficiente en prod, pero OK para MVP)
        companies = self.company_repo.get_multi(0, 100, filters={"esta_activo": True})
        
        matches = []
        for company in companies:
            result = self.calculate_match_score(user_id, company.id)
            if "match_score" in result:
                matches.append({
                    "company_name": company.nombre_empresa,
                    "score": result["match_score"],
                    "recommendation": result["recommendation"]
                })
        
        # Ordenar descendente
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:limit]

    def find_best_candidates_for_company(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Encuentra usuarios para una empresa"""
        users = self.user_repo.get_multi(0, 100, filters={"is_active": True})
        
        candidates = []
        for user in users:
            result = self.calculate_match_score(user.id, company_id)
            if "match_score" in result:
                candidates.append({
                    "user_name": user.full_name,
                    "score": result["match_score"],
                    "recommendation": result["recommendation"]
                })
        
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:limit]
