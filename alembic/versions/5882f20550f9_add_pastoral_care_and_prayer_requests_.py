"""add_pastoral_care_and_prayer_requests_tables

Revision ID: 5882f20550f9
Revises: 3f9489593c84
Create Date: 2025-08-12 17:10:27.903813

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "5882f20550f9"
down_revision: Union[str, None] = "3f9489593c84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pastoral_care_requests table
    op.create_table(
        "pastoral_care_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("requester_name", sa.String(length=100), nullable=False),
        sa.Column("requester_phone", sa.String(length=20), nullable=False),
        sa.Column(
            "request_type",
            sa.String(length=50),
            server_default="general",
            nullable=True,
        ),
        sa.Column("request_content", sa.Text(), nullable=False),
        sa.Column("preferred_date", sa.Date(), nullable=True),
        sa.Column("preferred_time_start", sa.Time(), nullable=True),
        sa.Column("preferred_time_end", sa.Time(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), server_default="pending", nullable=True
        ),
        sa.Column(
            "priority", sa.String(length=20), server_default="normal", nullable=True
        ),
        sa.Column("assigned_pastor_id", sa.Integer(), nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("scheduled_time", sa.Time(), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            onupdate=sa.func.now(),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_pastor_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(["church_id"], ["churches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_pastoral_care_church_id",
        "pastoral_care_requests",
        ["church_id"],
        unique=False,
    )
    op.create_index(
        "idx_pastoral_care_created_at",
        "pastoral_care_requests",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "idx_pastoral_care_member_id",
        "pastoral_care_requests",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        "idx_pastoral_care_priority",
        "pastoral_care_requests",
        ["priority"],
        unique=False,
    )
    op.create_index(
        "idx_pastoral_care_status", "pastoral_care_requests", ["status"], unique=False
    )

    # Create prayer_requests table
    op.create_table(
        "prayer_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("requester_name", sa.String(length=100), nullable=False),
        sa.Column("requester_phone", sa.String(length=20), nullable=True),
        sa.Column(
            "prayer_type", sa.String(length=50), server_default="general", nullable=True
        ),
        sa.Column("prayer_content", sa.Text(), nullable=False),
        sa.Column("is_anonymous", sa.Boolean(), server_default="false", nullable=True),
        sa.Column("is_urgent", sa.Boolean(), server_default="false", nullable=True),
        sa.Column(
            "status", sa.String(length=20), server_default="active", nullable=True
        ),
        sa.Column("is_public", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("answered_testimony", sa.Text(), nullable=True),
        sa.Column("prayer_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            onupdate=sa.func.now(),
            nullable=True,
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(NOW() + INTERVAL '30 days')"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["church_id"], ["churches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_prayer_requests_church_id", "prayer_requests", ["church_id"], unique=False
    )
    op.create_index(
        "idx_prayer_requests_created_at",
        "prayer_requests",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "idx_prayer_requests_expires_at",
        "prayer_requests",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        "idx_prayer_requests_is_public", "prayer_requests", ["is_public"], unique=False
    )
    op.create_index(
        "idx_prayer_requests_member_id", "prayer_requests", ["member_id"], unique=False
    )
    op.create_index(
        "idx_prayer_requests_status", "prayer_requests", ["status"], unique=False
    )

    # Create prayer_participations table
    op.create_table(
        "prayer_participations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prayer_request_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column(
            "participated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["church_id"], ["churches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["prayer_request_id"], ["prayer_requests.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prayer_request_id", "member_id"),
    )
    op.create_index(
        "idx_prayer_participations_member_id",
        "prayer_participations",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        "idx_prayer_participations_prayer_id",
        "prayer_participations",
        ["prayer_request_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_index(
        "idx_prayer_participations_prayer_id", table_name="prayer_participations"
    )
    op.drop_index(
        "idx_prayer_participations_member_id", table_name="prayer_participations"
    )
    op.drop_table("prayer_participations")

    op.drop_index("idx_prayer_requests_status", table_name="prayer_requests")
    op.drop_index("idx_prayer_requests_member_id", table_name="prayer_requests")
    op.drop_index("idx_prayer_requests_is_public", table_name="prayer_requests")
    op.drop_index("idx_prayer_requests_expires_at", table_name="prayer_requests")
    op.drop_index("idx_prayer_requests_created_at", table_name="prayer_requests")
    op.drop_index("idx_prayer_requests_church_id", table_name="prayer_requests")
    op.drop_table("prayer_requests")

    op.drop_index("idx_pastoral_care_status", table_name="pastoral_care_requests")
    op.drop_index("idx_pastoral_care_priority", table_name="pastoral_care_requests")
    op.drop_index("idx_pastoral_care_member_id", table_name="pastoral_care_requests")
    op.drop_index("idx_pastoral_care_created_at", table_name="pastoral_care_requests")
    op.drop_index("idx_pastoral_care_church_id", table_name="pastoral_care_requests")
    op.drop_table("pastoral_care_requests")
