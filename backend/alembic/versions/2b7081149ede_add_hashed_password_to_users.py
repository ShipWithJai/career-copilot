"""add hashed_password to users

Revision ID: 2b7081149ede
Revises: 79fa21d24835
Create Date: 2026-10-10 11:14:09.292395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b7081149ede'
down_revision: Union[str, Sequence[str], None] = '79fa21d24835'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('hashed_password', sa.String(), server_default='dummy_hash', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hashed_password')
