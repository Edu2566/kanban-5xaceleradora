"""add kpi fields to negotiation

Revision ID: 1_add_kpi_fields
Revises: 1080e19ce8ee
Create Date: 2025-06-11 14:30:00
"""
from alembic import op
import sqlalchemy as sa

revision = '1_add_kpi_fields'
down_revision = '1080e19ce8ee'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('negotiations', sa.Column('value', sa.Numeric(10, 2), nullable=True, server_default='0'))
    op.add_column('negotiations', sa.Column('status', sa.String(length=20), nullable=True, server_default='open'))
    op.add_column('negotiations', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('negotiations', sa.Column('closed_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('negotiations', 'closed_at')
    op.drop_column('negotiations', 'created_at')
    op.drop_column('negotiations', 'status')
    op.drop_column('negotiations', 'value')
