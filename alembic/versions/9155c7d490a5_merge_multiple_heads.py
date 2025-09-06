"""Merge multiple heads

Revision ID: 9155c7d490a5
Revises: system_ann_001, sys_announce_001
Create Date: 2025-09-07 00:34:15.318923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9155c7d490a5'
down_revision: Union[str, None] = ('system_ann_001', 'sys_announce_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass