# Aurum API - FastAPI + PostgreSQL + Docker + Alembic

Sistema robusto de autenticación y gestión de usuarios con FastAPI, SQLAlchemy, JWT, PostgreSQL y migraciones Alembic en Docker.

## 🎯 Descripción General

**Aurum API** es una API RESTful de producción construida con tecnologías modernas:
- **FastAPI**: Framework web asincrónico de alto rendimiento
- **PostgreSQL**: Base de datos relacional robusta en Docker
- **SQLAlchemy**: ORM para manejo seguro de datos
- **Alembic**: Versionado y migraciones de BD
- **JWT**: Autenticación segura con tokens (30 min expiración)
- **bcrypt**: Hasheado seguro de contraseñas
- **Docker Compose**: Containerización y orquestación

La API proporciona endpoints profesionales para:
- ✅ Registro seguro de usuarios
- ✅ Autenticación con JWT
- ✅ Acceso a perfil protegido
- ✅ Persistencia de datos con migraciones versionadas
- ✅ Swagger/ReDoc automático

## 📋 Estructura del Proyecto

```
AURUM BACK END/
│
├── 📁 app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                      # FastAPI app + endpoints raíz
│   │
│   ├── core/
│   │   ├── config.py                # Settings desde .env
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy Base + engine + fallback SQLite
│   │   └── session.py               # SessionLocal + dependencia get_db
│   │
│   ├── models/
│   │   ├── __init__.py              # Importa y expone User
│   │   └── user.py                  # Modelo SQLAlchemy User
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── schemas.py               # Base schemas
│   │   └── user.py                  # Pydantic UserCreate, User, Token
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py              # JWT, password hashing, get_current_user
│   │       └── user.py              # (endpoints adicionales)
│   │
│   └── repositories/
│       └── user_repository.py       # (patrón repository - opcional)
│
├── 📁 alembic/                      # Migraciones versionadas
│   ├── env.py                       # Config: carga .env, target_metadata
│   ├── script.py.mako               # Template para nuevas migraciones
│   ├── versions/
│   │   ├── __init__.py
│   │   ├── b6ff38f7e173_init_test.py            # Initial (vacío)
│   │   ├── 1a2b3c4d5e6f_create_users_table.py  # ⭐ Tabla users
│   │   └── (migraciones aplicadas)
│   └── alembic.ini                  # Configuración
│
├── 📁 scripts/
│   ├── wait-for-db.sh               # Espera Postgres + ejecuta migraciones
│   ├── dev.ps1                      # Automation para dev
│   └── revision.ps1                 # Automation para migraciones
│
├── 📄 Dockerfile                    # Python 3.12-slim + dependencies
├── 📄 docker-compose.yml            # Prod: Postgres + API (sin reload)
├── 📄 docker-compose.dev.yml        # Dev: API con --reload
│
├── 📄 .env                          # Variables (gitignored)
├── 📄 .env.example                  # Template
├── 📄 requirements.txt              # Dependencias pip
├── 📄 README.md                     # Este archivo
└── 📄 alembic.ini                   # Config Alembic
```

## 🏗️ Arquitectura Técnica

### Flujo de Autenticación

```
1️⃣  POST /users/             → Crear usuario (email, username, password)
                                 ↓
2️⃣  API valida              → Pydantic UserCreate
                                 ↓
3️⃣  API hashea pwd          → bcrypt.hashpw()
                                 ↓
4️⃣  API inserta en BD       → SQLAlchemy ORM → Postgres
                                 ↓
5️⃣  POST /token             → Login (username, password en form-data)
                                 ↓
6️⃣  API verifica credenciales → compara hashes
                                 ↓
7️⃣  API genera JWT          → jose.jwt.encode() con exp=+30min
                                 ↓
8️⃣  GET /users/me           → Bearer token en Authorization header
                                 ↓
9️⃣  API valida JWT          → jose.jwt.decode() + get_user()
                                 ↓
🔟 API devuelve usuario     → User schema (sin contraseña)
```

### Stack en Docker

```
┌──────────────────────────────────────┐
│     FastAPI (Python 3.12)            │
│  - Uvicorn: http://0.0.0.0:8000      │
│  - Endpoints: /users, /token, /docs  │
│  - Validación: Pydantic              │
│  - Auth: OAuth2 + JWT (jose)         │
└──────────────┬───────────────────────┘
               │ SQLAlchemy (sync)
               ▼
┌──────────────────────────────────────┐
│     PostgreSQL 16                    │
│  - Host: db:5432                     │
│  - Database: aurum_db                │
│  - Tablas: alembic_version, users    │
│  - Volumen: db_data (persistente)    │
└──────────────────────────────────────┘
```

---
🚀 Inicio Rápido (Quick Start)PrerrequisitosDocker Desktop instalado y corriendo.PowerShell (Windows).1. Clonar y ConfigurarPowerShellgit clone [https://github.com/MatiasJimenezSanchez/DAO-Auth.git](https://github.com/MatiasJimenezSanchez/DAO-Auth.git)
cd DAO-Authcp .env.example .env
2. Cargar Herramientas de DesarrolloHemos incluido un script de PowerShell para facilitar la gestión. Cárgalo en tu sesión:PowerShell. .\comandos-docker.ps1
3. Iniciar ServiciosPowerShellaurum-start
Esto levantará la API en http://localhost:8000 y PostgreSQL en el puerto 5432.4. Verificar EstadoPowerShellaurum-status
🛠️ Comandos Disponibles (PowerShell)ComandoDescripciónaurum-startLevanta los contenedores (API + DB)aurum-stopDetiene los serviciosaurum-restartReinicia los servicios`aurum-logs [webdb]`aurum-testEjecuta la suite de pruebas (Pytest) dentro del contenedoraurum-shell webEntra a la consola del contenedor de la APIaurum-db-reset⚠️ Borra y recrea la base de datos desde cero
## 📦 Requisitos

### 1. Clonar el repositorio

```bash
git clone https://github.com/MatiasJimenezSanchez/DAO-Auth.git
cd DAO-Auth
```

### 2. Crear entorno virtual

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tu configuración
```

### 5. Ejecutar la aplicación

```bash
# Desarrollo (con recarga automática)
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación de API

Una vez que la aplicación está corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Endpoints Principales

### Autenticación

#### Login
```bash
POST /api/v1/token
Content-Type: application/x-www-form-urlencoded

username=usuario&password=contraseña
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

#### Refrescar Token
```bash
POST /api/v1/refresh-token
Authorization: Bearer {token}
```

### Usuarios

#### Registrar Usuario
```bash
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "juan",
  "email": "juan@example.com",
  "password": "Mi_Contraseña_Segura",
  "full_name": "Juan Pérez",
  "disabled": false
}
```

#### Obtener Usuario Actual
```bash
GET /api/v1/users/me
Authorization: Bearer {token}
```

#### Listar Usuarios
```bash
GET /api/v1/users/?skip=0&limit=10
Authorization: Bearer {token}
```

#### Obtener Usuario por Username
```bash
GET /api/v1/users/{username}
Authorization: Bearer {token}
```

#### Actualizar Perfil
```bash
PUT /api/v1/users/me/update
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "nuevo@example.com",
  "full_name": "Juan Carlos Pérez"
}
```

#### Cambiar Contraseña
```bash
POST /api/v1/users/me/change-password
Authorization: Bearer {token}

old_password=antiguo&new_password=nuevo
```

#### Eliminar Usuario
```bash
DELETE /api/v1/users/{username}
Authorization: Bearer {token}
```

## 🔧 Configuración

Las variables de configuración están en `app/core/config.py`. Puedes sobrescribir valores usando variables de entorno:

```bash
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://user:password@localhost/aurum
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 🗄️ Base de Datos

### SQLite (Desarrollo)
Por defecto, usa SQLite. Se crea un archivo `sql_app.db` automáticamente.

### PostgreSQL (Producción)

1. Instala el driver:
```bash
pip install psycopg2-binary
```

2. Configura la URL:
```bash
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/aurum_db
```

## 🔑 Seguridad

- **Contraseñas**: Hasheadas con bcrypt (máximo 72 bytes)
- **Tokens**: JWT con expiración configurable (30 min por defecto)
- **CORS**: Configurable según necesidad
- **SQL Injection**: Protegido con SQLAlchemy ORM

## 📝 Ejemplos de Uso

### Con curl

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "email": "juan@example.com",
    "password": "Mi_Contraseña_123",
    "full_name": "Juan Pérez"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=juan&password=Mi_Contraseña_123"

# Obtener usuario actual
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer {tu_token}"
```

### Con Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Registrar
response = requests.post(
    f"{BASE_URL}/users/register",
    json={
        "username": "juan",
        "email": "juan@example.com",
        "password": "Mi_Contraseña_123",
        "full_name": "Juan Pérez"
    }
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/token",
    data={"username": "juan", "password": "Mi_Contraseña_123"}
)
token = response.json()["access_token"]

# Obtener usuario actual
response = requests.get(
    f"{BASE_URL}/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

## 🧪 Testing
El proyecto cuenta con una suite de pruebas robusta que corre dentro de Docker para asegurar la consistencia.

Para ejecutar todos los tests:

PowerShell

aurum-test
Módulos probados:

✅ Usuarios: Creación, validación de duplicados, lectura y actualización.

✅ Empresas: Flujos CRUD completos, validación de slugs y nombres únicos.

📚 Documentación API
Una vez iniciado el servicio, puedes acceder a la documentación interactiva generada automáticamente:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🔄 Flujo de Migraciones (Alembic)
Si modificas los modelos en app/models/, genera una nueva migración:

PowerShell

# 1. Crear revisión
aurum-migrate -Action revision -Message "descripcion_cambio"

# 2. Aplicar cambios a la BD
aurum-migrate -Action upgrade
## 🧪 Testing

Notas sobre cómo están configurados y cómo ejecutar los tests en este repo:

- Dependencias recomendadas:

```bash
pip install -r requirements.txt
pip install pytest httpx
```

- Infraestructura de tests del proyecto:
  - `tests/conftest.py` crea una base de datos SQLite temporal `./test.db` y ejecuta `Base.metadata.create_all(bind=engine)`.
  - La dependencia `get_db` de la app se sobrescribe en los tests para usar la sesión de prueba.
  - Por eso los tests son aislados y rápidos, no tocan tu contenedor Postgres.

- Ejecutar todos los tests:

```bash
pytest -v
```

- Ejecutar un test específico (ejemplo):

```bash
pytest tests/test_users_extended.py::test_create_extended_user -q
```

- Resultado esperado en este punto del proyecto:
  - `tests/test_users_extended.py` pasa (verifica creación de usuario con campos extendidos como `city_id`, `xp_total`).

- Archivos importantes de test:
  - `tests/conftest.py` — fixture `db` y `client` (TestClient + override `get_db`).
  - `tests/test_users_extended.py` — caso de creación de usuario extendido con catálogos.

Si necesitas que los tests usen Postgres en Docker en lugar de SQLite, modifica `tests/conftest.py` para apuntar a `DATABASE_URL` y asegúrate de levantar el servicio `db`.

## 🔁 Migraciones y estado actual

- Se corrigió y normalizó el flujo de migraciones durante la sesión:
  - Se limpió la revisión problemática en `alembic/versions` (errores de `down_revision` y enum `gender`).
  - Se aplicó una migración base (autogenerada) contra la BD en Docker y, para asegurar sincronía, se ejecutó `alembic stamp head` cuando fue necesario.
  - Nota: para entornos de producción evita `stamp head` salvo que entiendas las implicaciones; en desarrollo fue usado para sincronizar rápidamente el estado.

## 🌱 Seed (datos semilla)

- Script de semillas creado: `app/db/seeds.py` — ejemplo para poblar regiones/provincias/ciudades de Ecuador.
- Ejecutar seeds localmente (usa la misma DB configurada en `DATABASE_URL` o el fallback SQLite):

```bash
python -m app.db.seeds
```

Esto inserta algunas regiones, provincias y ciudades de ejemplo usadas por los tests y por el endpoint `POST /users/`.


## 🚀 Despliegue en Producción

### Con Gunicorn

```bash
pip install gunicorn

gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Con Docker

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t aurum-api .
docker run -p 8000:8000 aurum-api
```

## 📦 Dependencias

- **FastAPI**: Framework web moderno
- **Uvicorn**: Servidor ASGI
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos
- **bcrypt**: Hasheado seguro de contraseñas
- **python-jose**: Manejo de JWT
- **python-multipart**: Soporte de formularios

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Matías Jiménez Sánchez**

- GitHub: [@MatiasJimenezSanchez](https://github.com/MatiasJimenezSanchez)
- Email: matjimsan@outlook.com

## ❓ Preguntas y Soporte

Si tienes preguntas o necesitas soporte, por favor abre un issue en GitHub.

---

**Hecho con ❤️ usando FastAPI y Python**
