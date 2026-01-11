# app/models/extended_user.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric
)
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(200), nullable=False)

    # --- nuevos campos ---
    birth_date = Column(DateTime, nullable=True)
    gender = Column(String(20))

    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)

    # Gamificación
    xp_total = Column(Integer, default=0, nullable=False)
    xp_validated = Column(Integer, default=0)
    current_level = Column(Integer, default=1, nullable=False)
    streak_days = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    last_activity_at = Column(DateTime)

    # Avatar y prefs
    avatar_url = Column(String(500))
    preferred_theme = Column(String(20), default="dark")
    preferred_lang = Column(String(5), default="es")
    timezone = Column(String(50), default="America/Guayaquil")

    # Consentimientos
    accepts_terms = Column(Boolean, default=False, nullable=False)
    accepts_privacy = Column(Boolean, default=False, nullable=False)
    accepts_data_share = Column(Boolean, default=False)
    accepts_contact = Column(Boolean, default=False)
    accepts_marketing = Column(Boolean, default=False)

    # Verificación
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    phone = Column(String(20))
    phone_verified = Column(Boolean, default=False)

    # Seguridad
    requires_2fa = Column(Boolean, default=False)
    secret_2fa = Column(String(255))
    recovery_codes_2fa = Column(Text)  # JSONB en prod
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)

    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=1)
    last_session_at = Column(DateTime)
    total_sessions = Column(Integer, default=0)

    # Métricas agregadas
    total_simulations_enrolled = Column(Integer, default=0)
    total_simulations_completed = Column(Integer, default=0)
    total_certificates = Column(Integer, default=0)
    total_learning_hours = Column(Numeric(10, 2), default=0)

    # Referidos
    referral_code = Column(String(20), unique=True)
    referred_by_user_id = Column(Integer, ForeignKey("users.id"))

    # Estado
    is_active = Column(Boolean, default=True)
    deactivation_reason = Column(String(100))
    deactivated_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    region = relationship("Region", foreign_keys=[region_id])
    province = relationship("Province", foreign_keys=[province_id])
    city = relationship("City", foreign_keys=[city_id])
    referrer = relationship("User", remote_side=[id])