"""Add worship_type column to community_music_teams table

Revision ID: worship_type_001
Revises: add_community_sharing_additional_fields
Create Date: 2025-09-18 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'worship_type_001'
down_revision = 'add_community_sharing_additional_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Rename team_type to worship_type and add new team_types column"""

    # 1. team_type 컬럼명을 worship_type으로 변경
    op.alter_column('community_music_teams', 'team_type', new_column_name='worship_type')

    # 2. worship_type 컬럼 길이 확장 및 설명 업데이트
    op.alter_column('community_music_teams', 'worship_type',
                   type_=sa.String(length=50),
                   comment='예배 형태 (주일예배, 수요예배, 특별예배 등)')

    # 3. 새로운 team_types 컬럼 추가 (팀 유형용)
    op.add_column('community_music_teams',
                  sa.Column('team_types', sa.JSON, nullable=True,
                           comment='팀 유형 배열 (솔로, 찬양팀, 워십팀, 밴드 등)'))

    # 4. 기존 데이터에 기본값 설정
    op.execute("UPDATE community_music_teams SET team_types = '[\"찬양팀\"]' WHERE team_types IS NULL")


def downgrade():
    """Revert worship_type back to team_type and remove team_types column"""
    # 1. Drop team_types column
    op.drop_column('community_music_teams', 'team_types')

    # 2. Rename worship_type back to team_type
    op.alter_column('community_music_teams', 'worship_type', new_column_name='team_type')

    # 3. Revert team_type column length and comment
    op.alter_column('community_music_teams', 'team_type',
                   type_=sa.String(length=9),
                   comment='팀 유형')