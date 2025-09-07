"""Add simple login history table

Revision ID: simple_login_history_001
Revises: 62e7378
Create Date: 2025-09-07 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'simple_login_history_001'
down_revision: Union[str, None] = 'system_ann_001'  # Based on current main branch
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create simple login_history table
    Very basic schema to avoid complexity issues
    """
    # Create login_history table
    op.create_table(
        'login_history',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create basic indexes for performance
    op.create_index('ix_login_history_id', 'login_history', ['id'])
    op.create_index('ix_login_history_user_id', 'login_history', ['user_id'])
    op.create_index('ix_login_history_timestamp', 'login_history', ['timestamp'])
    
    # Compound index for common queries
    op.create_index('ix_login_history_user_timestamp', 'login_history', ['user_id', 'timestamp'])


def downgrade() -> None:
    """
    Drop login_history table and indexes
    """
    # Drop indexes first
    op.drop_index('ix_login_history_user_timestamp', table_name='login_history')
    op.drop_index('ix_login_history_timestamp', table_name='login_history')
    op.drop_index('ix_login_history_user_id', table_name='login_history')
    op.drop_index('ix_login_history_id', table_name='login_history')
    
    # Drop table
    op.drop_table('login_history')