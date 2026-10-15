"""add jobs table

Revision ID: 7f6e1e313fa0
Revises: 942f036e6630
Create Date: 2026-10-11 14:25:56.230938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f6e1e313fa0'
down_revision: Union[str, Sequence[str], None] = '942f036e6630'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('company', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('apply_url', sa.String(), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_company'), 'jobs', ['company'], unique=False)
    op.create_index(op.f('ix_jobs_location'), 'jobs', ['location'], unique=False)
    op.create_index(op.f('ix_jobs_title'), 'jobs', ['title'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_jobs_title'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_location'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_company'), table_name='jobs')
    op.drop_table('jobs')
