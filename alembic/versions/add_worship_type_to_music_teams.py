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
    """Add worship_type column to community_music_teams table"""
    # Add worship_type column
    op.add_column('community_music_teams',
                  sa.Column('worship_type', sa.String(length=50), nullable=True,
                           comment='예배 형태 (주일예배, 수요예배, 특별예배 등)'))

    # Update existing records with default value
    op.execute("UPDATE community_music_teams SET worship_type = '주일예배' WHERE worship_type IS NULL")

    # Make the column NOT NULL after setting default values
    op.alter_column('community_music_teams', 'worship_type', nullable=False)

    # Update team_type column length to accommodate longer values
    op.alter_column('community_music_teams', 'team_type',
                   type_=sa.String(length=50),
                   comment='팀 형태 (찬양팀, 워십팀, 밴드, 오케스트라 등)')


def downgrade():
    """Remove worship_type column from community_music_teams table"""
    # Drop worship_type column
    op.drop_column('community_music_teams', 'worship_type')

    # Revert team_type column length
    op.alter_column('community_music_teams', 'team_type',
                   type_=sa.String(length=9),
                   comment='팀 유형')