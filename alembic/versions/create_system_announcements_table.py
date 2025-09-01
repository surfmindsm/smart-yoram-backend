"""Create system_announcements table and separate from announcements

Revision ID: system_ann_001
Revises: ann_multi_target_001
Create Date: 2025-09-01 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'system_ann_001'
down_revision = 'aa06dac1934a'
branch_labels = None
depends_on = None


def upgrade():
    """Create system_announcements table and restore announcements table to original state"""
    
    # Create system_announcements table
    try:
        op.create_table(
            'system_announcements',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('priority', sa.String(50), nullable=False, server_default='normal'),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('target_churches', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('is_pinned', sa.Boolean(), default=False),
            sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('author_name', sa.String()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        )
        
        # Add check constraint for priority
        op.create_check_constraint(
            'check_system_priority',
            'system_announcements',
            "priority IN ('urgent', 'important', 'normal')"
        )
        
    except Exception as e:
        print(f"System announcements table creation failed (may already exist): {e}")
    
    # Create system_announcement_reads table
    try:
        op.create_table(
            'system_announcement_reads',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('system_announcement_id', sa.Integer(), sa.ForeignKey('system_announcements.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('church_id', sa.Integer(), sa.ForeignKey('churches.id', ondelete='CASCADE'), nullable=False),
            sa.Column('read_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        
        # Add unique index for system_announcement_id + user_id + church_id
        op.create_index(
            'ix_system_announcement_reads_unique', 
            'system_announcement_reads', 
            ['system_announcement_id', 'user_id', 'church_id'], 
            unique=True
        )
        
        # Add check constraint
        op.create_check_constraint(
            'check_system_announcement_read_not_null',
            'system_announcement_reads',
            'system_announcement_id IS NOT NULL AND user_id IS NOT NULL AND church_id IS NOT NULL'
        )
        
    except Exception as e:
        print(f"System announcement reads table creation failed (may already exist): {e}")
    
    # Restore announcements table to original state
    # Remove columns that were added but don't exist in DB
    try:
        # Drop constraints first if they exist
        try:
            op.drop_constraint('check_type', 'announcements')
        except:
            pass
        try:
            op.drop_constraint('check_priority', 'announcements')
        except:
            pass
        try:
            op.drop_constraint('check_target_type', 'announcements')
        except:
            pass
        try:
            op.drop_constraint('check_target_consistency', 'announcements')
        except:
            pass
        
        # Remove columns that don't exist in the actual DB
        columns_to_check = ['type', 'priority', 'target_type', 'start_date', 'end_date', 'created_by']
        for column in columns_to_check:
            try:
                # Try to drop column - will fail silently if doesn't exist
                op.drop_column('announcements', column)
            except:
                pass
                
        # Ensure church_id is NOT NULL (restore original constraint)
        try:
            op.alter_column('announcements', 'church_id', nullable=False)
        except:
            pass
            
    except Exception as e:
        print(f"Announcements table restoration failed: {e}")


def downgrade():
    """Remove system_announcements tables"""
    
    # Drop system announcement tables
    op.drop_table('system_announcement_reads')
    op.drop_table('system_announcements')
    
    # Restore any modified announcement table constraints if needed
    # (This is a simplified downgrade - full restoration would be more complex)