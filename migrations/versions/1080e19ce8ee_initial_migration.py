"""initial migration

Revision ID: 1080e19ce8ee
Revises: 
Create Date: 2025-06-11 14:08:28.069125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1080e19ce8ee'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pipelines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=120), nullable=False),
    sa.Column('user_name', sa.String(length=120), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_email')
    )
    op.create_table('api_keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('pipeline_users',
    sa.Column('pipeline_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('pipeline_id', 'user_id')
    )
    op.create_table('stages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('pipeline_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('negotiations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('stage_id', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['stage_id'], ['stages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stage_users',
    sa.Column('stage_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stage_id'], ['stages.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('stage_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stage_users')
    op.drop_table('negotiations')
    op.drop_table('stages')
    op.drop_table('pipeline_users')
    op.drop_table('api_keys')
    op.drop_table('users')
    op.drop_table('pipelines')
    op.drop_table('accounts')
    # ### end Alembic commands ###
