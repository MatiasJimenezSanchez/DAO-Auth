"""
Configuración de la aplicación
"""
import os
from typing import Optional

class Settings:
    """Configuración principal de la aplicación"""
    
    # Información de la aplicación
    APP_NAME: str = "Aurum API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API de autenticación con FastAPI y JWT"
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # Si usas PostgreSQL, descomenta esto:
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aurum_db")
    
    # Configuración de SQLite
    SQLALCHEMY_ECHO: bool = False  # Cambiar a True para ver queries SQL en logs
    
    # Configuración de CORS
    ALLOWED_ORIGINS: list = ["*"]  # En producción, especifica los orígenes
    
    # Paginación
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # Logs
    LOG_LEVEL: str = "INFO"
    
    @property
    def sqlalchemy_database_url(self) -> str:
        """Retorna la URL de la base de datos"""
        return self.DATABASE_URL

# Instancia global de configuración
settings = Settings()
