"""Add login history tracking table

Revision ID: login_history_001
Revises: 9155c7d490a5
Create Date: 2025-09-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'login_history_001'
down_revision: Union[str, None] = '9155c7d490a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_login_history table
    op.create_table(
        'user_login_history',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('login_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('session_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_duration', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_id_login_time', 'user_login_history', ['user_id', 'login_time'])
    op.create_index(op.f('ix_user_login_history_id'), 'user_login_history', ['id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_user_login_history_id'), table_name='user_login_history')
    op.drop_index('idx_user_id_login_time', table_name='user_login_history')
    
    # Drop table
    op.drop_table('user_login_history')