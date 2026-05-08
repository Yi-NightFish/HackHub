"""add project page

Revision ID: 0fd5c13711eb
Revises: 8e29b94fbec1
Create Date: 2026-05-08 23:02:36.786008
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fd5c13711eb'
down_revision = '8e29b94fbec1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tech_stack', sa.String(length=300), nullable=True),
        sa.Column('demo_link', sa.String(length=300), nullable=True),
        sa.Column('github_link', sa.String(length=300), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['team.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id')
    )


def downgrade():
    op.drop_table('project')