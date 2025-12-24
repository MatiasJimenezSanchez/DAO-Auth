"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuración principal de la aplicación (cargada desde .env)."""

    APP_NAME: str = os.getenv("APP_NAME", "Aurum API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", "API de autenticación con FastAPI y JWT")

    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "please-change-me")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

    # Otros ajustes
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "False").lower() in ("1", "true", "yes")
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()
