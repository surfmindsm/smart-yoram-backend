"""add location fields to pastoral care

Revision ID: add_pastoral_location
Revises: add_geocoding_fields
Create Date: 2025-08-22 16:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_pastoral_location"
down_revision: Union[str, None] = "add_geocoding_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns exist before adding them to avoid duplicate column errors
    import sqlalchemy as sa
    from sqlalchemy import inspect
    
    # Get current connection
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('pastoral_care_requests')]
    
    # Add location-related columns to pastoral_care_requests table only if they don't exist
    if "address" not in existing_columns:
        op.add_column(
            "pastoral_care_requests",
            sa.Column("address", sa.String(length=500), nullable=True),
        )
    if "latitude" not in existing_columns:
        op.add_column(
            "pastoral_care_requests",
            sa.Column("latitude", sa.Numeric(precision=10, scale=8), nullable=True),
        )
    if "longitude" not in existing_columns:
        op.add_column(
            "pastoral_care_requests",
            sa.Column("longitude", sa.Numeric(precision=11, scale=8), nullable=True),
        )
    if "contact_info" not in existing_columns:
        op.add_column(
            "pastoral_care_requests",
            sa.Column("contact_info", sa.String(length=500), nullable=True),
        )
    if "is_urgent" not in existing_columns:
        op.add_column(
            "pastoral_care_requests",
            sa.Column("is_urgent", sa.Boolean(), server_default="false", nullable=True),
        )

    # Create indexes only if they don't exist
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('pastoral_care_requests')]
    
    if "idx_pastoral_care_location" not in existing_indexes:
        op.create_index(
            "idx_pastoral_care_location",
            "pastoral_care_requests",
            ["latitude", "longitude"],
            unique=False,
        )

    if "idx_pastoral_care_is_urgent" not in existing_indexes:
        op.create_index(
            "idx_pastoral_care_is_urgent",
            "pastoral_care_requests",
            ["is_urgent"],
            unique=False,
        )


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("idx_pastoral_care_is_urgent", table_name="pastoral_care_requests")
    op.drop_index("idx_pastoral_care_location", table_name="pastoral_care_requests")

    # Drop columns
    op.drop_column("pastoral_care_requests", "is_urgent")
    op.drop_column("pastoral_care_requests", "contact_info")
    op.drop_column("pastoral_care_requests", "longitude")
    op.drop_column("pastoral_care_requests", "latitude")
    op.drop_column("pastoral_care_requests", "address")
