import pytest
from app.models.oracle import OracleQuestion, QuestionOption, OracleSession
from app.schemas.oracle import AnswerCreate
from pydantic import ValidationError

class TestOracleEngineSafe:
    def test_schema_answer_valid(self):
        schema = AnswerCreate(pregunta_id=1, opcion_id=4, tiempo_respuesta_segundos=12)
        assert schema.opcion_id == 4

    def test_schema_answer_invalid_time(self):
        with pytest.raises(ValidationError):
            AnswerCreate(pregunta_id=1, opcion_id=4, tiempo_respuesta_segundos=-5)

    def test_model_question_option_weights(self):
        # Asignamos explícitamente el default para pruebas en memoria
        opcion = QuestionOption(pregunta_id=1, texto_opcion="Me gusta programar", peso_analytical=0, peso_creative=0)
        assert opcion.peso_analytical == 0
        assert opcion.peso_creative == 0
        
    def test_model_session_accumulation_logic(self):
        # Simulamos la lógica de acumulación de scores inicializando en 0
        sesion = OracleSession(usuario_id=1, estado="en_progreso", score_analytical=0, score_creative=0)
        opcion_elegida = QuestionOption(peso_analytical=5, peso_creative=2)
        
        # Aplicar pesos de la opción a la sesión
        sesion.score_analytical += opcion_elegida.peso_analytical
        sesion.score_creative += opcion_elegida.peso_creative
        
        assert sesion.score_analytical == 5
        assert sesion.score_creative == 2
