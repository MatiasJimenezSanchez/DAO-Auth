# app/models/__init__.py
from app.db.base import Base
from app.models.user import User  # Cambiar extended_user por user
from app.models.catalog import Region, Province, City

__all__ = ["Base", "User", "Region", "Province", "City"]