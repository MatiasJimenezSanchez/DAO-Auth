from app.db.base import SessionLocal

# Dependencia para obtener la DB en cada solicitud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
