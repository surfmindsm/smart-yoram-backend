"""Make agent_id nullable in chat_histories for default agent support

Revision ID: make_agent_id_nullable
Revises: 
Create Date: 2025-08-25 07:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_agent_id_nullable'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Make agent_id nullable in chat_histories table"""
    # Make agent_id column nullable to support default agent (ID: 0)
    # which doesn't exist in ai_agents table
    op.alter_column('chat_histories', 'agent_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)


def downgrade():
    """Make agent_id non-nullable again"""
    op.alter_column('chat_histories', 'agent_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)