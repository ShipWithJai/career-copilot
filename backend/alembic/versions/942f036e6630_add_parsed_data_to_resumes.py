"""add parsed_data to resumes

Revision ID: 942f036e6630
Revises: bbd993e35cb0
Create Date: 2026-10-11 13:27:06.437394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '942f036e6630'
down_revision: Union[str, Sequence[str], None] = 'bbd993e35cb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('resumes', sa.Column('parsed_data', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('resumes', 'parsed_data')
