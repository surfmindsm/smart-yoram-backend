"""Add secretary agent fields to AI Agent model

Revision ID: secretary_agent_001
Revises: 
Create Date: 2024-08-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'secretary_agent_001'
down_revision = 'de7501bc3e2f'
depends_on = None


def upgrade() -> None:
    """Add new fields to ai_agents table for secretary agent functionality."""
    
    # Add new fields to ai_agents table with proper defaults
    op.add_column('ai_agents', sa.Column('is_default', sa.Boolean(), nullable=False, default=False, server_default='false'))
    op.add_column('ai_agents', sa.Column('enable_church_data', sa.Boolean(), nullable=False, default=False, server_default='false'))
    op.add_column('ai_agents', sa.Column('created_by_system', sa.Boolean(), nullable=False, default=False, server_default='false'))
    op.add_column('ai_agents', sa.Column('gpt_model', sa.String(50), nullable=True))
    op.add_column('ai_agents', sa.Column('max_tokens', sa.Integer(), nullable=True))
    op.add_column('ai_agents', sa.Column('temperature', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove secretary agent fields from ai_agents table."""
    
    op.drop_column('ai_agents', 'temperature')
    op.drop_column('ai_agents', 'max_tokens')
    op.drop_column('ai_agents', 'gpt_model')
    op.drop_column('ai_agents', 'created_by_system')
    op.drop_column('ai_agents', 'enable_church_data')
    op.drop_column('ai_agents', 'is_default')