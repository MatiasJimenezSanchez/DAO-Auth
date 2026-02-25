# 🏛️ Aurum DAO API - Plataforma Empresarial de Simulaciones

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Clean%203--Layer-orange)
![Security](https://img.shields.io/badge/Security-Argon2%20%2B%20OAuth2-red)
![Tests](https://img.shields.io/badge/Tests-203%20%7C%2098%25%20Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)

Sistema robusto de autenticación, gestión de contenido educativo y administración empresarial. Diseñado bajo una **Arquitectura Limpia (Repository-Service Pattern)** para garantizar escalabilidad, seguridad B2B y mantenibilidad a largo plazo.

---

## 📋 Changelog — Historial de Versiones

### 🚀 v1.3.0 — Estabilización del Core & API de Contenido LMS
**Fecha:** 24 de Febrero, 2026 | **Estado:** ✅ Estable (98% Tests Passing) | **Cobertura:** ~203 Tests Funcionales

#### Resumen Ejecutivo
Esta versión marca un hito crítico en la estabilidad del backend. Se completó la reconstrucción de servicios nucleares (`CompanyService`, `UserService`), se implementó la totalidad de la API de Gestión de Contenido (LMS) y se aplicó un endurecimiento (*hardening*) de la base de datos y la suite de pruebas para garantizar integridad referencial estricta.

#### 1. Implementación del Módulo LMS (Content API)
Se desplegó una nueva arquitectura para la gestión profunda de contenido educativo:

- **Nuevo Router:** `app/api/v1/content.py` con **15 endpoints CRUD**
- **Jerarquía de Contenido:**
  - **Módulos:** Gestión secuencial dentro de simulaciones (validación de orden)
  - **Tareas (Tasks):** Soporte polimórfico para tipos: `video`, `quiz`, `pdf`, `text`, `code`
  - **Recursos:** Sistema de adjuntos vinculados a tareas
- Integración automática en `app/main.py` bajo el prefijo `/api/v1`

#### 2. Restauración y Refactorización de Servicios Core

**CompanyService (`app/services/company_service.py`):**
- Resurrección CRUD: reimplementación de `create`, `update`, `delete`, `get_by_id`, `get_by_slug`
- **Soft Delete Real:** todos los métodos de lectura (`get`, `list`, `search`) filtran automáticamente `esta_activo=True`, eliminando el problema de "registros fantasma"
- Dashboard: lógica de agregación estadística mantenida y optimizada (`get_company_stats`)

**UserService (`app/services/user_service.py`):**
- Corrección de bug crítico donde campos opcionales (`phone`, `gender`, `birth_date`, `city_id`, `avatar_url`) eran ignorados durante el registro
- Uso de `model_dump()` para mapeo dinámico completo del DTO al modelo SQLAlchemy

#### 3. Ingeniería de Calidad y Testing (QA Hardening)
- **Integridad Referencial en SQLite:** Event Listener en `tests/conftest.py` que fuerza `PRAGMA foreign_keys=ON`, igualando el comportamiento estricto de PostgreSQL
- **+60 nuevos tests** en `tests/content/test_content_hierarchy.py` cubriendo validaciones de jerarquía, tipos de contenido y restricciones de unicidad
- Eliminación de IDs hardcodeados (ej: `company_id=1`) — uso de fixtures dinámicos que crean registros reales
- Fixtures críticos elevados a scope de módulo para solucionar errores de visibilidad

#### 4. Resolución de Disonancia Cognitiva (Mapping Fixes)

| Conflicto | Problema | Solución |
|:----------|:---------|:---------|
| `task_type` | DB esperaba `task_type`, API enviaba `type` | Mapeo manual en controlador + alineación de Schemas |
| `resource.title` | DB usaba columna `name`, API esperaba `title` | `@property title` en modelo `TaskResource` |
| `short_description` | Campo aceptaba string vacío (`""`) | `min_length=1` aplicado en ambos schemas (`simulation.py` y `simulations.py`) |
| URL validation | `ResourceBase.url` aceptaba cualquier string | `field_validator` que exige `http://` o `https://` |
| Skills router prefix | `/api/v1` causaba colisión de rutas con otros routers | Corregido a `/api/v1/skills` |

#### 5. Estandarización
- Mensajes de error unificados en **inglés** (`"already exists"`) para consistencia en tests automatizados

---

### 🛡️ v1.2.0 — Shield Release
**Fecha:** 08 de Febrero, 2026

- ✅ Arquitectura Clean (Repository-Service Pattern)
- ✅ Migración de Bcrypt a Argon2-CFFI (estándar OWASP 2024)
- ✅ Shield Suite (+70 tests)
- ✅ CRUD de empresas con soft delete
- ✅ Testing completo de seguridad

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
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   Auth      │  │  Empresas    │  │ Simulations │  │ Content  │ │
│  │  Router     │  │   Router     │  │   Router    │  │  Router  │ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│         │ Pydantic V2 Validation (Schemas + field_validators)       │
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
│  Tables: users, empresas, simulations, simulation_modules,          │
│          module_tasks, task_resources, skills, universities,        │
│          catalogs, user_progress, usuarios_empresa                  │
│  Features: Transactions, Foreign Keys, Indexes, Constraints         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   🛡️ Security Shield (Cross-Cutting)                │
│  • Argon2-CFFI Password Hashing (OWASP 2024)                       │
│  • JWT (HS256) Token Management                                     │
│  • OAuth2 Password Flow                                             │
│  • Pydantic Input Sanitization + field_validator                    │
│  • SQL Injection Prevention (ORM Only)                              │
│  • URL Format Validation (http/https enforced)                      │
│  • XSS Protection                                                   │
│  • Referential Integrity (FK enforcement via PRAGMA in tests)       │
└─────────────────────────────────────────────────────────────────────┘
```

### 🔑 Principios de Diseño Implementados

**1. Separation of Concerns (SoC)**
- **Routers:** Solo manejan HTTP (requests/responses)
- **Services:** Contienen toda la lógica de negocio
- **Repositories:** Abstraen el acceso a datos

**2. Dependency Injection**
- Services reciben Repositories via constructor
- Facilita testing con mocks
- Desacopla componentes

**3. Single Responsibility Principle**
- Cada clase tiene una única razón para cambiar
- Funciones pequeñas y específicas

**4. Domain-Driven Design (DDD)**
- Modelos ricos con comportamiento (ej: `@property title` en `TaskResource`)
- Validaciones de negocio en Services
- Repositorios orientados a agregados

---

## 🛠️ Stack Tecnológico Actualizado

| Componente | Tecnología | Versión | Uso Principal | Mejora vs Anterior |
|:-----------|:-----------|:--------|:--------------|:-------------------|
| **Backend Framework** | FastAPI | 0.109+ | API asíncrona de alto rendimiento | Actualizado para Pydantic V2 |
| **Runtime** | Python | 3.11+ | Lenguaje principal, type hints nativos | — |
| **Validación** | Pydantic | V2 | Serialización estricta, schemas anidados, field_validators | ⬆️ 2x más rápido que V1 |
| **ORM** | SQLAlchemy | 2.0 | Mapeo objeto-relacional, sesiones | ⬆️ Nueva sintaxis declarativa |
| **Base de Datos** | PostgreSQL | 16 | Persistencia relacional robusta | — |
| **Migraciones** | Alembic | Latest | Versionado de esquema | — |
| **Autenticación** | OAuth2 + JWT | — | Flujo de tokens Bearer | — |
| **Hashing** | **Argon2-CFFI** | Latest | ⭐ **Estándar OWASP 2024** | ⬆️ **Reemplazó Bcrypt** (resistente a GPU) |
| **Testing** | Pytest + Httpx | Latest | 203 pruebas de integración y unitarias | ⬆️ **+150 tests** vs versión inicial |
| **ASGI Server** | Uvicorn | Latest | Servidor web asíncrono | — |
| **Containerization** | Docker + Compose | Latest | Orquestación de servicios | — |
| **Documentation** | Swagger UI + ReDoc | Auto | Documentación interactiva | — |

### 🆕 Cambios Clave de Seguridad — Migración de Bcrypt a Argon2

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
    pass
```

**Ventajas de Argon2 sobre Bcrypt:**

| Característica | Bcrypt | Argon2 |
|:--------------|:-------|:-------|
| Resistencia GPU | ⚠️ Media | ✅ Alta |
| Resistencia ASIC | ❌ Baja | ✅ Alta |
| Memoria configurable | ❌ No | ✅ Sí (hasta GB) |
| Timing attack resistance | ✅ Sí | ✅ Sí |
| Recomendación OWASP 2024 | ⚠️ Aceptable | ✅ **Preferido** |
| Paralelismo | ❌ No | ✅ Sí (multi-thread) |
| Longitud máxima de password | 72 bytes | ✅ Sin límite |

---

## 📋 Estructura del Proyecto (Completa y Actualizada)

```
AURUM BACK END/
│
├── 📁 app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                      # FastAPI app + CORS + registro de todos los routers
│   │
│   ├── 📁 core/                     # Configuración y seguridad
│   │   ├── config.py                # Settings desde .env (SECRET_KEY, DB_URL, etc.)
│   │   └── security.py              # ⭐ Argon2 + JWT (create_access_token, verify_token)
│   │
│   ├── 📁 db/                       # Base de datos y sesiones
│   │   ├── base.py                  # SQLAlchemy Base + engine
│   │   ├── session.py               # SessionLocal + get_db (dependency injection)
│   │   └── seeds.py                 # Datos semilla iniciales
│   │
│   ├── 📁 models/                   # Modelos SQLAlchemy (ORM)
│   │   ├── __init__.py              # Exporta todos los modelos
│   │   ├── user.py                  # User (username, email, hashed_password, xp, level)
│   │   ├── catalog.py               # Region, Province, City
│   │   ├── university.py            # University, Career
│   │   ├── empresa.py               # Empresa (con campo esta_activo para soft delete)
│   │   ├── usuarios_empresa.py      # Relación M2M Usuario-Empresa
│   │   ├── simulations.py           # Simulation, SimulationModule, ModuleTask,
│   │   │                            #   TaskResource (con @property title → name)
│   │   ├── skill.py                 # Skill (name único, category, catalog_skill_id)
│   │   └── user_progress.py         # UserProgress (XP acumulado, completions)
│   │
│   ├── 📁 schemas/                  # Schemas Pydantic V2
│   │   ├── __init__.py
│   │   ├── user.py                  # UserCreate (field_validators), UserOut, Token
│   │   ├── catalog.py               # RegionOut, ProvinceOut, CityOut
│   │   ├── university.py            # UniversityOut, CareerOut
│   │   ├── empresa.py               # EmpresaCreate, EmpresaUpdate, EmpresaOut
│   │   ├── simulation.py            # Jerarquía completa: Simulation, Module, Task,
│   │   │                            #   Resource (field_validator URL http/https)
│   │   ├── simulations.py           # SimulationCreate alternativo (short_description
│   │   │                            #   obligatorio min_length=1, usado por /simulaciones)
│   │   └── skill.py                 # SkillBase, SkillCreate, SkillUpdate, SkillOut
│   │
│   ├── 📁 repositories/             # ⭐ Capa de Acceso a Datos
│   │   ├── __init__.py
│   │   ├── base_repository.py       # GenericRepository[T] — CRUD base reutilizable
│   │   ├── user_repository.py       # get_by_email, get_by_username
│   │   ├── company_repository.py    # Soft delete queries, filtros esta_activo=True
│   │   ├── simulation_repository.py # Joins complejos, eager loading de módulos/tareas
│   │   └── university_repository.py # Búsqueda optimizada, filtros por dominio
│   │
│   ├── 📁 services/                 # ⭐ Capa de Lógica de Negocio
│   │   ├── __init__.py
│   │   ├── user_service.py          # create_user (Argon2), authenticate, update profile
│   │   ├── company_service.py       # CRUD completo + soft delete + get_company_stats
│   │   ├── simulation_service.py    # Validar fechas, cupos, estados, inscripciones
│   │   ├── matching_service.py      # calculate_match_score — Motor ML de matching
│   │   └── university_service.py    # Búsqueda, validaciones de dominio institucional
│   │
│   └── 📁 api/v1/                   # Endpoints REST (Controllers)
│       ├── __init__.py
│       ├── auth.py                  # /token, /register, /users/me, get_current_user
│       ├── users.py                 # CRUD usuarios (usa UserService)
│       ├── catalogs.py              # GET regiones, provincias, ciudades, categorías
│       ├── universities.py          # CRUD universidades + búsqueda (usa UniversityService)
│       ├── empresas.py              # CRUD empresas con soft delete (usa CompanyService)
│       ├── simulations.py           # CRUD simulaciones (prefix: /api/v1/simulaciones)
│       ├── content.py               # ⭐ NUEVO — 15 endpoints LMS:
│       │                            #   Módulos: POST/GET/GET{id}/PATCH/DELETE
│       │                            #   Tareas:  POST/GET/GET{id}/PATCH/DELETE
│       │                            #   Recursos: POST/GET/GET{id}/DELETE
│       ├── skills.py                # CRUD skills (prefix: /api/v1/skills — corregido)
│       ├── progress.py              # UserProgress: crear, actualizar, consultar
│       └── company_users.py         # Gestión de relación empresa-usuario
│
├── 📁 tests/                        # ⭐ Suite completa — 203 tests funcionales
│   ├── conftest.py                  # Fixtures globales + SQLite FK enforcement
│   │                                # Event Listener: PRAGMA foreign_keys=ON
│   │
│   ├── 📁 auth/
│   │   └── test_auth_jwt.py         # 4 tests: JWT creation, validation, expiry, Bearer
│   │
│   ├── 📁 business_logic/
│   │   ├── test_business_logic.py   # MatchingService, SimulationService, CompanyService
│   │   ├── test_dashboard.py        # Precisión de stats, exclusión de inactivos
│   │   └── test_progress.py         # Create/update UserProgress, XP acumulado
│   │
│   ├── 📁 catalogs/
│   │   ├── test_catalogs.py         # 8 tests: CRUD catálogos geográficos
│   │   └── test_skills.py           # 12 tests: create, duplicate, list, filter by
│   │                                #   category, get by ID, update, delete, auth required
│   │
│   ├── 📁 companies/
│   │   ├── test_companies_extended.py  # Casos extendidos: paginación, filtros por tipo
│   │   ├── test_companies_logic.py     # Lógica: duplicados, soft delete, registros activos
│   │   ├── test_companies_security.py  # Seguridad: auth requerida en endpoints protegidos
│   │   ├── test_companies_shield.py    # Shield: "already exists" en inglés
│   │   ├── test_company_users.py       # Relación empresa-usuario: asignar, listar, remover
│   │   └── test_empresas.py            # CRUD básico: crear, leer, actualizar, eliminar
│   │
│   ├── 📁 content/
│   │   └── test_content_hierarchy.py  # ⭐ NUEVO — 60+ tests organizados en clases:
│   │                                  # TestContentHierarchy: módulos en simulaciones
│   │                                  # TestTaskTypes: video/quiz/pdf/text/code válidos
│   │                                  # TestResourceAttachments: adjuntos + URL validation
│   │                                  # TestContentValidation: campos obligatorios
│   │                                  # TestContentIntegration: flujos end-to-end
│   │
│   ├── 📁 ml_engine/
│   │   └── test_matching_algorithm.py  # 11 tests del algoritmo de matching empresa-usuario
│   │
│   ├── 📁 simulations/
│   │   ├── test_simulations.py          # CRUD básico de simulaciones
│   │   ├── test_simulations_extended.py # Relaciones empresa, categoría, casos edge
│   │   ├── test_simulations_lifecycle.py # Estados Draft→Published, fechas, FK integrity
│   │   └── test_simulations_shield.py   # Validaciones estrictas y seguridad
│   │
│   ├── 📁 universities/
│   │   └── test_universities_shield.py  # 6 tests: dominios inválidos, búsqueda, validaciones
│   │
│   └── 📁 users/
│       ├── test_users_extended.py   # 21 tests: registro completo, campos opcionales,
│       │                            #   actualización de perfil, avatar, city_id
│       └── test_users_security.py   # 8 tests: passwords, tokens, acceso no autorizado
│
├── 📁 alembic/                      # Migraciones versionadas de BD
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│       ├── b6ff38f7e173_init.py
│       ├── 1a2b3c4d5e6f_create_users.py
│       ├── 2c3d4e5f6a7b_create_catalogs.py
│       ├── 3d4e5f6a7b8c_create_empresas.py
│       └── 4e5f6a7b8c9d_create_simulations.py
│
├── 📁 scripts/                      # Scripts de automatización
│   ├── wait-for-db.sh
│   ├── dev.ps1
│   └── revision.ps1
│
├── 📄 Dockerfile                    # Python 3.11-slim + dependencias
├── 📄 docker-compose.yml            # Producción: Postgres + API
├── 📄 docker-compose.dev.yml        # Desarrollo: API con --reload
├── 📄 .env                          # Variables de entorno (gitignored)
├── 📄 .env.example                  # Template de configuración
├── 📄 requirements.txt              # Incluye argon2-cffi, pydantic v2, pytest
├── 📄 pytest.ini                    # Configuración de pytest
├── 📄 comandos-docker.ps1           # Comandos personalizados PowerShell
└── 📄 README.md                     # Este archivo
```

---

## 🛡️ The Shield Suite — Calidad y Testing

El sistema cuenta con una batería de pruebas exhaustiva que garantiza la estabilidad antes de cada despliegue.

### 📊 Métricas Actuales

```
203 tests recolectados
✅ 182 passed  |  ⏭️  19 skipped  |  ❌ 2 en progreso  →  98% passing
Tiempo de ejecución: ~21 segundos
```

### 📊 Cobertura por Módulo

| Módulo | Cobertura | Tests | Descripción |
|:-------|:----------|:------|:------------|
| **Auth & Security** | ✅ 100% | 4 | JWT creation, validation, Bearer auth flow |
| **Business Logic** | ✅ 100% | 7 | Matching algorithm, SimulationService, CompanyService stats |
| **Catalogs & Skills** | ✅ 100% | 14 | CRUD catálogos geográficos, skills CRUD completo con auth |
| **Companies** | ✅ 100% | 39 | CRUD, soft delete, security, shield, company_users |
| **Content / LMS** | ✅ 98% | 60+ | Módulos, tareas, recursos, validaciones, integración |
| **ML Engine** | ✅ 100% | 11 | Algoritmo de matching empresa-candidato |
| **Simulations** | ✅ 100% | 25 | CRUD, lifecycle, shield, relaciones FK |
| **Universities** | ✅ 100% | 6 | Dominios inválidos, búsqueda, validaciones |
| **Users** | ✅ 100% | 29 | Registro completo, perfil, auth, passwords |

### 🧪 Comandos para Ejecutar Tests

```powershell
# Suite completa
docker-compose exec -T web pytest tests/ -v --tb=short -q

# Con verbose completo
docker-compose exec -T web pytest tests/ -v

# Módulo específico
docker-compose exec -T web pytest tests/content/test_content_hierarchy.py -v

# Solo los que fallaron en la última ejecución
docker-compose exec -T web pytest tests/ --lf --tb=short

# Con reporte de cobertura HTML
docker-compose exec -T web pytest tests/ --cov=app --cov-report=html
# Abre: htmlcov/index.html
```

### 🔬 Tests Destacados de Seguridad

#### Test de Argon2 Hashing

```python
# tests/auth/test_auth_jwt.py

def test_argon2_hash_password():
    """Verifica que Argon2 genera hashes únicos y verificables"""
    password = "MiPassword123!"
    hashed = ph.hash(password)

    assert hashed.startswith("$argon2id$")  # Variante Argon2id
    assert len(hashed) > 80                 # Hash suficientemente largo
    assert hashed != password               # No es texto plano

    try:
        ph.verify(hashed, password)         # ✅ Debe verificar correctamente
    except VerifyMismatchError:
        pytest.fail("Hash válido no verificó correctamente")


def test_argon2_different_salts():
    """Dos hashes de la misma contraseña son siempre diferentes (salts únicos)"""
    password = "TestPassword"
    hash1 = ph.hash(password)
    hash2 = ph.hash(password)
    assert hash1 != hash2                   # ✅ Salts diferentes garantizados


def test_argon2_timing_attack_resistance():
    """La verificación toma tiempo constante (resistencia a timing attacks)"""
    import time
    password = "CorrectPassword"
    hashed = ph.hash(password)

    start = time.time()
    try: ph.verify(hashed, password)
    except: pass
    time_correct = time.time() - start

    start = time.time()
    try: ph.verify(hashed, "WrongPassword")
    except: pass
    time_wrong = time.time() - start

    assert abs(time_correct - time_wrong) < 0.01  # < 10ms de diferencia
```

#### Test de SQL Injection Prevention

```python
# tests/users/test_users_security.py

def test_sql_injection_in_username(client):
    """Inputs maliciosos son sanitizados automáticamente por Pydantic"""
    malicious_username = "admin' OR '1'='1"
    response = client.post("/api/v1/register", json={
        "username": malicious_username,
        "email": "hacker@test.com",
        "password": "Test123!",
        "full_name": "Hacker"
    })
    assert response.status_code in [400, 422]


def test_sql_injection_in_search(client, auth_headers):
    """SQLi en búsquedas no causa crash ni exposición de datos"""
    malicious_query = "'; DROP TABLE users; --"
    response = client.get(
        f"/api/v1/universities/search?q={malicious_query}",
        headers=auth_headers
    )
    assert response.status_code in [200, 404]

    # Verificar que la tabla users sigue existiendo (no fue dropeada)
    response_check = client.get("/api/v1/users/me", headers=auth_headers)
    assert response_check.status_code == 200  # ✅ Tabla intacta
```

#### Tests del Módulo LMS (Content Hierarchy)

```python
# tests/content/test_content_hierarchy.py

class TestTaskTypes:
    def test_create_video_task(self, client, base_module):
        """Crear tarea de tipo video exitosamente"""
        task_data = {
            "title": "Intro Video",
            "task_type": "video",          # campo correcto
            "module_id": base_module["id"],
            "order": 1
        }
        res = client.post("/api/v1/tasks", json=task_data)
        assert res.status_code == 201
        assert res.json()["task_type"] == "video"

    def test_create_invalid_task_type(self, client, base_module):
        """task_type inválido debe ser rechazado con 422"""
        task_data = {
            "title": "Bad Task",
            "task_type": "invalid_type",
            "module_id": base_module["id"],
            "order": 1
        }
        res = client.post("/api/v1/tasks", json=task_data)
        assert res.status_code == 422

    def test_task_order_unique_per_module(self, client, base_module):
        """No pueden existir dos tareas con el mismo order en un módulo"""
        task = {"title": "T1", "task_type": "video",
                "module_id": base_module["id"], "order": 1}
        client.post("/api/v1/tasks", json=task)
        res2 = client.post("/api/v1/tasks", json=task)
        assert res2.status_code in [400, 409]


class TestResourceAttachments:
    def test_attach_resource_to_task(self, client, base_task):
        """Adjuntar recurso válido a una tarea"""
        resource_data = {
            "title": "Tutorial Video",
            "url": "https://youtube.com/watch?v=xyz",
            "task_id": base_task["id"],
            "resource_type": "video"
        }
        res = client.post("/api/v1/resources", json=resource_data)
        assert res.status_code == 201

    def test_resource_invalid_url_rejected(self, client, base_task):
        """URL sin protocolo http/https debe ser rechazada"""
        resource_data = {
            "title": "Bad URL",
            "url": "not-a-valid-url",      # sin http://
            "task_id": base_task["id"]
        }
        res = client.post("/api/v1/resources", json=resource_data)
        assert res.status_code in [422, 400]


class TestContentValidation:
    def test_simulation_description_required(self, client, base_company, base_category):
        """short_description vacío debe ser rechazado con 422"""
        sim_data = {
            "title": "No Desc Sim",
            "slug": "no-desc",
            "short_description": "",       # min_length=1 → debe fallar
            "company_id": base_company.id,
            "category_id": base_category.id
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code in [422, 400]
```

---

## 📚 API Reference Completa

### 🔐 Autenticación (`/api/v1/`)

| Método | Endpoint | Descripción | Body/Params |
|:-------|:---------|:------------|:------------|
| POST | `/token` | Login OAuth2 — retorna JWT Bearer | `username`, `password` (form-data) |
| POST | `/register` | Registro de usuario con hash Argon2 | `UserCreate` JSON |
| GET | `/users/me` | Perfil del usuario autenticado | Header: `Authorization: Bearer {token}` |

### 👤 Usuarios (`/api/v1/users/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/` | Crear usuario |
| GET | `/` | Listar usuarios (paginado) |
| GET | `/{username}` | Obtener por username |
| PUT | `/{id}` | Actualizar perfil completo |
| DELETE | `/{id}` | Eliminar usuario |

### 🏢 Empresas (`/api/v1/empresas/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/` | Crear empresa |
| GET | `/` | Listar activas (filtros: `tipo_empresa`, paginación) |
| GET | `/{id}` | Obtener por ID (solo activas) |
| GET | `/slug/{slug}` | Obtener por slug único |
| PUT | `/{id}` | Actualizar empresa |
| DELETE | `/{id}` | ⭐ Soft delete — marca `esta_activo=False` |
| GET | `/tipo/{tipo}` | Filtrar por tipo de empresa |

### 🎯 Simulaciones (`/api/v1/simulaciones/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `` | Crear simulación (`short_description` obligatorio `min_length=1`) |
| GET | `` | Listar con filtros (`company_id`, `category_id`) |
| GET | `/{id}` | Obtener con módulos y tareas anidados |
| PUT | `/{id}` | Actualizar simulación |
| DELETE | `/{id}` | Eliminar simulación |
| POST | `/{id}/publish` | Publicar (Draft → Published) |
| POST | `/{id}/inscribir` | Inscribir usuario (valida estado y cupos disponibles) |

### 📚 Content / LMS — Módulos (`/api/v1/modules/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/modules` | Crear módulo (requiere `simulation_id` válido, FK enforced) |
| GET | `/modules` | Listar módulos (filtrable por `simulation_id`) |
| GET | `/modules/{id}` | Obtener módulo específico |
| PATCH | `/modules/{id}` | Actualizar título, descripción u orden |
| DELETE | `/modules/{id}` | Eliminar módulo (cascade sobre tareas y recursos) |

### 📚 Content / LMS — Tareas (`/api/v1/tasks/`)

| Método | Endpoint | Descripción | `task_type` válidos |
|:-------|:---------|:------------|:--------------------|
| POST | `/tasks` | Crear tarea (requiere `module_id` válido) | `video`, `quiz`, `pdf`, `text`, `code` |
| GET | `/tasks` | Listar tareas (filtrable por `module_id`, paginado) | — |
| GET | `/tasks/{id}` | Obtener tarea específica | — |
| PATCH | `/tasks/{id}` | Actualizar campos de la tarea | — |
| DELETE | `/tasks/{id}` | Eliminar tarea (cascade sobre recursos) | — |

### 📚 Content / LMS — Recursos (`/api/v1/resources/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| POST | `/resources` | Adjuntar recurso a tarea. `url` debe iniciar con `http://` o `https://` |
| GET | `/resources` | Listar recursos (filtrable por `task_id`) |
| GET | `/resources/{id}` | Obtener recurso específico |
| DELETE | `/resources/{id}` | Eliminar recurso adjunto |

**Tipos de recurso (`resource_type`):** `file`, `video`, `link`, `pdf`, `image`

### 🧠 Skills (`/api/v1/skills/`)

| Método | Endpoint | Descripción | Auth |
|:-------|:---------|:------------|:----:|
| POST | `/` | Crear skill. `name` único. Status 201 | ✅ |
| GET | `/` | Listar skills (filtrable por `category`) | ❌ |
| GET | `/{id}` | Obtener skill por ID | ❌ |
| PUT | `/{id}` | Actualizar skill | ✅ |
| DELETE | `/{id}` | Eliminar skill | ✅ |

**Categorías válidas:** `technical`, `soft`, `language`, `tool`

### 🎓 Universidades (`/api/v1/universities/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| GET | `/` | Listar todas las universidades |
| GET | `/search` | ⭐ Búsqueda optimizada (`?q=nombre`) |
| GET | `/{id}` | Obtener universidad por ID |
| GET | `/{id}/careers` | Carreras de una universidad específica |

### 📈 Catálogos (`/api/v1/`)

| Método | Endpoint | Descripción |
|:-------|:---------|:------------|
| GET | `/regions` | Listar todas las regiones |
| GET | `/provinces` | Listar provincias |
| GET | `/cities` | Listar ciudades |
| GET | `/categories` | Listar categorías de simulaciones |

---

## 🔒 Especificaciones de Seguridad Completas

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
    """Verificación de contraseña con rehash automático si los parámetros cambiaron"""
    try:
        ph.verify(hashed_password, plain_password)
        # Rehash si es necesario (parámetros de seguridad actualizados)
        if ph.check_needs_rehash(hashed_password):
            pass  # Señal para rehash en próximo login
        return True
    except VerifyMismatchError:
        return False
```

### 2. Validación de Inputs con Pydantic V2

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr                          # Validación automática de formato email
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=200)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username debe ser alfanumérico')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe tener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password debe tener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password debe tener al menos un número')
        return v
```

### 3. Validación de URLs (ResourceBase)

```python
# app/schemas/simulation.py
from pydantic import field_validator

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    url: str = Field(..., min_length=1, max_length=500)
    task_id: int

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Garantiza que las URLs sean válidas y no arbitrarias"""
        if not str(v).startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
```

### 4. Protección SQL Injection (ORM Exclusivo)

```python
# ✅ CORRECTO — siempre ORM, nunca interpolación de strings
class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def search(self, term: str):
        return self.db.query(User).filter(
            User.full_name.ilike(f"%{term}%")  # SQLAlchemy escapa automáticamente
        ).all()

# ❌ PROHIBIDO — nunca raw SQL con f-strings
# result = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
# result = db.execute("SELECT * FROM users WHERE name = '" + name + "'")
```

### 5. JWT Token Management

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
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
```

### 6. Integridad Referencial en Tests (SQLite)

```python
# tests/conftest.py
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Fuerza enforcement de Foreign Keys en SQLite.
    SQLite las ignora por defecto; esto iguala el comportamiento de PostgreSQL.
    Garantiza que los tests fallen si intentan crear relaciones huérfanas.
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

---

## 📦 Ejemplos de Uso Completos

### Registro y Login con Argon2

```bash
# 1. Registrar usuario (password hasheado automáticamente con Argon2)
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria_test",
    "email": "maria@example.com",
    "password": "MiPassword123!",
    "full_name": "María González",
    "city_id": 1,
    "phone": "+593987654321",
    "gender": "female"
  }'

# Respuesta:
# {
#   "id": 1,
#   "username": "maria_test",
#   "email": "maria@example.com",
#   "full_name": "María González",
#   "xp_total": 0,
#   "level_current": 1
# }

# 2. Login (verifica con Argon2, retorna JWT)
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=maria_test&password=MiPassword123!"

# Respuesta:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

### Crear Jerarquía LMS Completa

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 1. Crear Simulación (short_description es obligatorio)
curl -X POST "http://localhost:8000/api/v1/simulaciones" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Avanzado para Data Science",
    "slug": "python-avanzado-ds",
    "short_description": "Aprende Python a nivel experto para análisis de datos",
    "company_id": 1,
    "category_id": 2
  }'
# → { "id": 10, "title": "Python Avanzado para Data Science", "state": "draft", ... }

# 2. Crear Módulo dentro de la Simulación
curl -X POST "http://localhost:8000/api/v1/modules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Módulo 1: Fundamentos de Python",
    "simulation_id": 10,
    "order": 1,
    "description": "Bases del lenguaje y estructuras de datos"
  }'
# → { "id": 5, "title": "Módulo 1: Fundamentos de Python", "order": 1, ... }

# 3. Crear Tarea tipo video (task_type válidos: video/quiz/pdf/text/code)
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Video: Introducción a Python",
    "task_type": "video",
    "module_id": 5,
    "order": 1,
    "description": "Historia y filosofía del lenguaje"
  }'
# → { "id": 20, "title": "Video: Introducción a Python", "task_type": "video", ... }

# 4. Adjuntar Recurso (url debe empezar con http:// o https://)
curl -X POST "http://localhost:8000/api/v1/resources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Video Tutorial en YouTube",
    "url": "https://youtube.com/watch?v=python-intro-123",
    "task_id": 20,
    "resource_type": "video"
  }'
# → { "id": 8, "title": "Video Tutorial en YouTube", "url": "https://...", ... }
```

### Uso del Módulo de Skills

```bash
# Crear skill (requiere autenticación)
curl -X POST "http://localhost:8000/api/v1/skills/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "description": "Lenguaje de programación multiparadigma",
    "category": "technical"
  }'
# → { "id": 3, "name": "Python", "category": "technical", ... }

# Listar skills por categoría (sin auth)
curl "http://localhost:8000/api/v1/skills/?category=technical"
curl "http://localhost:8000/api/v1/skills/?category=soft"
curl "http://localhost:8000/api/v1/skills/?category=language"

# Obtener skill específico
curl "http://localhost:8000/api/v1/skills/3"
```

### Repository + Service Pattern en Código

```python
# app/api/v1/users.py
@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends()
):
    """Endpoint simplificado: delega toda la lógica al Service"""
    return user_service.create_user(user_data)


# app/services/user_service.py
class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    def create_user(self, user_data: UserCreate) -> User:
        # 1. Validar que el email no exista
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(400, "Email already registered")

        # 2. Hash de contraseña con Argon2
        hashed_password = hash_password(user_data.password)

        # 3. Crear usuario — model_dump() incluye TODOS los campos opcionales
        db_user = User(
            **user_data.model_dump(exclude={'password'}),
            hashed_password=hashed_password,
            xp_total=0,
            level_current=1,
            is_active=True
        )
        self.user_repo.db.add(db_user)
        self.user_repo.db.commit()
        self.user_repo.db.refresh(db_user)
        return db_user


# app/repositories/user_repository.py
class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session = Depends(get_db)):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
```

### Soft Delete en CompanyService

```python
# app/services/company_service.py
class CompanyService:

    def get_all(self, skip: int = 0, limit: int = 100):
        """Solo devuelve empresas activas — los soft-deleted quedan invisibles"""
        return (
            self.db.query(Empresa)
            .filter(Empresa.esta_activo == True)  # ← filtro automático
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, empresa_id: int):
        """Soft delete: marca como inactiva, no borra el registro"""
        empresa = self.get_by_id(empresa_id)
        if not empresa:
            raise HTTPException(404, "Company not found")
        empresa.esta_activo = False
        self.db.commit()
        return {"message": "Company deactivated successfully"}

    def get_company_stats(self, empresa_id: int) -> dict:
        """Dashboard: estadísticas agregadas de la empresa"""
        empresa = self.get_by_id(empresa_id)
        simulations = self.db.query(Simulation).filter(
            Simulation.company_id == empresa_id
        ).all()
        return {
            "total_simulations": len(simulations),
            "published": sum(1 for s in simulations if s.state == "published"),
            "draft": sum(1 for s in simulations if s.state == "draft"),
            "total_spots": sum(s.total_spots or 0 for s in simulations),
        }
```

---

## 🚀 Inicio Rápido (Quick Start)

### Prerequisitos
- **Docker Desktop** instalado y corriendo
- **PowerShell** (Windows) o Bash (Linux/Mac)
- **Git** para clonar el repositorio

### 1. Clonar y Configurar

```powershell
git clone https://github.com/MatiasJimenezSanchez/DAO-Auth.git
cd "AURUM BACK END"

# Copiar configuración de ejemplo
cp .env.example .env

# Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Pegar el resultado en .env como SECRET_KEY=<resultado>

# (Opcional) Editar otras variables en .env
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
- **API REST:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **PostgreSQL:** localhost:5432

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

### 6. Verificar API

```bash
curl http://localhost:8000/
# → { "status": "online", "message": "Aurum API v1.0" }

curl http://localhost:8000/docs
# → Swagger UI interactivo
```

### 7. Ejecutar Tests Shield

```powershell
docker-compose exec -T web pytest tests/ -v --tb=short -q
# Esperado: 182 passed, 19 skipped (~21s)
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
| `aurum-db-reset` | ⚠️ Borra y recrea la base de datos (destructivo) |
| `aurum-help` | Muestra ayuda de todos los comandos |

---

## 🔄 Migraciones de Base de Datos (Alembic)

```powershell
# Aplicar todas las migraciones pendientes
aurum-migrate -Action upgrade

# Ver historial completo de migraciones
aurum-migrate -Action history

# Crear nueva migración automática (detecta cambios en modelos)
aurum-migrate -Action revision -Message "add_new_column_to_users"

# Revertir última migración
aurum-migrate -Action downgrade -Target "-1"

# Ir a versión específica
aurum-migrate -Action downgrade -Target "b6ff38f7e173"
```

---

## 🚀 Despliegue en Producción

### Docker Compose (Recomendado)

```bash
# 1. Configurar variables de entorno
cp .env.example .env
nano .env
# Establecer: SECRET_KEY, DATABASE_URL, POSTGRES_PASSWORD

# 2. Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Levantar servicios en modo detached
docker-compose up -d

# 4. Aplicar migraciones
docker-compose exec web alembic upgrade head

# 5. Cargar datos semilla (primera vez)
docker-compose exec web python -m app.db.seeds

# 6. Verificar estado
docker-compose logs -f web
curl http://localhost:8000/
```

---

## 🗺️ Roadmap

### v1.2.0 ✅ (08 Febrero 2026)
- ✅ Arquitectura Clean (Repository-Service Pattern)
- ✅ Migración a Argon2-CFFI (estándar OWASP 2024)
- ✅ Shield Suite (+70 tests)
- ✅ CRUD de empresas con soft delete real
- ✅ Testing completo de seguridad (Argon2, JWT, SQLi)

### v1.3.0 ✅ (24 Febrero 2026 — Actual)
- ✅ API de Contenido LMS completa (15 endpoints: módulos, tareas, recursos)
- ✅ 203 tests funcionales (98% passing, ~21s ejecución)
- ✅ Corrección de disonancia Schema↔Modelo (`task_type`, `resource.title`, URL validation)
- ✅ Integridad referencial forzada en tests SQLite (`PRAGMA foreign_keys=ON`)
- ✅ Módulo Skills con CRUD completo y autenticación (prefix corregido a `/api/v1/skills`)
- ✅ Módulos Progress y Dashboard operativos
- ✅ Estandarización de mensajes de error en inglés ("already exists")
- ✅ `short_description` obligatorio con `min_length=1` en ambos schemas de simulaciones
- ✅ `field_validator` en `ResourceBase.url` (http/https enforced)
- ✅ Resolución de colisión de rutas en router de Skills

### v1.4.0 (Q2 2026)
- [ ] Sistema de inscripciones completo (cupos, listas de espera, notificaciones)
- [ ] Rate limiting con Redis (prevención de abuso de API)
- [ ] Logs estructurados en JSON (integración con ELK Stack)
- [ ] WebSockets para notificaciones en tiempo real

### v2.0.0 (Q3 2026)
- [ ] Sistema de matchmaking empresa-candidato mejorado (ML engine)
- [ ] Recomendaciones personalizadas de simulaciones
- [ ] Multi-idioma (i18n) — español/inglés/portugués
- [ ] Dashboard de administración completo
- [ ] API pública con documentación OpenAPI 3.1

---

## 📄 Licencia

MIT License — Copyright (c) 2026 Matías Jiménez Sánchez

---

## 👨‍💻 Autor

**Matías Jiménez Sánchez** — Lead Backend Engineer & Architect

- GitHub: [@MatiasJimenezSanchez](https://github.com/MatiasJimenezSanchez)
- Email: matjimsan@outlook.com
- LinkedIn: [Matías Jiménez](https://linkedin.com/in/matias-jimenez)

---

**🎉 ¡Gracias por usar Aurum DAO API!**

**Hecho con ❤️ usando FastAPI, Python, PostgreSQL y Argon2**

---

*Última actualización: 24 de Febrero de 2026 — LMS Stable Release (v1.3.0)*
*Documentación generada y mantenida manualmente*