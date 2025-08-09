"""Merge announcement and other changes

Revision ID: bb57c0ba2b2d
Revises: 81f8e0f81892, add_announcement_categories
Create Date: 2025-08-10 02:56:17.979121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb57c0ba2b2d'
down_revision: Union[str, None] = ('81f8e0f81892', 'add_announcement_categories')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass