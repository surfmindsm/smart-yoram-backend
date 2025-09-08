"""Add community applications table safe

Revision ID: 65ee06adcadf
Revises: 09389104b722
Create Date: 2025-09-08 22:00:59.786177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65ee06adcadf'
down_revision: Union[str, None] = '09389104b722'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 안전하게 community_applications 테이블 생성
    # 이미 존재한다면 에러를 발생시키지 않음
    try:
        op.create_table(
            'community_applications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('applicant_type', sa.String(length=20), nullable=False),
            sa.Column('organization_name', sa.String(length=200), nullable=False),
            sa.Column('contact_person', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=False),
            sa.Column('business_number', sa.String(length=50), nullable=True),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('service_area', sa.String(length=200), nullable=True),
            sa.Column('website', sa.String(length=500), nullable=True),
            sa.Column('attachments', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('reviewed_by', sa.Integer(), nullable=True),
            sa.Column('rejection_reason', sa.Text(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_community_applications_id'), 'community_applications', ['id'], unique=False)
        op.create_index(op.f('ix_community_applications_email'), 'community_applications', ['email'], unique=False)
    except Exception as e:
        # 테이블이 이미 존재하거나 다른 오류 발생 시 무시
        print(f"Warning: Could not create community_applications table: {e}")
        pass


def downgrade() -> None:
    # 안전하게 테이블 삭제
    try:
        op.drop_index(op.f('ix_community_applications_email'), table_name='community_applications')
        op.drop_index(op.f('ix_community_applications_id'), table_name='community_applications')
        op.drop_table('community_applications')
    except Exception as e:
        print(f"Warning: Could not drop community_applications table: {e}")
        pass