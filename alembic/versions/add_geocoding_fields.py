"""Add latitude and longitude fields for geocoding

Revision ID: add_geocoding_fields
Revises: fc3485f396cf
Create Date: 2025-01-22 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_geocoding_fields'
down_revision = 'fc3485f396cf'
branch_labels = None
depends_on = None


def upgrade():
    # Add latitude and longitude to members table
    op.add_column('members', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('members', sa.Column('longitude', sa.Float(), nullable=True))
    
    # Add latitude and longitude to families table
    op.add_column('families', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('families', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade():
    # Remove columns from families table
    op.drop_column('families', 'longitude')
    op.drop_column('families', 'latitude')
    
    # Remove columns from members table
    op.drop_column('members', 'longitude')
    op.drop_column('members', 'latitude')