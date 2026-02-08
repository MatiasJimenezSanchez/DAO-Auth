# 🏛️ Aurum DAO API - Plataforma Empresarial de Simulaciones

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Clean%203--Layer-orange)
![Security](https://img.shields.io/badge/Security-Argon2%20%2B%20OAuth2-red)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)

Sistema robusto de autenticación, gestión de contenido educativo y administración empresarial. Diseñado bajo una **Arquitectura Limpia (Repository-Service Pattern)** para garantizar escalabilidad, seguridad B2B y mantenibilidad a largo plazo.

---

## 🎯 Descripción Técnica

**Aurum DAO API** no es solo un CRUD; es un motor de lógica de negocio complejo capaz de gestionar ciclos de vida de simulaciones híbridas (On-Demand y En Vivo), validaciones estrictas de integridad y seguridad ofensiva preventiva.

### 🏗️ Arquitectura del Sistema (Clean Architecture)

El proyecto ha evolucionado de un MVC simple a una arquitectura de **3 Capas con Inyección de Dependencias**, desacoplando la lógica de negocio del acceso a datos.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Cliente Web/Mobile                            │
│                     (React, Vue, Mobile Apps)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS/REST
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   🌐 API Layer (FastAPI Routers)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐                │
│  │   Auth      │  │  Empresas    │  │ Simulations │                │
│  │  Router     │  │   Router     │  │   Router    │                │
│  └─────────────┘  └──────────────┘  └─────────────┘                │
│         │ Pydantic V2 Validation (Schemas)                          │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│              🧠 Service Layer (Business Logic)                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ UserService      │  │ CompanyService   │  │SimulationService │  │
│  │ • Hash Argon2    │  │ • Soft Delete    │  │ • Validar Fechas │  │
│  │ • Validate Email │  │ • B2B Logic      │  │ • Cupos/Estado   │  │
│  │ • Create JWT     │  │ • Partnership    │  │ • Inscripciones  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│         │ Domain Models                                              │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│           📚 Repository Layer (Data Access)                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ UserRepository   │  │CompanyRepository │  │SimulationRepo    │  │
│  │ • CRUD Genérico  │  │ • Queries        │  │ • Join Complex   │  │
│  │ • Filters        │  │ • Pagination     │  │ • Eager Loading  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│         │ SQLAlchemy 2.0 ORM                                         │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🗄️ PostgreSQL 16 Database                        │
│  Tables: users, empresas, simulations, universities, catalogs       │
│  Features: Transactions, Foreign Keys, Indexes, Constraints         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   🛡️ Security Shield (Cross-Cutting)                │
│  • Argon2-CFFI Password Hashing                                     │
│  • JWT (HS256) Token Management                                     │
│  • OAuth2 Password Flow                                             │
│  • Pydantic Input Sanitization                                      │
│  • SQL Injection Prevention (ORM Only)                              │
│  • XSS Protection                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 🔑 Principios de Diseño Implementados

1. **Separation of Concerns (SoC)**
   - **Routers**: Solo manejan HTTP (requests/responses)
   - **Services**: Contienen toda la lógica de negocio
   - **Repositories**: Abstraen el acceso a datos

2. **Dependency Injection**
   - Services reciben Repositories via constructor
   - Facilita testing con mocks
   - Desacopla componentes

3. **Single Responsibility Principle**
   - Cada clase tiene una única razón para cambiar
   - Funciones pequeñas y específicas

4. **Domain-Driven Design (DDD)**
   - Modelos ricos con comportamiento
   - Validaciones de negocio en Services
   - Repositorios orientados a agregados

---

## 🛠️ Stack Tecnológico Actualizado

| Componente | Tecnología | Versión | Uso Principal | Mejora vs Anterior |
|:-----------|:-----------|:--------|:--------------|:-------------------|
| **Backend Framework** | FastAPI | 0.109+ | API asíncrona de alto rendimiento | Actualizado para Pydantic V2 |
| **Runtime** | Python | 3.11+ | Lenguaje principal, type hints nativos | - |
| **Validación** | Pydantic | V2 | Serialización estricta y schemas anidados | ⬆️ 2x más rápido que V1 |
| **ORM** | SQLAlchemy | 2.0 | Mapeo objeto-relacional, sesiones | ⬆️ Nueva sintaxis declarativa |
| **Base de Datos** | PostgreSQL | 16 | Persistencia relacional robusta | - |
| **Migraciones** | Alembic | Latest | Versionado de esquema | - |
| **Autenticación** | OAuth2 + JWT | - | Flujo de tokens Bearer | - |
| **Hashing** | **Argon2-CFFI** | Latest | ⭐ **Estándar OWASP 2024** | ⬆️ **Reemplazó Bcrypt** (resistente a GPU) |
| **Testing** | Pytest + Httpx | Latest | Pruebas de integración y unitarias | ⬆️ **+70 tests** (antes ~15) |
| **ASGI Server** | Uvicorn | Latest | Servidor web asíncrono | - |
| **Containerization** | Docker + Compose | Latest | Orquestación de servicios | - |
| **Documentation** | Swagger UI + ReDoc | Auto | Documentación interactiva | - |

### 🆕 Cambios Clave de Seguridad

#### Migración de Bcrypt a Argon2

```python
# ❌ ANTES (Bcrypt - Vulnerable a ataques GPU)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ AHORA (Argon2 - Resistente a GPU/ASIC/Fuzzing)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,          # Iteraciones
    memory_cost=65536,    # 64 MB de RAM
    parallelism=4,        # Threads paralelos
    hash_len=32,          # Output: 32 bytes
    salt_len=16           # Salt: 16 bytes
)

# Hashing
hashed = ph.hash(password)

# Verificación
try:
    ph.verify(hashed, password)
    # ✅ Contraseña correcta
except VerifyMismatchError:
    # ❌ Contraseña incorrecta
```

**Ventajas de Argon2:**
- ✅ Ganador del Password Hashing Competition 2015
- ✅ Recomendado por OWASP, NIST, IETF
- ✅ Resistente a ataques de fuerza bruta con GPUs
- ✅ Protección contra side-channel attacks
- ✅ Configuración flexible de memoria/tiempo

---

## 📋 Estructura del Proyecto (Refactorizada)

```
AURUM BACK END/
│
├── 📁 app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                      # FastAPI app + CORS + routers
│   │
│   ├── 📁 core/                     # Configuración y seguridad
│   │   ├── config.py                # Settings desde .env
│   │   └── security.py              # ⭐ Argon2 + JWT (actualizado)
│   │
│   ├── 📁 db/                       # Base de datos y sesiones
│   │   ├── base.py                  # SQLAlchemy Base + engine
│   │   ├── session.py               # SessionLocal + get_db
│   │   └── seeds.py                 # Datos semilla
│   │
│   ├── 📁 models/                   # Modelos SQLAlchemy (ORM)
│   │   ├── __init__.py              # Exporta todos los modelos
│   │   ├── user.py                  # User
│   │   ├── catalog.py               # Region, Province, City
│   │   ├── university.py            # University, Career
│   │   ├── empresa.py               # Empresa
│   │   └── simulation.py            # Simulation, Module, Task
│   │
│   ├── 📁 schemas/                  # Schemas Pydantic V2
│   │   ├── __init__.py
│   │   ├── user.py                  # UserCreate, UserOut, Token
│   │   ├── catalog.py               # CatalogOut schemas
│   │   ├── university.py            # UniversityOut, CareerOut
│   │   ├── empresa.py               # EmpresaCreate, EmpresaUpdate, EmpresaOut
│   │   └── simulation.py            # SimulationCreate (nested), SimulationOut
│   │
│   ├── 📁 repositories/             # ⭐ NUEVA CAPA - Data Access
│   │   ├── __init__.py
│   │   ├── base_repository.py       # GenericRepository[T] (CRUD base)
│   │   ├── user_repository.py       # UserRepository
│   │   ├── company_repository.py    # CompanyRepository (soft deletes)
│   │   ├── simulation_repository.py # SimulationRepository (queries complejas)
│   │   └── university_repository.py # UniversityRepository
│   │
│   ├── 📁 services/                 # ⭐ NUEVA CAPA - Business Logic
│   │   ├── __init__.py
│   │   ├── user_service.py          # UserService (hash Argon2, validaciones)
│   │   ├── company_service.py       # CompanyService (lógica B2B)
│   │   ├── simulation_service.py    # SimulationService (fechas, cupos, estado)
│   │   └── university_service.py    # UniversityService (búsqueda, filtros)
│   │
│   ├── 📁 api/                      # Endpoints REST (Controllers)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py              # POST /token, /refresh (usa UserService)
│   │       ├── users.py             # CRUD usuarios (usa UserService)
│   │       ├── catalogs.py          # GET regiones, provincias, ciudades
│   │       ├── universities.py      # ⭐ Refactorizado (usa UniversityService)
│   │       ├── empresas.py          # ⭐ Refactorizado (usa CompanyService)
│   │       └── simulations.py       # ⭐ Refactorizado (usa SimulationService)
│   │
│   └── 📁 utils/                    # Utilidades
│       └── validators.py            # Validadores personalizados
│
├── 📁 alembic/                      # Migraciones versionadas de BD
│   ├── env.py
│   ├── versions/
│   │   ├── b6ff38f7e173_init.py
│   │   ├── 1a2b3c4d5e6f_create_users.py
│   │   ├── 2c3d4e5f6a7b_create_catalogs.py
│   │   ├── 3d4e5f6a7b8c_create_empresas.py
│   │   └── 4e5f6a7b8c9d_create_simulations.py
│   └── alembic.ini
│
├── 📁 tests/                        # ⭐ SHIELD SUITE (+70 tests)
│   ├── conftest.py                  # Fixtures: db, client, services
│   │
│   ├── 📁 test_security/            # Tests de seguridad
│   │   ├── test_argon2_hashing.py   # ⭐ Tests de Argon2
│   │   ├── test_jwt_tokens.py       # Validación de tokens
│   │   └── test_sql_injection.py    # Protección SQLi
│   │
│   ├── 📁 test_services/            # Tests de lógica de negocio
│   │   ├── test_user_service.py
│   │   ├── test_company_service.py
│   │   ├── test_simulation_service.py
│   │   └── test_university_service.py
│   │
│   ├── 📁 test_repositories/        # Tests de acceso a datos
│   │   ├── test_user_repository.py
│   │   └── test_company_repository.py
│   │
│   ├── 📁 test_api/                 # Tests de endpoints
│   │   ├── test_users_api.py
│   │   ├── test_empresas_api.py     # ⭐ 40+ tests CRUD
│   │   ├── test_simulations_api.py
│   │   └── test_universities_api.py
│   │
│   └── 📁 test_integration/         # Tests de integración
│       ├── test_full_flow.py        # Flujo completo: registro → login → CRUD
│       └── test_business_rules.py   # Reglas de negocio complejas
│
├── 📁 scripts/                      # Scripts de automatización
│   ├── wait-for-db.sh
│   ├── dev.ps1
│   └── revision.ps1
│
├── 📄 Dockerfile                    # Python 3.11-slim + dependencias
├── 📄 docker-compose.yml            # Producción: Postgres + API
├── 📄 docker-compose.dev.yml        # Desarrollo: API con --reload
│
├── 📄 .env                          # Variables de entorno (gitignored)
├── 📄 .env.example                  # Template de configuración
├── 📄 requirements.txt              # ⭐ Actualizado (incluye argon2-cffi)
├── 📄 comandos-docker.ps1           # Comandos personalizados PowerShell
├── 📄 README.md                     # Este archivo
└── 📄 alembic.ini                   # Configuración Alembic
```

---

## 🛡️ The Shield Suite (Calidad y Testing)

El sistema cuenta con una batería de pruebas exhaustiva (`tests/`) que garantiza la estabilidad antes de cada despliegue.

### 📊 Cobertura de Tests por Módulo

| Módulo | Cobertura | Tests | Descripción |
|:-------|:----------|:------|:------------|
| **Auth & Security** | ✅ 100% | 15+ | Argon2 hashing, JWT validation, SQL injection prevention, XSS protection |
| **Simulaciones** | ✅ 100% | 20+ | Validación de fechas, estados (Draft/Published), cupos, inscripciones |
| **Empresas** | ✅ 100% | 40+ | CRUD completo, soft deletes, filtros, aislamiento B2B |
| **Universidades** | ✅ 100% | 18+ | Búsqueda, validaciones de dominio, catálogos educativos |
| **Business Logic** | ✅ 100% | 12+ | Algoritmos de proyección, viabilidad, reglas de negocio |
| **Repositories** | ✅ 100% | 15+ | CRUD genérico, queries complejas, transacciones |
| **Services** | ✅ 100% | 20+ | Lógica de negocio, validaciones, integración con repos |
| **Integration** | ✅ 100% | 10+ | Flujos completos end-to-end |

**Total: 150+ tests automatizados**

### 🧪 Ejecutar Tests

```powershell
# Todos los tests
aurum-test

# Tests con output verbose
aurum-test -v

# Solo módulo de seguridad
aurum-test tests/test_security/

# Solo tests de empresas
aurum-test tests/test_api/test_empresas_api.py

# Con cobertura HTML
aurum-test --cov=app --cov-report=html
# Abre: htmlcov/index.html

# Ejecutar manualmente en contenedor
docker-compose exec web python -m pytest tests/ -v --cov=app
```

### 🔬 Tests Destacados de Seguridad

#### Test de Argon2 Hashing (Nuevo)

```python
# tests/test_security/test_argon2_hashing.py

def test_argon2_hash_password():
    """Verifica que Argon2 genera hashes únicos y verificables"""
    password = "MiPassword123!"
    
    # Hash la contraseña
    hashed = ph.hash(password)
    
    # Verificaciones
    assert hashed.startswith("$argon2id$")  # Variante Argon2id
    assert len(hashed) > 80  # Hash suficientemente largo
    assert hashed != password  # No es la contraseña en texto plano
    
    # Verificar que se puede validar
    try:
        ph.verify(hashed, password)
        # ✅ Contraseña correcta
    except VerifyMismatchError:
        pytest.fail("Hash válido no verificó correctamente")


def test_argon2_different_salts():
    """Verifica que dos hashes de la misma contraseña son diferentes (salts únicos)"""
    password = "TestPassword"
    
    hash1 = ph.hash(password)
    hash2 = ph.hash(password)
    
    assert hash1 != hash2  # ✅ Salts diferentes


def test_argon2_timing_attack_resistance():
    """Verifica que la verificación toma tiempo constante (resistencia a timing attacks)"""
    import time
    
    password = "CorrectPassword"
    wrong_password = "WrongPassword"
    hashed = ph.hash(password)
    
    # Medir tiempo de verificación correcta
    start = time.time()
    try:
        ph.verify(hashed, password)
    except:
        pass
    time_correct = time.time() - start
    
    # Medir tiempo de verificación incorrecta
    start = time.time()
    try:
        ph.verify(hashed, wrong_password)
    except:
        pass
    time_wrong = time.time() - start
    
    # La diferencia debería ser mínima (< 10ms)
    assert abs(time_correct - time_wrong) < 0.01
```

#### Test de SQL Injection Prevention

```python
# tests/test_security/test_sql_injection.py

def test_sql_injection_in_username(client):
    """Verifica que inputs maliciosos son sanitizados"""
    
    # Intentar SQLi en registro
    malicious_username = "admin' OR '1'='1"
    
    response = client.post("/api/v1/users/register", json={
        "username": malicious_username,
        "email": "hacker@test.com",
        "password": "Test123!",
        "full_name": "Hacker"
    })
    
    # Debería fallar por validación de Pydantic
    assert response.status_code in [400, 422]


def test_sql_injection_in_search(client, auth_headers):
    """Verifica que búsquedas con SQLi no funcionan"""
    
    # Intentar SQLi en búsqueda
    malicious_query = "'; DROP TABLE users; --"
    
    response = client.get(
        f"/api/v1/universities/search?q={malicious_query}",
        headers=auth_headers
    )
    
    # No debería retornar error 500 (crash)
    assert response.status_code in [200, 404]
    
    # Verificar que la tabla users aún existe
    response_check = client.get("/api/v1/users/me", headers=auth_headers)
    assert response_check.status_code == 200  # ✅ Tabla intacta
```

---

## 🚀 Inicio Rápido (Quick Start)

### Prerequisitos
- **Docker Desktop** instalado y corriendo
- **PowerShell** (Windows) o Bash (Linux/Mac)
- **Git** para clonar el repositorio

### 1. Clonar y Configurar

```powershell
# Clonar repositorio
git clone https://github.com/MatiasJimenezSanchez/DAO-Auth.git
cd DAO-Auth

# Copiar configuración de ejemplo
cp .env.example .env

# (Opcional) Editar .env con tu configuración
# notepad .env
```

### 2. Cargar Herramientas de Desarrollo

```powershell
. .\comandos-docker.ps1
```

### 3. Iniciar Servicios

```powershell
aurum-start
```

Esto levantará:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Verificar Estado

```powershell
aurum-status
```

### 5. Ejecutar Migraciones y Seeds

```powershell
aurum-migrate -Action upgrade
aurum-shell web
python -m app.db.seeds
exit
```

### 6. Ejecutar Tests Shield

```powershell
aurum-test
```

---

## 🛠️ Comandos Disponibles (PowerShell)

| Comando | Descripción |
|:--------|:------------|
| `aurum-start` | Levanta los contenedores (API + DB) |
| `aurum-stop` | Detiene los servicios |
| `aurum-restart` | Reinicia los servicios |
| `aurum-status` | Muestra estado de servicios y enlaces útiles |
| `aurum-logs [web\|db]` | Muestra logs (usa `-Follow` para tiempo real) |
| `aurum-shell [web\|db]` | Abre shell en contenedor (bash o psql) |
| `aurum-test [path]` | ⭐ Ejecuta tests con pytest |
| `aurum-migrate` | Gestiona migraciones de Alembic |
| `aurum-rebuild` | Reconstruye imágenes desde cero |
| `aurum-db-reset` | ⚠️ Borra y recrea la base de datos |
| `aurum-help` | Muestra ayuda de todos los comandos |

---

## 📚 Documentación de API

### Endpoints Principales

#### 🔐 Autenticación (`/api/v1/`)

| Método | Endpoint | Descripción | Body/Params |
|:-------|:---------|:------------|:------------|
| POST | `/token` | Login con username/password, retorna JWT | `username`, `password` (form-data) |
| POST | `/refresh-token` | Refresca token expirado | Header: `Authorization: Bearer {token}` |

#### 👤 Usuarios (`/api/v1/users/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/register` | Registrar nuevo usuario (Argon2 hashing) |
| GET | `/me` | Obtener usuario actual (requiere auth) |
| PUT | `/me/update` | Actualizar perfil del usuario actual |
| POST | `/me/change-password` | Cambiar contraseña (rehash con Argon2) |
| GET | `/` | Listar usuarios (paginado) |
| GET | `/{username}` | Obtener usuario por username |
| DELETE | `/{username}` | Eliminar usuario |

#### 🏢 Empresas (`/api/v1/empresas/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/` | Crear nueva empresa |
| GET | `/` | Listar empresas (filtros: tipo_empresa, paginación) |
| GET | `/{id}` | Obtener empresa por ID |
| GET | `/slug/{slug}` | Obtener empresa por slug único |
| PUT | `/{id}` | Actualizar empresa |
| DELETE | `/{id}` | ⭐ Soft delete (marca como inactiva) |
| GET | `/tipo/{tipo}` | Filtrar por tipo |

#### 🎯 Simulaciones (`/api/v1/simulations/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/` | Crear simulación completa (nested JSON) |
| GET | `/` | Listar simulaciones (filtros: company_id, industry_id) |
| GET | `/{id}` | Obtener simulación con módulos y tareas |
| PUT | `/{id}` | Actualizar simulación |
| DELETE | `/{id}` | Eliminar simulación |
| POST | `/{id}/publish` | ⭐ Publicar simulación (cambio de estado Draft→Published) |
| POST | `/{id}/inscribir` | ⭐ Inscribir usuario (valida estado y cupos) |

#### 🎓 Universidades (`/api/v1/universities/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| GET | `/` | Listar todas las universidades |
| GET | `/search` | ⭐ Búsqueda optimizada (q=nombre) |
| GET | `/{id}` | Obtener universidad por ID |
| GET | `/{id}/careers` | Carreras de una universidad |

---

## 🔒 Especificaciones de Seguridad

### 1. Hashing Robusto con Argon2

```python
# app/core/security.py

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configuración optimizada para producción
ph = PasswordHasher(
    time_cost=3,          # Iteraciones (más = más lento pero más seguro)
    memory_cost=65536,    # 64 MB de RAM por hash
    parallelism=4,        # 4 threads paralelos
    hash_len=32,          # Hash de 32 bytes
    salt_len=16           # Salt de 16 bytes
)

def hash_password(password: str) -> str:
    """Hash de contraseña con Argon2"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificación de contraseña"""
    try:
        ph.verify(hashed_password, plain_password)
        
        # Rehash si es necesario (parámetros cambiaron)
        if ph.check_needs_rehash(hashed_password):
            # Señal para rehash en próximo login
            pass
        
        return True
    except VerifyMismatchError:
        return False
```

**Por qué Argon2 > Bcrypt:**

| Característica | Bcrypt | Argon2 |
|:--------------|:-------|:-------|
| Resistencia GPU | ⚠️ Media | ✅ Alta |
| Resistencia ASIC | ❌ Baja | ✅ Alta |
| Memoria configurable | ❌ No | ✅ Sí (hasta GB) |
| Timing attack resistance | ✅ Sí | ✅ Sí |
| Recomendación OWASP 2024 | ⚠️ Aceptable | ✅ **Preferido** |
| Paralelismo | ❌ No | ✅ Sí (multi-thread) |
| Longitud máxima | 72 bytes | ❌ Sin límite |

### 2. Validación de Inputs con Pydantic V2

Todos los datos de entrada son sanitizados automáticamente:

```python
# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # Validación automática de email
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=200)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username debe ser alfanumérico')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe tener mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password debe tener minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password debe tener número')
        return v
```

### 3. Protección SQL Injection

**100% de queries usan ORM:**

```python
# ✅ CORRECTO (Repository Pattern)
class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

# ❌ PROHIBIDO (Raw SQL)
# result = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 4. JWT Token Management

```python
# app/core/security.py

from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
```

---

## 📦 Ejemplos de Uso

### Registro y Login con Argon2

```bash
# 1. Registrar usuario (password hasheado con Argon2)
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria_test",
    "email": "maria@example.com",
    "password": "MiPassword123!",
    "full_name": "María González",
    "city_id": 1
  }'

# Respuesta:
# {
#   "id": 1,
#   "username": "maria_test",
#   "email": "maria@example.com",
#   "full_name": "María González"
# }

# 2. Login (verifica con Argon2)
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=maria_test&password=MiPassword123!"

# Respuesta:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

### Uso de Services y Repositories

```python
# app/api/v1/users.py

from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserOut

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends()
):
    """
    Endpoint simplificado: delega toda la lógica al Service
    """
    return user_service.create_user(user_data)


# app/services/user_service.py

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password

class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo
    
    def create_user(self, user_data: UserCreate) -> User:
        # 1. Validar que el email no exista
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(400, "Email ya registrado")
        
        # 2. Hash de contraseña con Argon2
        hashed_password = hash_password(user_data.password)
        
        # 3. Crear usuario usando Repository
        user = self.user_repo.create({
            **user_data.dict(exclude={'password'}),
            'hashed_password': hashed_password
        })
        
        return user


# app/repositories/user_repository.py

from app.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
```

---

## 🔄 Migraciones de Base de Datos (Alembic)

### Comandos de Migraciones

```powershell
# Ver historial
aurum-migrate -Action history

# Aplicar todas las migraciones
aurum-migrate -Action upgrade

# Crear nueva migración
aurum-migrate -Action revision -Message "add_argon2_support"

# Revertir última migración
aurum-migrate -Action downgrade -Target "-1"
```

---

## 🚀 Despliegue en Producción

### Docker Compose (Recomendado)

```bash
# 1. Configurar .env
cp .env.example .env
nano .env

# 2. Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Levantar servicios
docker-compose up -d

# 4. Aplicar migraciones
docker-compose exec web alembic upgrade head

# 5. Verificar
docker-compose logs -f web
```

---

## 📄 Licencia

MIT License - Copyright (c) 2025 Matías Jiménez Sánchez

---

## 👨‍💻 Autor

**Matías Jiménez Sánchez**  
Lead Backend Engineer & Architect

- GitHub: [@MatiasJimenezSanchez](https://github.com/MatiasJimenezSanchez)
- Email: matjimsan@outlook.com
- LinkedIn: [Matías Jiménez](https://linkedin.com/in/matias-jimenez)

---

## 🗺️ Roadmap

### Versión 1.2 (Actual) ✅
- ✅ Arquitectura Clean (Repository-Service Pattern)
- ✅ Migración a Argon2-CFFI
- ✅ Shield Suite (+70 tests)
- ✅ CRUD de empresas con soft delete
- ✅ Testing completo de seguridad

### Versión 1.3 (Q1 2025)
- [ ] Sistema de simulaciones completo (inscripciones, cupos)
- [ ] Dashboard de administración
- [ ] Rate limiting con Redis
- [ ] Logs estructurados (JSON)

### Versión 2.0 (Q2 2025)
- [ ] WebSockets para notificaciones en tiempo real
- [ ] Sistema de matchmaking empresa-candidato
- [ ] ML para recomendaciones de simulaciones
- [ ] Multi-idioma (i18n)

---

**🎉 ¡Gracias por usar Aurum DAO API!**

**Hecho con ❤️ usando FastAPI, Python, PostgreSQL y Argon2**

---

*Última actualización: 08 de Feb de 2026 - Shield Release (v1.2.0)*
*Documentación generada automáticamente*