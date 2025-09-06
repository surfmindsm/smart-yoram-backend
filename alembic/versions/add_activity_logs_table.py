"""Add activity logs table for GDPR compliance

Revision ID: activity_logs_001
Revises: login_history_001
Create Date: 2025-09-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'activity_logs_001'
down_revision: Union[str, None] = 'login_history_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('action', sa.Enum('VIEW', 'CREATE', 'UPDATE', 'DELETE', 'SEARCH', 'LOGIN', 'LOGOUT', name='actiontype'), nullable=False),
        sa.Column('resource', sa.Enum('MEMBER', 'ATTENDANCE', 'FINANCIAL', 'BULLETIN', 'ANNOUNCEMENT', 'SYSTEM', 'USER', 'CHURCH', name='resourcetype'), nullable=False),
        sa.Column('target_id', sa.String(length=50), nullable=True),
        sa.Column('target_name', sa.String(length=100), nullable=True),
        sa.Column('page_path', sa.String(length=200), nullable=False),
        sa.Column('page_name', sa.String(length=100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('sensitive_data', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create performance optimization indexes
    op.create_index('idx_user_timestamp', 'activity_logs', ['user_id', 'timestamp'])
    op.create_index('idx_action_resource', 'activity_logs', ['action', 'resource'])
    op.create_index('idx_target', 'activity_logs', ['target_id', 'resource'])
    op.create_index('idx_timestamp', 'activity_logs', ['timestamp'])
    op.create_index('idx_ip_address', 'activity_logs', ['ip_address'])
    op.create_index('idx_user_action_date', 'activity_logs', ['user_id', 'action', sa.text("date(timestamp)")])
    op.create_index('idx_resource_target', 'activity_logs', ['resource', 'target_id'])
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_index('idx_resource_target', table_name='activity_logs')
    op.drop_index('idx_user_action_date', table_name='activity_logs')
    op.drop_index('idx_ip_address', table_name='activity_logs')
    op.drop_index('idx_timestamp', table_name='activity_logs')
    op.drop_index('idx_target', table_name='activity_logs')
    op.drop_index('idx_action_resource', table_name='activity_logs')
    op.drop_index('idx_user_timestamp', table_name='activity_logs')
    
    # Drop table
    op.drop_table('activity_logs')
    
    # Drop enums (PostgreSQL)
    op.execute('DROP TYPE IF EXISTS resourcetype')
    op.execute('DROP TYPE IF EXISTS actiontype')