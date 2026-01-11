"""add extended user fields

Revision ID: 548ebac76920
Revises: 687ba0a6de5a
Create Date: 2026-01-11 17:53:15

"""
from alembic import op
import sqlalchemy as sa

revision = '548ebac76920'
down_revision = '687ba0a6de5a'
branch_labels = None
depends_on = None

def upgrade():
    # Añadir columnas de localización
    op.add_column('users', sa.Column('city_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('province_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('region_id', sa.Integer(), nullable=True))
    
    # Añadir columnas de perfil
    op.add_column('users', sa.Column('birth_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=300), nullable=True))
    
    # Añadir columnas de preferencias
    op.add_column('users', sa.Column('preferred_theme', sa.String(length=20), nullable=True, server_default='light'))
    op.add_column('users', sa.Column('preferred_lang', sa.String(length=5), nullable=True, server_default='es'))
    
    # Añadir columnas legales
    op.add_column('users', sa.Column('accepts_terms', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('accepts_privacy', sa.Boolean(), nullable=True, server_default='false'))
    
    # Añadir columnas de gamificación
    op.add_column('users', sa.Column('current_level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('users', sa.Column('xp_total', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('streak_days', sa.Integer(), nullable=True, server_default='0'))
    
    # Añadir timestamps
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'streak_days')
    op.drop_column('users', 'xp_total')
    op.drop_column('users', 'current_level')
    op.drop_column('users', 'accepts_privacy')
    op.drop_column('users', 'accepts_terms')
    op.drop_column('users', 'preferred_lang')
    op.drop_column('users', 'preferred_theme')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'region_id')
    op.drop_column('users', 'province_id')
    op.drop_column('users', 'city_id')
