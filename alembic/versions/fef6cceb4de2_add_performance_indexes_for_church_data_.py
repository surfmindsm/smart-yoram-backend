"""Add performance indexes for church data queries

Revision ID: fef6cceb4de2
Revises: secretary_constraints_001
Create Date: 2025-08-30 00:53:27.286835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fef6cceb4de2'
down_revision: Union[str, None] = 'secretary_constraints_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Members table performance indexes
    op.create_index('idx_members_church_status', 'members', ['church_id', 'status'])
    op.create_index('idx_members_church_status_gender', 'members', ['church_id', 'status', 'gender'])
    op.create_index('idx_members_church_status_age', 'members', ['church_id', 'status', 'age'])
    op.create_index('idx_members_church_status_position', 'members', ['church_id', 'status', 'position'])
    op.create_index('idx_members_church_status_department', 'members', ['church_id', 'status', 'department'])
    op.create_index('idx_members_church_status_district', 'members', ['church_id', 'status', 'district'])
    op.create_index('idx_members_church_registration_date', 'members', ['church_id', 'registration_date'])
    
    # Offerings table performance indexes
    op.create_index('idx_offerings_church_date', 'offerings', ['church_id', 'offered_on'])
    op.create_index('idx_offerings_church_date_desc', 'offerings', ['church_id', sa.text('offered_on DESC')])
    op.create_index('idx_offerings_church_fund_type', 'offerings', ['church_id', 'fund_type'])
    op.create_index('idx_offerings_church_member_date', 'offerings', ['church_id', 'member_id', 'offered_on'])
    
    # Attendance table performance indexes  
    op.create_index('idx_attendance_church_date', 'attendances', ['church_id', 'service_date'])
    op.create_index('idx_attendance_church_date_present', 'attendances', ['church_id', 'service_date', 'present'])
    op.create_index('idx_attendance_church_present_type', 'attendances', ['church_id', 'present', 'service_type'])
    op.create_index('idx_attendance_church_member_date', 'attendances', ['church_id', 'member_id', 'service_date'])
    
    # Announcements table performance indexes
    op.create_index('idx_announcements_church_created_desc', 'announcements', ['church_id', sa.text('created_at DESC')])
    op.create_index('idx_announcements_church_category', 'announcements', ['church_id', 'category'])
    
    # Prayer requests performance indexes
    op.create_index('idx_prayer_requests_church_created_desc', 'prayer_requests', ['church_id', sa.text('created_at DESC')])
    op.create_index('idx_prayer_requests_church_status', 'prayer_requests', ['church_id', 'status'])
    
    # Pastoral care requests performance indexes
    op.create_index('idx_pastoral_care_church_created_desc', 'pastoral_care_requests', ['church_id', sa.text('created_at DESC')])
    op.create_index('idx_pastoral_care_church_status', 'pastoral_care_requests', ['church_id', 'status'])


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_pastoral_care_church_status')
    op.drop_index('idx_pastoral_care_church_created_desc')
    op.drop_index('idx_prayer_requests_church_status')
    op.drop_index('idx_prayer_requests_church_created_desc')
    op.drop_index('idx_announcements_church_category')
    op.drop_index('idx_announcements_church_created_desc')
    op.drop_index('idx_attendance_church_member_date')
    op.drop_index('idx_attendance_church_present_type')
    op.drop_index('idx_attendance_church_date_present')
    op.drop_index('idx_attendance_church_date')
    op.drop_index('idx_offerings_church_member_date')
    op.drop_index('idx_offerings_church_fund_type')
    op.drop_index('idx_offerings_church_date_desc')
    op.drop_index('idx_offerings_church_date')
    op.drop_index('idx_members_church_registration_date')
    op.drop_index('idx_members_church_status_district')
    op.drop_index('idx_members_church_status_department')
    op.drop_index('idx_members_church_status_position')
    op.drop_index('idx_members_church_status_age')
    op.drop_index('idx_members_church_status_gender')
    op.drop_index('idx_members_church_status')