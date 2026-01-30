"""
Pytest Configuration and Fixtures
Versión corregida con SQLite en memoria para tests
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# ============================================
# FIX: Usar SQLite en memoria para tests
# ============================================
# Esto evita depender de PostgreSQL durante las pruebas
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_aurum.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión de base de datos para cada test
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Limpiar la base de datos después de cada test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Crea un cliente de prueba de FastAPI
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def empresa_data():
    """
    Datos de prueba para crear una empresa
    """
    return {
        "nombre_empresa": "Tech Innovations EC",
        "slug": "tech-innovations-ec",
        "tipo_empresa": "real_nacional",
        "industria": "Tecnología",
        "descripcion_corta": "Empresa de tecnología ecuatoriana líder en innovación",
        "email_contacto": "contacto@techinnovations.ec",
        "pais": "Ecuador",
        "ciudad": "Quito",
        "es_partner_activo": True,
        "tipo_partnership": "premium"
    }
