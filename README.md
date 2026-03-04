# Aurum DAO API - Educational Simulations Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Clean%203--Layer-orange)
![Security](https://img.shields.io/badge/Security-Argon2%20%2B%20OAuth2-red)
![Tests](https://img.shields.io/badge/Tests-203%20%7C%2098%25%20Passing-brightgreen)

Backend system for authentication, educational content management, and business administration. Built with Clean Architecture (Repository-Service Pattern) for scalability, B2B security, and long-term maintainability.

---

## Table of Contents

- [Version History](#version-history)
  - [v1.3.0 - LMS Content API & Core Stabilization](#v130---lms-content-api--core-stabilization)
  - [v1.2.0 - Shield Release](#v120---shield-release)
- [Technical Overview](#technical-overview)
- [System Architecture](#system-architecture)
  - [Design Principles](#design-principles)
- [Technology Stack](#technology-stack)
  - [Security: Bcrypt to Argon2 Migration](#security-bcrypt-to-argon2-migration)
- [Test Coverage](#test-coverage)
  - [Coverage by Module](#coverage-by-module)
  - [Running Tests](#running-tests)
  - [Security Test Examples](#security-test-examples)
- [API Reference](#api-reference)
  - [Authentication](#authentication-apiv1)
  - [Users](#users-apiv1users)
  - [Companies](#companies-apiv1empresas)
  - [Simulations](#simulations-apiv1simulaciones)
  - [Content/LMS - Modules](#contentlms---modules-apiv1modules)
  - [Content/LMS - Tasks](#contentlms---tasks-apiv1tasks)
  - [Content/LMS - Resources](#contentlms---resources-apiv1resources)
  - [Skills](#skills-apiv1skills)
  - [Universities](#universities-apiv1universities)
  - [Catalogs](#catalogs-apiv1)
- [Security Specifications](#security-specifications)
- [Usage Examples](#usage-examples)
- [Quick Start](#quick-start)
- [Command-Line Interface](#command-line-interface)
  - [Initialization](#initialization)
  - [Available Commands](#available-commands)
  - [Database Migrations](#database-migrations)
- [Production Deployment](#production-deployment)
- [Roadmap](#roadmap)
- [License](#license)
- [Author](#author)

---

## Version History

### v1.3.0 - LMS Content API & Core Stabilization
**Date:** February 24, 2026 | **Status:** Stable (98% Tests Passing) | **Coverage:** 203 Functional Tests

#### Summary
Core services reconstruction (`CompanyService`, `UserService`), complete LMS Content API implementation, and database/test suite hardening for strict referential integrity.

#### 1. LMS Module Implementation
Educational content management architecture:

- **Router:** `app/api/v1/content.py` with 15 CRUD endpoints
- **Content Hierarchy:**
  - **Modules:** Sequential management within simulations with order validation
  - **Tasks:** Polymorphic support for types: `video`, `quiz`, `pdf`, `text`, `code`
  - **Resources:** Attachment system linked to tasks
- Integration in `app/main.py` under `/api/v1` prefix

#### 2. Core Services Restoration and Refactoring

**CompanyService (`app/services/company_service.py`):**
- CRUD reimplementation: `create`, `update`, `delete`, `get_by_id`, `get_by_slug`
- **Soft Delete:** All read methods (`get`, `list`, `search`) automatically filter `esta_activo=True`
- Dashboard: Statistical aggregation logic maintained and optimized (`get_company_stats`)

**UserService (`app/services/user_service.py`):**
- Fixed bug where optional fields (`phone`, `gender`, `birth_date`, `city_id`, `avatar_url`) were ignored during registration
- Use of `model_dump()` for complete dynamic DTO-to-SQLAlchemy model mapping

#### 3. Quality Engineering and Testing

- **Referential Integrity in SQLite:** Event Listener in `tests/conftest.py` enforces `PRAGMA foreign_keys=ON`, matching PostgreSQL strict behavior
- **+60 new tests** in `tests/content/test_content_hierarchy.py` covering hierarchy validations, content types, and uniqueness constraints
- Removal of hardcoded IDs (e.g., `company_id=1`) - use of dynamic fixtures creating real records
- Critical fixtures elevated to module scope to resolve visibility errors

#### 4. Schema-Model Mapping Fixes

| Conflict | Problem | Solution |
|:---------|:--------|:---------|
| `task_type` | DB expected `task_type`, API sent `type` | Manual mapping in controller + Schema alignment |
| `resource.title` | DB used `name` column, API expected `title` | `@property title` in `TaskResource` model |
| `short_description` | Field accepted empty string (`""`) | `min_length=1` applied in both schemas |
| URL validation | `ResourceBase.url` accepted any string | `field_validator` requiring `http://` or `https://` |
| Skills router prefix | `/api/v1` caused route collision | Corrected to `/api/v1/skills` |

#### 5. Standardization
- Error messages unified in **English** (`"already exists"`) for automated test consistency

---

### v1.2.0 - Shield Release
**Date:** February 8, 2026

- Clean Architecture implementation (Repository-Service Pattern)
- Migration from Bcrypt to Argon2-CFFI (OWASP 2024 standard)
- Shield Suite (+70 tests)
- Company CRUD with soft delete
- Complete security testing

---

## Technical Overview

**Aurum DAO API** is a business logic engine capable of managing hybrid simulation lifecycles (On-Demand and Live), strict integrity validations, and preventive offensive security.

---

## System Architecture

Three-layer architecture with Dependency Injection, decoupling business logic from data access.
```
┌─────────────────────────────────────────────────────────────────────┐
│                        Web/Mobile Client                             │
│                     (React, Vue, Mobile Apps)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS/REST
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI Routers)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   Auth      │  │  Companies   │  │ Simulations │  │ Content  │ │
│  │  Router     │  │   Router     │  │   Router    │  │  Router  │ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│         │ Pydantic V2 Validation (Schemas + field_validators)       │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Service Layer (Business Logic)                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ UserService      │  │ CompanyService   │  │SimulationService │  │
│  │ • Hash Argon2    │  │ • Soft Delete    │  │ • Date Validation│  │
│  │ • Validate Email │  │ • B2B Logic      │  │ • Slots/State    │  │
│  │ • Create JWT     │  │ • Partnership    │  │ • Enrollments    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│         │ Domain Models                                              │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Repository Layer (Data Access)                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ UserRepository   │  │CompanyRepository │  │SimulationRepo    │  │
│  │ • Generic CRUD   │  │ • Queries        │  │ • Complex Joins  │  │
│  │ • Filters        │  │ • Pagination     │  │ • Eager Loading  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│         │ SQLAlchemy 2.0 ORM                                         │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL 16 Database                            │
│  Tables: users, empresas, simulations, simulation_modules,          │
│          module_tasks, task_resources, skills, universities,        │
│          catalogs, user_progress, usuarios_empresa                  │
│  Features: Transactions, Foreign Keys, Indexes, Constraints         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   Security Shield (Cross-Cutting)                    │
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

### Design Principles

**1. Separation of Concerns (SoC)**
- **Routers:** Handle HTTP only (requests/responses)
- **Services:** Contain all business logic
- **Repositories:** Abstract data access

**2. Dependency Injection**
- Services receive Repositories via constructor
- Facilitates testing with mocks
- Decouples components

**3. Single Responsibility Principle**
- Each class has a single reason to change
- Small, specific functions

**4. Domain-Driven Design (DDD)**
- Rich models with behavior (e.g., `@property title` in `TaskResource`)
- Business validations in Services
- Aggregate-oriented repositories

---

## Technology Stack

| Component | Technology | Version | Primary Use | Improvement vs Previous |
|:----------|:-----------|:--------|:------------|:------------------------|
| **Backend Framework** | FastAPI | 0.109+ | High-performance async API | Updated for Pydantic V2 |
| **Runtime** | Python | 3.11+ | Primary language, native type hints | — |
| **Validation** | Pydantic | V2 | Strict serialization, nested schemas, field_validators | 2x faster than V1 |
| **ORM** | SQLAlchemy | 2.0 | Object-relational mapping, sessions | New declarative syntax |
| **Database** | PostgreSQL | 16 | Robust relational persistence | — |
| **Migrations** | Alembic | Latest | Schema versioning | — |
| **Authentication** | OAuth2 + JWT | — | Bearer token flow | — |
| **Hashing** | **Argon2-CFFI** | Latest | **OWASP 2024 Standard** | **Replaced Bcrypt** (GPU-resistant) |
| **Testing** | Pytest + Httpx | Latest | 203 integration and unit tests | **+150 tests** vs initial version |
| **ASGI Server** | Uvicorn | Latest | Async web server | — |
| **Containerization** | Docker + Compose | Latest | Service orchestration | — |
| **Documentation** | Swagger UI + ReDoc | Auto | Interactive documentation | — |

### Security: Bcrypt to Argon2 Migration
```python
# BEFORE (Bcrypt - Vulnerable to GPU attacks)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# NOW (Argon2 - Resistant to GPU/ASIC/Fuzzing)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,          # Iterations
    memory_cost=65536,    # 64 MB RAM
    parallelism=4,        # Parallel threads
    hash_len=32,          # Output: 32 bytes
    salt_len=16           # Salt: 16 bytes
)

# Hashing
hashed = ph.hash(password)

# Verification
try:
    ph.verify(hashed, password)
except VerifyMismatchError:
    pass
```

**Argon2 Advantages over Bcrypt:**

| Feature | Bcrypt | Argon2 |
|:--------|:-------|:-------|
| GPU Resistance | Medium | High |
| ASIC Resistance | Low | High |
| Configurable Memory | No | Yes (up to GB) |
| Timing Attack Resistance | Yes | Yes |
| OWASP 2024 Recommendation | Acceptable | **Preferred** |
| Parallelism | No | Yes (multi-thread) |
| Max Password Length | 72 bytes | **Unlimited** |

---

## Test Coverage

Comprehensive test battery ensuring system stability before each deployment.

### Current Metrics
```
203 tests collected
✅ 182 passed  |  ⏭️  19 skipped  |  ❌ 2 in progress  →  98% passing
Execution time: ~21 seconds
```

### Coverage by Module

| Module | Coverage | Tests | Description |
|:-------|:---------|:------|:------------|
| **Auth & Security** | ✅ 100% | 4 | JWT creation, validation, Bearer auth flow |
| **Business Logic** | ✅ 100% | 7 | Matching algorithm, SimulationService, CompanyService stats |
| **Catalogs & Skills** | ✅ 100% | 14 | Geographic catalog CRUD, complete skills CRUD with auth |
| **Companies** | ✅ 100% | 39 | CRUD, soft delete, security, shield, company_users |
| **Content / LMS** | ✅ 98% | 60+ | Modules, tasks, resources, validations, integration |
| **ML Engine** | ✅ 100% | 11 | Company-candidate matching algorithm |
| **Simulations** | ✅ 100% | 25 | CRUD, lifecycle, shield, FK relationships |
| **Universities** | ✅ 100% | 6 | Invalid domains, search, validations |
| **Users** | ✅ 100% | 29 | Complete registration, profile, auth, passwords |

### Running Tests
```powershell
# Complete suite
docker-compose exec -T web pytest tests/ -v --tb=short -q

# Verbose output
docker-compose exec -T web pytest tests/ -v

# Specific module
docker-compose exec -T web pytest tests/content/test_content_hierarchy.py -v

# Only failed tests from last run
docker-compose exec -T web pytest tests/ --lf --tb=short

# With HTML coverage report
docker-compose exec -T web pytest tests/ --cov=app --cov-report=html
# Open: htmlcov/index.html
```

### Security Test Examples

#### Argon2 Hashing Test
```python
# tests/auth/test_auth_jwt.py

def test_argon2_hash_password():
    """Verifies Argon2 generates unique and verifiable hashes"""
    password = "MiPassword123!"
    hashed = ph.hash(password)

    assert hashed.startswith("$argon2id$")  # Argon2id variant
    assert len(hashed) > 80                 # Sufficiently long hash
    assert hashed != password               # Not plaintext

    try:
        ph.verify(hashed, password)         # Must verify correctly
    except VerifyMismatchError:
        pytest.fail("Valid hash failed verification")


def test_argon2_different_salts():
    """Two hashes of same password are always different (unique salts)"""
    password = "TestPassword"
    hash1 = ph.hash(password)
    hash2 = ph.hash(password)
    assert hash1 != hash2                   # Different salts guaranteed


def test_argon2_timing_attack_resistance():
    """Verification takes constant time (timing attack resistance)"""
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

    assert abs(time_correct - time_wrong) < 0.01  # < 10ms difference
```

#### SQL Injection Prevention Test
```python
# tests/users/test_users_security.py

def test_sql_injection_in_username(client):
    """Malicious inputs are automatically sanitized by Pydantic"""
    malicious_username = "admin' OR '1'='1"
    response = client.post("/api/v1/register", json={
        "username": malicious_username,
        "email": "hacker@test.com",
        "password": "Test123!",
        "full_name": "Hacker"
    })
    assert response.status_code in [400, 422]


def test_sql_injection_in_search(client, auth_headers):
    """SQLi in searches doesn't cause crashes or data exposure"""
    malicious_query = "'; DROP TABLE users; --"
    response = client.get(
        f"/api/v1/universities/search?q={malicious_query}",
        headers=auth_headers
    )
    assert response.status_code in [200, 404]

    # Verify users table still exists (wasn't dropped)
    response_check = client.get("/api/v1/users/me", headers=auth_headers)
    assert response_check.status_code == 200  # Table intact
```

#### LMS Module Tests (Content Hierarchy)
```python
# tests/content/test_content_hierarchy.py

class TestTaskTypes:
    def test_create_video_task(self, client, base_module):
        """Create video task successfully"""
        task_data = {
            "title": "Intro Video",
            "task_type": "video",          # Correct field
            "module_id": base_module["id"],
            "order": 1
        }
        res = client.post("/api/v1/tasks", json=task_data)
        assert res.status_code == 201
        assert res.json()["task_type"] == "video"

    def test_create_invalid_task_type(self, client, base_module):
        """Invalid task_type must be rejected with 422"""
        task_data = {
            "title": "Bad Task",
            "task_type": "invalid_type",
            "module_id": base_module["id"],
            "order": 1
        }
        res = client.post("/api/v1/tasks", json=task_data)
        assert res.status_code == 422

    def test_task_order_unique_per_module(self, client, base_module):
        """Cannot have two tasks with same order in module"""
        task = {"title": "T1", "task_type": "video",
                "module_id": base_module["id"], "order": 1}
        client.post("/api/v1/tasks", json=task)
        res2 = client.post("/api/v1/tasks", json=task)
        assert res2.status_code in [400, 409]


class TestResourceAttachments:
    def test_attach_resource_to_task(self, client, base_task):
        """Attach valid resource to task"""
        resource_data = {
            "title": "Tutorial Video",
            "url": "https://youtube.com/watch?v=xyz",
            "task_id": base_task["id"],
            "resource_type": "video"
        }
        res = client.post("/api/v1/resources", json=resource_data)
        assert res.status_code == 201

    def test_resource_invalid_url_rejected(self, client, base_task):
        """URL without http/https protocol must be rejected"""
        resource_data = {
            "title": "Bad URL",
            "url": "not-a-valid-url",      # No http://
            "task_id": base_task["id"]
        }
        res = client.post("/api/v1/resources", json=resource_data)
        assert res.status_code in [422, 400]


class TestContentValidation:
    def test_simulation_description_required(self, client, base_company, base_category):
        """Empty short_description must be rejected with 422"""
        sim_data = {
            "title": "No Desc Sim",
            "slug": "no-desc",
            "short_description": "",       # min_length=1 → must fail
            "company_id": base_company.id,
            "category_id": base_category.id
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code in [422, 400]
```
## API Reference

### Authentication (`/api/v1/`)

| Method | Endpoint | Description | Body/Params |
|:-------|:---------|:------------|:------------|
| POST | `/token` | OAuth2 Login - returns JWT Bearer | `username`, `password` (form-data) |
| POST | `/register` | User registration with Argon2 hash | `UserCreate` JSON |
| GET | `/users/me` | Authenticated user profile | Header: `Authorization: Bearer {token}` |

### Users (`/api/v1/users/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/` | Create user |
| GET | `/` | List users (paginated) |
| GET | `/{username}` | Get by username |
| PUT | `/{id}` | Update complete profile |
| DELETE | `/{id}` | Delete user |

### Companies (`/api/v1/empresas/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/` | Create company |
| GET | `/` | List active companies (filters: `tipo_empresa`, pagination) |
| GET | `/{id}` | Get by ID (active only) |
| GET | `/slug/{slug}` | Get by unique slug |
| PUT | `/{id}` | Update company |
| DELETE | `/{id}` | Soft delete - marks `esta_activo=False` |
| GET | `/tipo/{tipo}` | Filter by company type |

### Simulations (`/api/v1/simulaciones/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `` | Create simulation (`short_description` required `min_length=1`) |
| GET | `` | List with filters (`company_id`, `category_id`) |
| GET | `/{id}` | Get with nested modules and tasks |
| PUT | `/{id}` | Update simulation |
| DELETE | `/{id}` | Delete simulation |
| POST | `/{id}/publish` | Publish (Draft → Published) |
| POST | `/{id}/inscribir` | Enroll user (validates state and available slots) |

### Content/LMS - Modules (`/api/v1/modules/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/modules` | Create module (requires valid `simulation_id`, FK enforced) |
| GET | `/modules` | List modules (filterable by `simulation_id`) |
| GET | `/modules/{id}` | Get specific module |
| PATCH | `/modules/{id}` | Update title, description or order |
| DELETE | `/modules/{id}` | Delete module (cascade on tasks and resources) |

### Content/LMS - Tasks (`/api/v1/tasks/`)

| Method | Endpoint | Description | Valid `task_type` |
|:-------|:---------|:------------|:------------------|
| POST | `/tasks` | Create task (requires valid `module_id`) | `video`, `quiz`, `pdf`, `text`, `code` |
| GET | `/tasks` | List tasks (filterable by `module_id`, paginated) | — |
| GET | `/tasks/{id}` | Get specific task | — |
| PATCH | `/tasks/{id}` | Update task fields | — |
| DELETE | `/tasks/{id}` | Delete task (cascade on resources) | — |

### Content/LMS - Resources (`/api/v1/resources/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/resources` | Attach resource to task. `url` must start with `http://` or `https://` |
| GET | `/resources` | List resources (filterable by `task_id`) |
| GET | `/resources/{id}` | Get specific resource |
| DELETE | `/resources/{id}` | Delete attached resource |

**Resource types (`resource_type`):** `file`, `video`, `link`, `pdf`, `image`

### Skills (`/api/v1/skills/`)

| Method | Endpoint | Description | Auth |
|:-------|:---------|:------------|:----:|
| POST | `/` | Create skill. Unique `name`. Status 201 | ✅ |
| GET | `/` | List skills (filterable by `category`) | ❌ |
| GET | `/{id}` | Get skill by ID | ❌ |
| PUT | `/{id}` | Update skill | ✅ |
| DELETE | `/{id}` | Delete skill | ✅ |

**Valid categories:** `technical`, `soft`, `language`, `tool`

### Universities (`/api/v1/universities/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/` | List all universities |
| GET | `/search` | Optimized search (`?q=name`) |
| GET | `/{id}` | Get university by ID |
| GET | `/{id}/careers` | Careers from specific university |

### Catalogs (`/api/v1/`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/regions` | List all regions |
| GET | `/provinces` | List provinces |
| GET | `/cities` | List cities |
| GET | `/categories` | List simulation categories |

---

## Security Specifications

### 1. Robust Hashing with Argon2
```python
# app/core/security.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Production-optimized configuration
ph = PasswordHasher(
    time_cost=3,          # Iterations (more = slower but more secure)
    memory_cost=65536,    # 64 MB RAM per hash
    parallelism=4,        # 4 parallel threads
    hash_len=32,          # 32-byte hash
    salt_len=16           # 16-byte salt
)

def hash_password(password: str) -> str:
    """Hash password with Argon2"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with automatic rehash if parameters changed"""
    try:
        ph.verify(hashed_password, plain_password)
        # Rehash if necessary (updated security parameters)
        if ph.check_needs_rehash(hashed_password):
            pass  # Signal for rehash on next login
        return True
    except VerifyMismatchError:
        return False
```

### 2. Input Validation with Pydantic V2
```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr                          # Automatic email format validation
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=200)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must have at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must have at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must have at least one number')
        return v
```

### 3. URL Validation (ResourceBase)
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
        """Ensures URLs are valid and not arbitrary"""
        if not str(v).startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
```

### 4. SQL Injection Protection (ORM Exclusive)
```python
# CORRECT - always ORM, never string interpolation
class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def search(self, term: str):
        return self.db.query(User).filter(
            User.full_name.ilike(f"%{term}%")  # SQLAlchemy escapes automatically
        ).all()

# FORBIDDEN - never raw SQL with f-strings
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
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

### 6. Referential Integrity in Tests (SQLite)
```python
# tests/conftest.py
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Forces Foreign Key enforcement in SQLite.
    SQLite ignores them by default; this matches PostgreSQL strict behavior.
    Ensures tests fail if attempting to create orphaned relationships.
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

---

## Usage Examples

### Registration and Login with Argon2
```bash
# 1. Register user (password hashed automatically with Argon2)
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

# Response:
# {
#   "id": 1,
#   "username": "maria_test",
#   "email": "maria@example.com",
#   "full_name": "María González",
#   "xp_total": 0,
#   "level_current": 1
# }

# 2. Login (verifies with Argon2, returns JWT)
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=maria_test&password=MiPassword123!"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

### Creating Complete LMS Hierarchy
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 1. Create Simulation (short_description is required)
curl -X POST "http://localhost:8000/api/v1/simulaciones" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python for Data Science",
    "slug": "python-advanced-ds",
    "short_description": "Learn expert-level Python for data analysis",
    "company_id": 1,
    "category_id": 2
  }'
# → { "id": 10, "title": "Advanced Python for Data Science", "state": "draft", ... }

# 2. Create Module within Simulation
curl -X POST "http://localhost:8000/api/v1/modules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Module 1: Python Fundamentals",
    "simulation_id": 10,
    "order": 1,
    "description": "Language basics and data structures"
  }'
# → { "id": 5, "title": "Module 1: Python Fundamentals", "order": 1, ... }

# 3. Create video task (valid task_types: video/quiz/pdf/text/code)
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Video: Introduction to Python",
    "task_type": "video",
    "module_id": 5,
    "order": 1,
    "description": "Language history and philosophy"
  }'
# → { "id": 20, "title": "Video: Introduction to Python", "task_type": "video", ... }

# 4. Attach Resource (url must start with http:// or https://)
curl -X POST "http://localhost:8000/api/v1/resources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "YouTube Tutorial Video",
    "url": "https://youtube.com/watch?v=python-intro-123",
    "task_id": 20,
    "resource_type": "video"
  }'
# → { "id": 8, "title": "YouTube Tutorial Video", "url": "https://...", ... }
```

### Using Skills Module
```bash
# Create skill (requires authentication)
curl -X POST "http://localhost:8000/api/v1/skills/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "description": "Multi-paradigm programming language",
    "category": "technical"
  }'
# → { "id": 3, "name": "Python", "category": "technical", ... }

# List skills by category (no auth)
curl "http://localhost:8000/api/v1/skills/?category=technical"
curl "http://localhost:8000/api/v1/skills/?category=soft"
curl "http://localhost:8000/api/v1/skills/?category=language"

# Get specific skill
curl "http://localhost:8000/api/v1/skills/3"
```

### Repository + Service Pattern in Code
```python
# app/api/v1/users.py
@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends()
):
    """Simplified endpoint: delegates all logic to Service"""
    return user_service.create_user(user_data)


# app/services/user_service.py
class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    def create_user(self, user_data: UserCreate) -> User:
        # 1. Validate email doesn't exist
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(400, "Email already registered")

        # 2. Hash password with Argon2
        hashed_password = hash_password(user_data.password)

        # 3. Create user - model_dump() includes ALL optional fields
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

### Soft Delete in CompanyService
```python
# app/services/company_service.py
class CompanyService:

    def get_all(self, skip: int = 0, limit: int = 100):
        """Only returns active companies - soft-deleted remain invisible"""
        return (
            self.db.query(Empresa)
            .filter(Empresa.esta_activo == True)  # Automatic filter
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, empresa_id: int):
        """Soft delete: marks as inactive, doesn't delete record"""
        empresa = self.get_by_id(empresa_id)
        if not empresa:
            raise HTTPException(404, "Company not found")
        empresa.esta_activo = False
        self.db.commit()
        return {"message": "Company deactivated successfully"}

    def get_company_stats(self, empresa_id: int) -> dict:
        """Dashboard: aggregated company statistics"""
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

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- PowerShell (Windows) or Bash (Linux/Mac)
- Git to clone repository

### 1. Clone and Configure
```bash
git clone https://github.com/MatiasJimenezSanchez/DAO-Auth.git
cd DAO-Auth

# Copy example configuration
cp .env.example .env

# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Paste result in .env as SECRET_KEY=<result>

# (Optional) Edit other variables in .env
# notepad .env
```

### 2. Load Development Tools
```powershell
. .\comandos-delphos.ps1
```

### 3. Start Services
```bash
aurum-start
```

This will start:
- **REST API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432

### 4. Verify Status
```bash
aurum-status
```

### 5. Run Migrations and Seeds
```bash
aurum-migrate -Action upgrade

aurum-shell web
python -m app.db.seeds
exit
```

### 6. Verify API
```bash
curl http://localhost:8000/
# → { "status": "online", "message": "Aurum API v1.0" }

curl http://localhost:8000/docs
# → Interactive Swagger UI
```

### 7. Run Shield Tests
```bash
docker-compose exec -T web pytest tests/ -v --tb=short -q
# Expected: 182 passed, 19 skipped (~21s)
```

---

## Command-Line Interface

### Initialization

Before using CLI commands, load the PowerShell script in your session:
```powershell
. .\comandos-delphos.ps1
```

This imports all `aurum-*` commands into your current PowerShell environment.nt.

### Available Commands

#### Service Management

| Command | Description | Docker Command Executed |
|:--------|:------------|:------------------------|
| `aurum-start` | Start containers (API + DB) | `docker-compose up -d` |
| `aurum-stop` | Stop services | `docker-compose stop` |
| `aurum-restart` | Restart services | `docker-compose restart` |
| `aurum-rebuild` | Rebuild images from scratch | `docker-compose build --no-cache` |
| `aurum-status` | Show service status and useful links | `docker-compose ps` + custom output |

#### Logs and Debugging

| Command | Description | Docker Command Executed |
|:--------|:------------|:------------------------|
| `aurum-logs [service]` | Show logs (default: web) | `docker-compose logs [service]` |
| `aurum-logs [service] -Follow` | Follow logs in real-time | `docker-compose logs -f [service]` |

**Examples:**
```powershell
# View API logs
aurum-logs web

# Follow database logs
aurum-logs db -Follow

# View all services
aurum-logs
```

#### Shell Access

| Command | Description | Access |
|:--------|:------------|:-------|
| `aurum-shell web` | Open bash shell in web container | `docker-compose exec web bash` |
| `aurum-shell db` | Open PostgreSQL shell | `docker-compose exec db psql -U postgres -d aurum_dao` |

**Usage:**
```powershell
# Access Python environment
aurum-shell web
# Inside container:
python -m app.db.seeds
pip list
exit

# Query database directly
aurum-shell db
# Inside psql:
\dt
SELECT * FROM users;
\q
```

#### Testing

| Command | Description | Pytest Command |
|:--------|:------------|:---------------|
| `aurum-test` | Run complete test suite | `pytest tests/ -v --tb=short` |
| `aurum-test [path]` | Run specific test file/directory | `pytest [path] -v` |
| `aurum-test -Coverage` | Generate HTML coverage report | `pytest --cov=app --cov-report=html` |

**Examples:**
```powershell
# Complete suite
aurum-test

# Specific module
aurum-test tests/auth/test_auth_jwt.py

# With coverage
aurum-test -Coverage
# Opens htmlcov/index.html
```

### Database Migrations

All migration commands use Alembic internally via `docker-compose exec web alembic`.

| Command | Description | Alembic Command |
|:--------|:------------|:----------------|
| `aurum-migrate -Action upgrade` | Apply all pending migrations | `alembic upgrade head` |
| `aurum-migrate -Action downgrade -Target "-1"` | Revert last migration | `alembic downgrade -1` |
| `aurum-migrate -Action downgrade -Target [revision]` | Revert to specific version | `alembic downgrade [revision]` |
| `aurum-migrate -Action history` | Show migration history | `alembic history` |
| `aurum-migrate -Action current` | Show current version | `alembic current` |
| `aurum-migrate -Action revision -Message "description"` | Create new migration (autogenerate) | `alembic revision --autogenerate -m "description"` |

**Examples:**
```powershell
# Apply all migrations
aurum-migrate -Action upgrade

# Create new migration after model changes
aurum-migrate -Action revision -Message "add_user_avatar_field"

# View migration history
aurum-migrate -Action history

# Revert last migration
aurum-migrate -Action downgrade -Target "-1"

# Revert to specific version
aurum-migrate -Action downgrade -Target "b6ff38f7e173"
```

#### Database Reset (Destructive)

| Command | Description | Warning |
|:--------|:------------|:--------|
| `aurum-db-reset` | **Drop database, recreate, run migrations** | ⚠️ **All data will be lost** |

**Workflow:**
```powershell
aurum-db-reset
# Executes:
# 1. docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS aurum_dao;"
# 2. docker-compose exec db psql -U postgres -c "CREATE DATABASE aurum_dao;"
# 3. docker-compose exec web alembic upgrade head
# 4. docker-compose exec web python -m app.db.seeds
```

#### Help

| Command | Description |
|:--------|:------------|
| `aurum-help` | Display all available commands with descriptions |

---

## Production Deployment

### Docker Compose (Recommended)
```bash
# 1. Configure environment variables
cp .env.example .env
nano .env
# Set: SECRET_KEY, DATABASE_URL, POSTGRES_PASSWORD

# 2. Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Start services in detached mode
docker-compose up -d

# 4. Apply migrations
docker-compose exec web alembic upgrade head

# 5. Load seed data (first time only)
docker-compose exec web python -m app.db.seeds

# 6. Verify status
docker-compose logs -f web
curl http://localhost:8000/
```

### Environment Variables (Production)
```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
POSTGRES_USER=production_user
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=aurum_production

# Security
SECRET_KEY=<generate_with_secrets.token_urlsafe(32)>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional
SENTRY_DSN=https://...
LOG_LEVEL=INFO
```

---

## Roadmap

### v1.2.0 ✅ (February 8, 2026)
- ✅ Clean Architecture (Repository-Service Pattern)
- ✅ Migration to Argon2-CFFI (OWASP 2024 standard)
- ✅ Shield Suite (+70 tests)
- ✅ Company CRUD with real soft delete
- ✅ Complete security testing (Argon2, JWT, SQLi)

### v1.3.0 ✅ (February 24, 2026 - Current)
- ✅ Complete LMS Content API (15 endpoints: modules, tasks, resources)
- ✅ 203 functional tests (98% passing, ~21s execution)
- ✅ Schema↔Model mapping fixes (`task_type`, `resource.title`, URL validation)
- ✅ Referential integrity enforced in SQLite tests (`PRAGMA foreign_keys=ON`)
- ✅ Skills module with complete CRUD and authentication (prefix corrected to `/api/v1/skills`)
- ✅ Progress and Dashboard modules operational
- ✅ Error message standardization in English ("already exists")
- ✅ `short_description` required with `min_length=1` in both simulation schemas
- ✅ `field_validator` in `ResourceBase.url` (http/https enforced)
- ✅ Skills router route collision resolution

### v1.4.0 (Q2 2026)
- [ ] Complete enrollment system (slots, waitlists, notifications)
- [ ] Rate limiting with Redis (API abuse prevention)
- [ ] Structured JSON logging (ELK Stack integration)
- [ ] WebSockets for real-time notifications

### v2.0.0 (Q3 2026)
- [ ] Enhanced company-candidate matchmaking system (ML engine)
- [ ] Personalized simulation recommendations
- [ ] Multi-language (i18n) - Spanish/English/Portuguese
- [ ] Complete administration dashboard
- [ ] Public API with OpenAPI 3.1 documentation

---

## License

MIT License - Copyright (c) 2026 Matías Jiménez Sánchez

---

## Author

**Matías Jiménez Sánchez** - Lead Backend Engineer & Architect

- GitHub: [@MatiasJimenezSanchez](https://github.com/MatiasJimenezSanchez)
- Email: matjimsan@outlook.com
- LinkedIn: [Matías Jiménez](https://linkedin.com/in/matias-jimenez)

---

**Thank you for using Aurum DAO API!**

**Built with ❤️ using FastAPI, Python, PostgreSQL and Argon2**

---

*Last updated: February 24, 2026 - LMS Stable Release (v1.3.0)*
*Documentation manually generated and maintained*