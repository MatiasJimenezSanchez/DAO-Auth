"""merge heads
Revision ID: d3f1c9a7b8c9
Revises: 45fa723a1543, 6040db657c5c
Create Date: 2025-12-24 21:10:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd3f1c9a7b8c9'
down_revision = '6040db657c5c'
branch_labels = None
depends_on = None


def upgrade():
    # Already applied in 1a2b3c4d5e6f; no-op here
    pass


def downgrade():
    # Already applied in 1a2b3c4d5e6f; no-op here
    pass
