"""Add church_news table for community news feature

Revision ID: add_church_news_001
Revises: 65ee06adcadf
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = 'add_church_news_001'
down_revision: Union[str, None] = '65ee06adcadf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # church_news 테이블 생성
    op.create_table(
        'church_news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.Enum('urgent', 'important', 'normal', name='newspriority'), nullable=True),
        
        # 행사 정보
        sa.Column('event_date', sa.Date(), nullable=True),
        sa.Column('event_time', sa.Time(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('organizer', sa.String(length=100), nullable=False),
        sa.Column('target_audience', sa.String(length=100), nullable=True),
        sa.Column('participation_fee', sa.String(length=50), nullable=True),
        
        # 신청 관련
        sa.Column('registration_required', sa.Boolean(), nullable=True),
        sa.Column('registration_deadline', sa.Date(), nullable=True),
        
        # 연락처 정보
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=100), nullable=True),
        
        # 상태 관리
        sa.Column('status', sa.Enum('active', 'completed', 'cancelled', name='newsstatus'), nullable=True),
        
        # 메타데이터
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=True),
        
        # 태그 및 이미지
        sa.Column('tags', JSON, nullable=True),
        sa.Column('images', JSON, nullable=True),
        
        # 공통 필드
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        
        # 작성자 정보
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('church_id', sa.Integer(), nullable=True),
        
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 인덱스 생성
    op.create_index(op.f('ix_church_news_id'), 'church_news', ['id'], unique=False)
    op.create_index(op.f('ix_church_news_title'), 'church_news', ['title'], unique=False)
    op.create_index(op.f('ix_church_news_category'), 'church_news', ['category'], unique=False)
    op.create_index(op.f('ix_church_news_priority'), 'church_news', ['priority'], unique=False)
    op.create_index(op.f('ix_church_news_status'), 'church_news', ['status'], unique=False)
    op.create_index(op.f('ix_church_news_event_date'), 'church_news', ['event_date'], unique=False)
    op.create_index(op.f('ix_church_news_created_at'), 'church_news', ['created_at'], unique=False)


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index(op.f('ix_church_news_created_at'), table_name='church_news')
    op.drop_index(op.f('ix_church_news_event_date'), table_name='church_news')
    op.drop_index(op.f('ix_church_news_status'), table_name='church_news')
    op.drop_index(op.f('ix_church_news_priority'), table_name='church_news')
    op.drop_index(op.f('ix_church_news_category'), table_name='church_news')
    op.drop_index(op.f('ix_church_news_title'), table_name='church_news')
    op.drop_index(op.f('ix_church_news_id'), table_name='church_news')
    
    # 테이블 삭제
    op.drop_table('church_news')
    
    # Enum 타입 삭제
    op.execute('DROP TYPE IF EXISTS newsstatus')
    op.execute('DROP TYPE IF EXISTS newspriority')