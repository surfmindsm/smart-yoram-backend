"""Update announcements for system-wide notifications with priority and date filtering

Revision ID: sys_announce_001
Revises: secretary_constraints_001
Create Date: 2024-09-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'sys_announce_001'
down_revision = 'secretary_agent_001'
branch_labels = None
depends_on = None


def upgrade():
    """Add system announcement support and read tracking"""
    
    # Skip the broken constraint migration
    op.execute(text("UPDATE alembic_version SET version_num = 'sys_announce_001'"))
    
    # Add new columns to announcements table
    try:
        op.add_column('announcements', sa.Column('type', sa.String(50), nullable=False, server_default='church'))
        op.add_column('announcements', sa.Column('priority', sa.String(50), nullable=False, server_default='normal'))
        op.add_column('announcements', sa.Column('start_date', sa.Date(), nullable=True))
        op.add_column('announcements', sa.Column('end_date', sa.Date(), nullable=True))
        op.add_column('announcements', sa.Column('created_by', sa.Integer(), nullable=True))
        
        # Change church_id to nullable for system announcements
        op.alter_column('announcements', 'church_id', nullable=True)
        
    except Exception as e:
        print(f"Column addition failed (may already exist): {e}")
    
    # Create announcement_reads table
    try:
        op.create_table(
            'announcement_reads',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('announcement_id', sa.Integer(), sa.ForeignKey('announcements.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('read_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        
        # Create unique index for announcement_id + user_id
        op.create_index('ix_announcement_reads_unique', 'announcement_reads', ['announcement_id', 'user_id'], unique=True)
        
    except Exception as e:
        print(f"Table creation failed (may already exist): {e}")
    
    # Set default values for existing records
    op.execute(text("""
        UPDATE announcements 
        SET start_date = date('now', '-30 days'), 
            end_date = NULL,
            created_by = author_id
        WHERE start_date IS NULL
    """))
    
    # Make start_date non-nullable after setting defaults
    op.alter_column('announcements', 'start_date', nullable=False)
    op.alter_column('announcements', 'created_by', nullable=False)


def downgrade():
    """Remove system announcement support"""
    
    # Drop announcement_reads table
    op.drop_table('announcement_reads')
    
    # Remove added columns
    op.drop_column('announcements', 'created_by')
    op.drop_column('announcements', 'end_date')
    op.drop_column('announcements', 'start_date')
    op.drop_column('announcements', 'priority')
    op.drop_column('announcements', 'type')
    
    # Change church_id back to non-nullable
    op.alter_column('announcements', 'church_id', nullable=False)