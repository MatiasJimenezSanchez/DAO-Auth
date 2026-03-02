import pytest
from pydantic import ValidationError
from app.schemas.user import UserUpdate

class TestAIFeaturesValidation:
    def test_ai_scores_within_limits_accepted(self):
        # 1. Rango válido (0 a 100) debe pasar
        update_data = UserUpdate(
            analytical_score=85, 
            creative_score=100, 
            social_score=0
        )
        assert update_data.analytical_score == 85
        assert update_data.creative_score == 100
        assert update_data.social_score == 0

    def test_ai_score_above_100_rejected(self):
        # 2. Score mayor a 100 debe crashear Pydantic
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(analytical_score=101)
        assert "analytical_score" in str(exc_info.value)
        assert "less than or equal to 100" in str(exc_info.value) or "le" in str(exc_info.value)

    def test_ai_score_negative_rejected(self):
        # 3. Score negativo debe crashear Pydantic
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(creative_score=-5)
        assert "creative_score" in str(exc_info.value)
        assert "greater than or equal to 0" in str(exc_info.value) or "ge" in str(exc_info.value)
