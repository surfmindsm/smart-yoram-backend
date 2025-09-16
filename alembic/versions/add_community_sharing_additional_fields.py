"""Add additional fields to community_sharing table

Revision ID: community_sharing_update_001
Revises: 4fe66c56fd0d
Create Date: 2025-09-16 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'community_sharing_update_001'
down_revision = '4fe66c56fd0d'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to community_sharing if they don't exist

    # Check if is_free column exists, if not add it
    try:
        op.add_column('community_sharing', sa.Column('is_free', sa.Boolean(), nullable=True, default=True, comment='무료 여부'))
    except:
        pass  # Column already exists

    # Check if price column exists, if not add it
    try:
        op.add_column('community_sharing', sa.Column('price', sa.Integer(), nullable=True, default=0, comment='가격'))
    except:
        pass  # Column already exists

    # Check if view_count column exists (might be named 'views' in existing table)
    try:
        op.add_column('community_sharing', sa.Column('view_count', sa.Integer(), nullable=True, default=0, comment='조회수'))
    except:
        pass  # Column already exists or named differently

    # Ensure contact_info column exists (should already exist from previous migration)
    # This is just for safety
    try:
        op.add_column('community_sharing', sa.Column('contact_info', sa.String(), nullable=True, comment='연락처 정보'))
    except:
        pass  # Column already exists


def downgrade():
    # Remove the columns we added
    try:
        op.drop_column('community_sharing', 'is_free')
    except:
        pass

    try:
        op.drop_column('community_sharing', 'price')
    except:
        pass

    try:
        op.drop_column('community_sharing', 'view_count')
    except:
        pass