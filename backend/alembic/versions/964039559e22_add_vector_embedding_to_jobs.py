"""add vector embedding to jobs

Revision ID: 964039559e22
Revises: 7f6e1e313fa0
Create Date: 2026-10-11 16:04:41.433867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '964039559e22'
down_revision: Union[str, Sequence[str], None] = '7f6e1e313fa0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('jobs', sa.Column('embeddings', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jobs', 'embeddings')
