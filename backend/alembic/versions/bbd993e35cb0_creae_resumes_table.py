"""creae resumes table

Revision ID: bbd993e35cb0
Revises: 2b7081149ede
Create Date: 2026-10-10 14:21:22.639858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbd993e35cb0'
down_revision: Union[str, Sequence[str], None] = '2b7081149ede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('resumes', sa.Column('title', sa.String(length=255), nullable=False))
    op.add_column('resumes', sa.Column('content', sa.Text(), nullable=False))
    op.add_column('resumes', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('resumes', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('resumes', 'updated_at')
    op.drop_column('resumes', 'created_at')
    op.drop_column('resumes', 'content')
    op.drop_column('resumes', 'title')
