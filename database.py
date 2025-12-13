# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. URL de la base de datos
# Para SQLite es un archivo local. Para Postgres sería: "postgresql://user:password@localhost/dbname"
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. El Motor (Engine)
# connect_args={"check_same_thread": False} es SOLO necesario para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. La Sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. La Base para los modelos
Base = declarative_base()

# 5. Dependencia para obtener la DB en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()