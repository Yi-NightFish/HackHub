"""add team join request

Revision ID: 8e29b94fbec1
Revises: 718625f9bfc4
Create Date: 2026-05-08 21:38:27.311772
"""
from alembic import op
import sqlalchemy as sa


revision = '8e29b94fbec1'
down_revision = '718625f9bfc4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'team_join_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['team.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('team_join_request')