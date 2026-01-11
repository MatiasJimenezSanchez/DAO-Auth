# app/db/seeds.py
"""Seed script to populate regions, provinces and cities (Ecuador example).
Run with: python -m app.db.seeds or import and call `run()` from scripts.
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.catalog import Region, Province, City

DATA = [
    {
        "region": {"name": "Costa", "code": "COS"},
        "provinces": [
            {"name": "Guayas", "code": "09", "cities": ["Guayaquil", "Milagro"]},
            {"name": "El Oro", "code": "07", "cities": ["Machala"]},
        ],
    },
    {
        "region": {"name": "Sierra", "code": "SIE"},
        "provinces": [
            {"name": "Pichincha", "code": "17", "cities": ["Quito"]},
            {"name": "Azuay", "code": "01", "cities": ["Cuenca"]},
        ],
    },
]


def run():
    db: Session = SessionLocal()
    try:
        for entry in DATA:
            r = Region(code=entry["region"]["code"], name=entry["region"]["name"], is_active=True)
            db.add(r)
            db.flush()
            for p in entry["provinces"]:
                prov = Province(code=p["code"], name=p["name"], region_id=r.id, is_active=True)
                db.add(prov)
                db.flush()
                for city_name in p.get("cities", []):
                    c = City(name=city_name, province_id=prov.id, is_active=True)
                    db.add(c)
        db.commit()
        print("Seeding completed")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
