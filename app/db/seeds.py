"""
Seed Data Script
Pobla la base de datos con información inicial:
- Catálogos Geográficos (Ecuador)
- Industrias y Categorías
- Habilidades
"""
import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.catalog import (
    Region, Province, City, 
    Industry, ContentCategory, SkillCatalog
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_geography(db: Session):
    logger.info("--- Sembrando Geografía (Ecuador) ---")
    
    # 1. REGIONES
    regiones_data = [
        {"name": "Costa", "code": "COS", "map_color": "#FFD700"},
        {"name": "Sierra", "code": "SIE", "map_color": "#8B4513"},
        {"name": "Amazonía", "code": "AMA", "map_color": "#228B22"},
        {"name": "Insular", "code": "INS", "map_color": "#00BFFF"},
    ]
    
    regiones_map = {}
    
    for r_data in regiones_data:
        region = db.query(Region).filter(Region.code == r_data["code"]).first()
        if not region:
            region = Region(**r_data)
            db.add(region)
            db.commit()
            db.refresh(region)
            logger.info(f"Region creada: {region.name}")
        regiones_map[region.code] = region.id

    # 2. PROVINCIAS (Ejemplo: Principales)
    provincias_data = [
        # Sierra
        {"name": "Pichincha", "code": "PIC", "region_code": "SIE"},
        {"name": "Azuay", "code": "AZU", "region_code": "SIE"},
        {"name": "Loja", "code": "LOJ", "region_code": "SIE"},
        # Costa
        {"name": "Guayas", "code": "GUA", "region_code": "COS"},
        {"name": "Manabí", "code": "MAN", "region_code": "COS"},
        {"name": "El Oro", "code": "ORO", "region_code": "COS"},
    ]

    provincias_map = {}

    for p_data in provincias_data:
        p_code = p_data.pop("code")
        reg_code = p_data.pop("region_code")
        
        provincia = db.query(Province).filter(Province.code == p_code).first()
        if not provincia:
            provincia = Province(
                code=p_code,
                region_id=regiones_map[reg_code],
                **p_data
            )
            db.add(provincia)
            db.commit()
            db.refresh(provincia)
            logger.info(f"Provincia creada: {provincia.name}")
        provincias_map[p_code] = provincia.id

    # 3. CIUDADES (Principales)
    ciudades_data = [
        {"name": "Quito", "prov_code": "PIC", "is_capital": True},
        {"name": "Guayaquil", "prov_code": "GUA", "is_capital": False},
        {"name": "Cuenca", "prov_code": "AZU", "is_capital": False},
        {"name": "Loja", "prov_code": "LOJ", "is_capital": False},
        {"name": "Manta", "prov_code": "MAN", "is_capital": False},
        {"name": "Machala", "prov_code": "ORO", "is_capital": False},
    ]

    for c_data in ciudades_data:
        prov_code = c_data.pop("prov_code")
        ciudad = db.query(City).filter(City.name == c_data["name"]).first()
        if not ciudad:
            ciudad = City(
                province_id=provincias_map[prov_code],
                **c_data
            )
            db.add(ciudad)
            db.commit()
            logger.info(f"Ciudad creada: {ciudad.name}")

def seed_industries(db: Session):
    logger.info("--- Sembrando Industrias ---")
    
    # Industrias Padre
    parents = [
        {"name": "Tecnología", "slug": "tecnologia", "icon": "laptop"},
        {"name": "Finanzas", "slug": "finanzas", "icon": "attach_money"},
        {"name": "Salud", "slug": "salud", "icon": "local_hospital"},
        {"name": "Ingeniería", "slug": "ingenieria", "icon": "engineering"},
    ]
    
    parents_map = {}
    
    for p in parents:
        ind = db.query(Industry).filter(Industry.slug == p["slug"]).first()
        if not ind:
            ind = Industry(**p, level=1)
            db.add(ind)
            db.commit()
            db.refresh(ind)
        parents_map[p["slug"]] = ind.id

    # Industrias Hijas (Sub-industrias)
    children = [
        {"name": "Desarrollo de Software", "slug": "software-dev", "parent": "tecnologia"},
        {"name": "Ciberseguridad", "slug": "cybersecurity", "parent": "tecnologia"},
        {"name": "Data Science", "slug": "data-science", "parent": "tecnologia"},
        {"name": "Banca de Inversión", "slug": "investment-banking", "parent": "finanzas"},
        {"name": "Fintech", "slug": "fintech", "parent": "finanzas"},
    ]

    for c in children:
        parent_slug = c.pop("parent")
        ind = db.query(Industry).filter(Industry.slug == c["slug"]).first()
        if not ind:
            ind = Industry(
                **c, 
                parent_industry_id=parents_map[parent_slug],
                level=2
            )
            db.add(ind)
            db.commit()

def seed_skills(db: Session):
    logger.info("--- Sembrando Skills ---")
    
    skills = [
        {"name": "Python", "slug": "python", "category": "technical", "demand": "high"},
        {"name": "React", "slug": "react", "category": "technical", "demand": "high"},
        {"name": "SQL", "slug": "sql", "category": "technical", "demand": "high"},
        {"name": "Liderazgo", "slug": "liderazgo", "category": "soft", "demand": "medium"},
        {"name": "Comunicación Efectiva", "slug": "comunicacion", "category": "soft", "demand": "high"},
        {"name": "Inglés B2", "slug": "ingles-b2", "category": "language", "demand": "high"},
    ]

    for s in skills:
        skill = db.query(SkillCatalog).filter(SkillCatalog.slug == s["slug"]).first()
        if not skill:
            skill = SkillCatalog(
                name=s["name"],
                slug=s["slug"],
                category=s["category"],
                market_demand=s["demand"]
            )
            db.add(skill)
            db.commit()
            logger.info(f"Skill creada: {skill.name}")

def main():
    db = SessionLocal()
    try:
        seed_geography(db)
        seed_industries(db)
        seed_skills(db)
        logger.info("✅ PROCESO DE SEMILLAS COMPLETADO EXITOSAMENTE")
    except Exception as e:
        logger.error(f"❌ Error sembrando datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
