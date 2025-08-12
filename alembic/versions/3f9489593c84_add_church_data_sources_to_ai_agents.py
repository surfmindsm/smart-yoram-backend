"""add_church_data_sources_to_ai_agents

Revision ID: 3f9489593c84
Revises: update_default_gpt_model
Create Date: 2025-08-12 16:55:18.812399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3f9489593c84'
down_revision: Union[str, None] = 'update_default_gpt_model'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add church_data_sources column to ai_agents table
    op.add_column('ai_agents', 
        sa.Column('church_data_sources', 
                  sa.JSON(), 
                  nullable=True,
                  server_default='{}')
    )
    
    # Add church_data_sources column to official_agent_templates table
    op.add_column('official_agent_templates', 
        sa.Column('church_data_sources', 
                  sa.JSON(), 
                  nullable=True,
                  server_default='{}')
    )


def downgrade() -> None:
    # Drop church_data_sources column from ai_agents table
    op.drop_column('ai_agents', 'church_data_sources')
    
    # Drop church_data_sources column from official_agent_templates table
    op.drop_column('official_agent_templates', 'church_data_sources')