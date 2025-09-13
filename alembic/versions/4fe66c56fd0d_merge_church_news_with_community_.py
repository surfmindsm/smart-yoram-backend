"""Merge church_news with community platform

Revision ID: 4fe66c56fd0d
Revises: add_church_news_001, community_platform_001
Create Date: 2025-09-13 15:49:22.763696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fe66c56fd0d'
down_revision: Union[str, None] = ('add_church_news_001', 'community_platform_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass