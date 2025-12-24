from sqlalchemy.orm import sessionmaker
from app.db.base import engine

# Crear la sesión usando el engine importado desde app.db.base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener la DB en cada solicitud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
