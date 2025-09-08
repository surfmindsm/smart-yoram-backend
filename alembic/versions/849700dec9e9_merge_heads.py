"""merge heads

Revision ID: 849700dec9e9
Revises: simple_login_history_001, sys_announce_001
Create Date: 2025-09-08 19:42:11.843909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '849700dec9e9'
down_revision: Union[str, None] = ('simple_login_history_001', 'sys_announce_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass