"""add_location_fields_to_pastoral_care

Revision ID: add_location_fields_pastoral
Revises: add_geocoding_fields
Create Date: 2025-08-22 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_location_fields_pastoral'
down_revision: Union[str, None] = 'add_geocoding_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add location-related columns to pastoral_care_requests table
    op.add_column('pastoral_care_requests', sa.Column('address', sa.String(length=500), nullable=True))
    op.add_column('pastoral_care_requests', sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True))
    op.add_column('pastoral_care_requests', sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True))
    op.add_column('pastoral_care_requests', sa.Column('contact_info', sa.String(length=500), nullable=True))
    op.add_column('pastoral_care_requests', sa.Column('is_urgent', sa.Boolean(), server_default='false', nullable=True))
    
    # Create index for location-based queries
    op.create_index('idx_pastoral_care_location', 'pastoral_care_requests', ['latitude', 'longitude'], unique=False)
    
    # Create index for urgent requests
    op.create_index('idx_pastoral_care_is_urgent', 'pastoral_care_requests', ['is_urgent'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_pastoral_care_is_urgent', table_name='pastoral_care_requests')
    op.drop_index('idx_pastoral_care_location', table_name='pastoral_care_requests')
    
    # Drop columns
    op.drop_column('pastoral_care_requests', 'is_urgent')
    op.drop_column('pastoral_care_requests', 'contact_info')
    op.drop_column('pastoral_care_requests', 'longitude')
    op.drop_column('pastoral_care_requests', 'latitude')
    op.drop_column('pastoral_care_requests', 'address')