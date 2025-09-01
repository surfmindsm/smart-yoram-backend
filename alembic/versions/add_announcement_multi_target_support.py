"""Add multi-target announcement support

Revision ID: ann_multi_target_001
Revises: sys_announce_001
Create Date: 2025-09-01 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ann_multi_target_001'
down_revision = 'sys_announce_001'
branch_labels = None
depends_on = None


def upgrade():
    """Add multi-target announcement support"""
    
    # Add target_type column to announcements
    try:
        op.add_column('announcements', sa.Column('target_type', sa.String(50), nullable=False, server_default='single'))
    except Exception as e:
        print(f"Column addition failed (may already exist): {e}")
    
    # Create announcement_targets table for multi-target support
    try:
        op.create_table(
            'announcement_targets',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('announcement_id', sa.Integer(), sa.ForeignKey('announcements.id', ondelete='CASCADE'), nullable=False),
            sa.Column('church_id', sa.Integer(), sa.ForeignKey('churches.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        
        # Create unique index for announcement_id + church_id
        op.create_index('ix_announcement_targets_unique', 'announcement_targets', ['announcement_id', 'church_id'], unique=True)
        
    except Exception as e:
        print(f"Table creation failed (may already exist): {e}")
    
    # Add check constraints
    try:
        op.create_check_constraint(
            'check_target_type',
            'announcements',
            "target_type IN ('all', 'specific', 'single')"
        )
        
        op.create_check_constraint(
            'check_target_consistency',
            'announcements',
            "(target_type = 'single' AND church_id IS NOT NULL) OR "
            "(target_type = 'all' AND church_id IS NULL) OR "
            "(target_type = 'specific' AND church_id IS NULL)"
        )
        
        op.create_check_constraint(
            'check_announcement_target_not_null',
            'announcement_targets',
            'announcement_id IS NOT NULL AND church_id IS NOT NULL'
        )
        
    except Exception as e:
        print(f"Constraint creation failed (may already exist): {e}")


def downgrade():
    """Remove multi-target announcement support"""
    
    # Drop announcement_targets table
    op.drop_table('announcement_targets')
    
    # Remove target_type column
    op.drop_column('announcements', 'target_type')
    
    # Drop constraints (PostgreSQL will auto-drop with table)
    try:
        op.drop_constraint('check_target_type', 'announcements')
        op.drop_constraint('check_target_consistency', 'announcements')
    except:
        pass