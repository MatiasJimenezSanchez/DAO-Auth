import sys
import os
import logging
from sqlalchemy.exc import IntegrityError

# Asegurar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.catalog import Region, Province, City, ContentCategory, Industry, SkillCatalog
from app.models.empresa import Empresa
from app.models.gamification import VirtualMentor
from app.models.oracle import Archetype, OracleQuestion, QuestionOption
from app.models.simulations import Simulation, SimulationModule, ModuleTask, TaskResource, ModelAnswer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_or_create(db: Session, model, unique_field: str, unique_value: str, **kwargs):
    """
    Función súper robusta para obtener o crear registros.
    Maneja bloqueos e IntegrityErrors limpiamente.
    """
    filter_kwargs = {unique_field: unique_value}
    instance = db.query(model).filter_by(**filter_kwargs).first()
    
    if instance:
        return instance

    instance = model(**filter_kwargs, **kwargs)
    try:
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"⚠️ Colisión detectada para {model.__name__} ({unique_value}). Recuperando existente...")
        if hasattr(model, 'name') and 'name' in kwargs:
             return db.query(model).filter_by(name=kwargs['name']).first()
        elif hasattr(model, 'slug') and 'slug' in kwargs:
             return db.query(model).filter_by(slug=kwargs['slug']).first()
        else:
            raise e

def seed_master(db: Session):
    logger.info("==================================================")
    logger.info("🌱 INICIANDO MEGA-SEEDER MAESTRO DE DELPHOS 🌱")
    logger.info("==================================================")

    # 1. CATÁLOGOS BASE
    region = get_or_create(db, Region, "name", "Sierra", code="SI", is_active=True)
    prov = get_or_create(db, Province, "name", "Pichincha", region_id=region.id, code="PI", is_active=True)
    city = get_or_create(db, City, "name", "Quito", province_id=prov.id, is_capital=True, is_active=True)
    
    ind = get_or_create(db, Industry, "slug", "technology", name="Technology", is_active=True)
    cat = get_or_create(db, ContentCategory, "slug", "software-engineering", name="Software Engineering", description="Desarrollo de Software", is_active=True)
    
    # CORRECCIÓN DE SKILLCATALOG (Campos exactos del modelo)
    skill = get_or_create(db, SkillCatalog, "slug", "python-dev", 
                          name="Python Development", 
                          category="technical", 
                          market_demand="high", 
                          trend="growing", 
                          avg_salary_impact=1.5, 
                          is_active=True)

    logger.info("✅ Catálogos base creados.")

    # 2. EMPRESA Y MENTOR IA
    empresa = get_or_create(db, Empresa, "slug", "tech-global-corp", 
                            nombre_empresa="Tech Global Corp", 
                            tipo_empresa="real_internacional", 
                            industria=ind.name, 
                            pais="Ecuador", ciudad=city.name)
    
    mentor = get_or_create(db, VirtualMentor, "nombre", "Alan Turing (AI)", 
                           empresa_id=empresa.id, 
                           titulo="Arquitecto Cloud & Mentor", 
                           personalidad="técnico", 
                           prompt_sistema="Eres Alan, un mentor estricto pero justo que enseña Python y Arquitectura.", 
                           modelo_ia="gpt-4o", 
                           is_active=True)
    
    logger.info(f"✅ Empresa '{empresa.nombre_empresa}' y Mentor IA listos.")

    # 3. ORÁCULO
    arch = get_or_create(db, Archetype, "slug", "hacker-analitico", 
                         nombre="Hacker Analítico", 
                         descripcion="Te encanta desarmar sistemas para entender cómo funcionan.", 
                         min_skills={"python-dev": 50}, 
                         esta_activo=True)
    
    q1 = get_or_create(db, OracleQuestion, "pregunta", "¿Qué haces si el servidor se cae un viernes a las 5PM?", 
                       categoria="Resolución de Problemas", orden=1, esta_activo=True)
    
    get_or_create(db, QuestionOption, "texto_opcion", "Abro los logs inmediatamente y busco el error.", 
                  pregunta_id=q1.id, skill_mapping={"python-dev": 20}, orden=1)
    get_or_create(db, QuestionOption, "texto_opcion", "Lloro y apago la computadora.", 
                  pregunta_id=q1.id, skill_mapping={"python-dev": -10}, orden=2)

    logger.info("✅ Oráculo Vocacional configurado.")

    # 4. SIMULACIÓN COMPLEJA (El Core)
    sim = get_or_create(db, Simulation, "slug", "arquitectura-backend-avanzada",
                        title="Arquitectura Backend Avanzada",
                        short_description="Construye APIs que soporten 1 millón de requests.",
                        full_description="Aprenderás sobre concurrencia, bases de datos y despliegues.",
                        company_id=empresa.id,
                        category_id=cat.id,
                        difficulty_level="advanced",
                        estimated_hours=10.0,
                        state="published",
                        is_premium=True)

    mod1 = get_or_create(db, SimulationModule, "title", "Módulo 1: Concurrencia",
                         simulation_id=sim.id, description="Entendiendo Asyncio en FastAPI.", order=1, estimated_hours=3.0)

    t1 = get_or_create(db, ModuleTask, "title", "Video Intro: The Event Loop",
                       module_id=mod1.id, description="Mira la explicación del CTO.", order=1, task_type="video", estimated_minutes=15)
    
    t2 = get_or_create(db, ModuleTask, "title", "Laboratorio: Async vs Sync",
                       module_id=mod1.id, description="Sube tu código comparando tiempos de respuesta.", order=2, task_type="submission", estimated_minutes=60)

    get_or_create(db, TaskResource, "name", "Documentación FastAPI",
                  task_id=t2.id, url="https://fastapi.tiangolo.com/async/", resource_type="link")
    
    get_or_create(db, ModelAnswer, "description", "El código debe usar `await` en llamadas I/O.",
                  task_id=t2.id, key_learnings=["Nunca bloquees el Event Loop.", "Usa librerías async para DB."])

    logger.info(f"✅ Simulación '{sim.title}' inyectada.")
    logger.info("==================================================")
    logger.info("🚀 TODO EL ECOSISTEMA HA SIDO SEMBRADO CON ÉXITO")
    logger.info("==================================================")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_master(db)
    except Exception as e:
        logger.error(f"❌ Error crítico en el seeder: {e}")
    finally:
        db.close()
