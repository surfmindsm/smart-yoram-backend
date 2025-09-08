"""Add community applications table

Revision ID: 09389104b722
Revises: 849700dec9e9
Create Date: 2025-09-08 19:42:54.322409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09389104b722'
down_revision: Union[str, None] = '849700dec9e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create community_applications table
    op.create_table(
        'community_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('applicant_type', sa.String(length=50), nullable=False, comment='신청자 유형'),
        sa.Column('organization_name', sa.String(length=200), nullable=False, comment='단체/회사명'),
        sa.Column('contact_person', sa.String(length=100), nullable=False, comment='담당자명'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='이메일'),
        sa.Column('phone', sa.String(length=50), nullable=False, comment='연락처'),
        sa.Column('business_number', sa.String(length=50), nullable=True, comment='사업자등록번호'),
        sa.Column('address', sa.Text(), nullable=True, comment='주소'),
        sa.Column('description', sa.Text(), nullable=False, comment='상세 소개 및 신청 사유'),
        sa.Column('service_area', sa.String(length=200), nullable=True, comment='서비스 지역'),
        sa.Column('website', sa.String(length=500), nullable=True, comment='웹사이트/SNS'),
        sa.Column('attachments', sa.Text(), nullable=True, comment='첨부파일 정보 JSON'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='신청 상태'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='신청일시'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True, comment='검토일시'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True, comment='검토자 ID'),
        sa.Column('rejection_reason', sa.Text(), nullable=True, comment='반려 사유'),
        sa.Column('notes', sa.Text(), nullable=True, comment='검토 메모'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_community_applications_id'), 'community_applications', ['id'], unique=False)


def downgrade() -> None:
    # Drop community_applications table
    op.drop_index(op.f('ix_community_applications_id'), table_name='community_applications')
    op.drop_table('community_applications')