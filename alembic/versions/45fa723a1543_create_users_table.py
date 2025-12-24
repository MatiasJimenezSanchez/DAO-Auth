"""create users table
Revision ID: 45fa723a1543
Revises: b6ff38f7e173
Create Date: 2025-12-24 20:52:44.960957
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '45fa723a1543'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None




def upgrade():
    # Already applied in 1a2b3c4d5e6f; no-op here
    pass


def downgrade():
    # Already applied in 1a2b3c4d5e6f; no-op here
    pass
