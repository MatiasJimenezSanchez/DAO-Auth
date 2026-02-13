import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token

# Usar archivo real
TEST_DB_FILE = "./test_final.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea la DB limpia al inicio"""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    Base.metadata.create_all(bind=engine)
    yield
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

@pytest.fixture(scope="function")
def db_session():
    """Sesión por test con limpieza profunda"""
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    connection.close()
    
    # LIMPIEZA TOTAL: Borrar datos de TODAS las tablas entre tests
    with engine.connect() as conn:
        with conn.begin():
            # Desactivar FKs para borrar sin preocuparse del orden
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            
            # Lista completa de tablas a limpiar
            tables_to_clean = [
                "usuarios_empresa", 
                "simulations", 
                "users", 
                "empresas",
                # Tablas de catálogos (las que causaban el fallo)
                "cities", 
                "provinces", 
                "regions", 
                "industries", 
                "skills", 
                "content_categories", 
                "universities"
            ]
            
            for table in tables_to_clean:
                try:
                    conn.execute(text(f"DELETE FROM {table}"))
                except Exception:
                    pass # Ignorar si la tabla no existe aun
            
            conn.execute(text("PRAGMA foreign_keys = ON;"))

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture
def valid_company_data():
    return {
        "nombre_empresa": "Test Company Inc",
        "slug": "test-company-inc",
        "tipo_empresa": "real_nacional",
        "industria": "Technology",
        "pais": "Ecuador",
        "ciudad": "Quito",
        "descripcion_corta": "A test company for unit tests"
    }

@pytest.fixture
def test_company(db_session, valid_company_data):
    from app.models.empresa import Empresa
    existing = db_session.query(Empresa).filter_by(slug=valid_company_data["slug"]).first()
    if existing: return existing
    company = Empresa(**valid_company_data)
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company
