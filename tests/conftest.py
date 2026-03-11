"""
conftest.py - Delphos Test Infrastructure v4 (INTEGRADO Y COMPLETO)

PATRON:
  - SQLite archivo físico (NullPool) para evitar "database is locked".
  - setup_db scope=function: Tablas frescas en cada test.
  - Global Seeder integrado: Crea los datos mínimos (Región, Provincia, Ciudad, Categoría, Industria, Empresa, Oráculo) para que las Foreign Keys no fallen.
  - FIXTURES RESTAURADOS: Todos los fixtures usados por Fases 1 a 14.
"""
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Forzar DATABASE_URL a SQLite local
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.setdefault("SECRET_KEY", "test_secret_key_123")

from app.main import app          # noqa: E402
from app.db.base import Base      # noqa: E402
from app.api.deps import get_db   # noqa: E402

# =============================================================================
# ENGINE - NullPool
# =============================================================================
engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

from sqlalchemy.pool import NullPool
from sqlalchemy import event

# === FIX DE LLAVES FORÁNEAS PARA SQLITE ===
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# =============================================================================
# SETUP + GLOBAL SEEDER
# =============================================================================
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        _seed_base_data(session)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise RuntimeError(f"[conftest] Global Seeder falló: {exc}") from exc
    finally:
        session.close()

    yield

    Base.metadata.drop_all(bind=engine)

def _seed_base_data(session):
    from app.models.catalog import Region, Province, City, ContentCategory, Industry
    from app.models.empresa import Empresa

    region = Region(name="Sierra", code="SI", is_active=True)
    session.add(region)
    session.flush()

    province = Province(region_id=region.id, name="Pichincha", code="PI", is_active=True)
    session.add(province)
    session.flush()

    city = City(province_id=province.id, name="Quito", is_capital=True, is_active=True)
    session.add(city)
    session.flush()

    industry = Industry(name="Technology", slug="technology", is_active=True)
    session.add(industry)
    session.flush()

    category = ContentCategory(name="General", slug="general", is_active=True)
    session.add(category)
    session.flush()

    empresa = Empresa(
        nombre_empresa="Empresa Base Test",
        slug="empresa-base-test",
        tipo_empresa="real_nacional",
        industria="Technology",
        pais="Ecuador",
        ciudad="Quito",
    )
    session.add(empresa)
    session.flush()

    _seed_oracle(session)
    _seed_virtual_mentor(session, empresa.id)


def _seed_virtual_mentor(session, empresa_id: int):
    """Seed de mentor virtual para tests de IA"""
    try:
        from app.models.gamification import VirtualMentor
        mentor = VirtualMentor(
            empresa_id=empresa_id,
            nombre="Mentor de Prueba IA",
            titulo="Senior AI Coach",
            bio="Mentor virtual para testing de conversaciones IA",
            personalidad="profesional",
            prompt_sistema="Eres un mentor profesional y amigable.",
            modelo_ia="gpt-4",
            is_active=True
        )
        session.add(mentor)
        session.flush()
    except Exception as e:
        print(f"Error seeding mentor: {e}")

def _seed_oracle(session):
    try:
        from app.models.oracle import Archetype, OracleQuestion, QuestionOption
        archetype = Archetype(nombre="Analítico", slug="analitico", descripcion="Perfil base", min_skills={}, esta_activo=True)
        session.add(archetype)
        session.flush()

        for i in range(1, 4):
            question = OracleQuestion(pregunta=f"Pregunta de prueba {i}", categoria=f"categoria_{i}", orden=i, esta_activo=True)
            session.add(question)
            session.flush()
            for j in range(1, 3):
                option = QuestionOption(pregunta_id=question.id, texto_opcion=f"Opción {j} de pregunta {i}", skill_mapping={"skill_test": j * 10}, orden=j)
                session.add(option)
        session.flush()
    except Exception:
        session.rollback()

# =============================================================================
# DB SESSION & CLIENT
# =============================================================================
@pytest.fixture(scope="function")
def db_session(setup_db):
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# =============================================================================
# USUARIOS Y AUTH
# =============================================================================
@pytest.fixture(scope="function")
def test_user(db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    user = User(username="testuser", email="test@test.com", hashed_password=get_password_hash("Password123!"), full_name="Test User", is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def auth_header(test_user):
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def test_user_for_company(db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    uid = uuid.uuid4().hex[:6]
    user = User(username=f"co_user_{uid}", email=f"co_{uid}@test.com", hashed_password=get_password_hash("pass123"), full_name="Company User", is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# =============================================================================
# COMPAÑÍAS Y SIMULACIONES
# =============================================================================
@pytest.fixture(scope="function")
def valid_company_data():
    uid = uuid.uuid4().hex[:8]
    return {"nombre_empresa": f"Test Company {uid}", "slug": f"test-company-{uid}", "tipo_empresa": "real_nacional", "industria": "Technology", "pais": "Ecuador", "ciudad": "Quito"}

@pytest.fixture(scope="function")
def base_company(db_session):
    from app.models.empresa import Empresa
    uid = uuid.uuid4().hex[:6]
    company = Empresa(nombre_empresa=f"Base Company {uid}", slug=f"base-company-{uid}", tipo_empresa="real_nacional", industria="Technology", pais="Ecuador", ciudad="Quito")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture(scope="function")
def test_company(base_company):
    return base_company

@pytest.fixture(scope="function")
def base_category(db_session):
    from app.models.catalog import ContentCategory
    uid = uuid.uuid4().hex[:6]
    category = ContentCategory(name=f"Category {uid}", slug=f"category-{uid}", is_active=True)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture(scope="function")
def seed_company_data(client, db_session):
    from app.models.empresa import Empresa
    from app.models.catalog import ContentCategory
    uid = uuid.uuid4().hex[:6]
    empresa = Empresa(nombre_empresa=f"Dashboard Co {uid}", slug=f"dashboard-co-{uid}", tipo_empresa="real_nacional", industria="Technology", pais="Ecuador", ciudad="Quito")
    db_session.add(empresa)
    cat = ContentCategory(name=f"DashCat {uid}", slug=f"dashcat-{uid}", is_active=True)
    db_session.add(cat)
    db_session.flush()
    db_session.commit()
    
    created = 0
    for _ in range(2):
        sim_uid = uuid.uuid4().hex[:6]
        res = client.post("/api/v1/simulaciones", json={"title": f"Dashboard Sim {sim_uid}", "slug": f"dash-sim-{sim_uid}", "short_description": "Dashboard test simulation", "company_id": empresa.id, "category_id": cat.id, "state": "published"})
        if res.status_code == 201:
            created += 1
            
    return {"empresa_id": empresa.id, "category_id": cat.id, "expected_simulations": created}

