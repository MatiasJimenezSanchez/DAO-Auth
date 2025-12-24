# Aurum Auth API

API de autenticación moderna con FastAPI y JWT. Proyecto refactorizado con arquitectura profesional y modular.

## 🚀 Características

- ✅ Autenticación con JWT
- ✅ Sistema de registro de usuarios
- ✅ Hasheado seguro de contraseñas con bcrypt
- ✅ Tokens con expiración configurable
- ✅ CRUD completo de usuarios
- ✅ Cambio de contraseña
- ✅ Arquitectura limpia y modular
- ✅ Documentación automática con Swagger

## 📋 Estructura del Proyecto

```
app/
├── api/               # Endpoints y routers
│   └── v1/
│       ├── auth.py   # Endpoints de autenticación
│       └── user.py   # Endpoints de usuario
├── core/              # Configuración y seguridad
│   ├── config.py     # Variables de configuración
│   └── security.py   # Funciones de seguridad
├── db/                # Base de datos
│   ├── session.py    # Configuración de sesión
│   └── base.py       # Base de modelos
├── models/            # Modelos SQLAlchemy
│   └── user.py       # Modelo de Usuario
├── repositories/      # Capa de acceso a datos
│   └── user_repository.py
├── schemas/           # Esquemas Pydantic
│   └── user.py
└── services/          # Lógica de negocio
    └── user_service.py
main.py              # Aplicación principal
requirements.txt     # Dependencias
```

## 🛠️ Instalación

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

Para agregar tests unitarios:

```bash
pip install pytest pytest-asyncio httpx
```

Crea un archivo `test_api.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

Ejecuta:
```bash
pytest
```

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
