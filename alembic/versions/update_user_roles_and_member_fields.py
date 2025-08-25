"""Update user roles and add member fields

Revision ID: update_user_roles_001
Revises: 
Create Date: 2025-01-30

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "update_user_roles_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Check if role column exists, add if not
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='role'
    """
        )
    )

    if result.fetchone() is None:
        op.add_column(
            "users",
            sa.Column("role", sa.String(), nullable=True, server_default="member"),
        )

    # Update existing users based on is_superuser
    op.execute(
        """
        UPDATE users 
        SET role = CASE 
            WHEN is_superuser = true THEN 'admin'
            WHEN full_name LIKE '%목사%' OR full_name LIKE '%pastor%' THEN 'pastor'
            ELSE 'member'
        END
        WHERE role IS NULL
    """
    )

    # Make role not nullable after setting values
    op.alter_column("users", "role", nullable=False)

    # Add new fields to members table
    op.add_column("members", sa.Column("profile_photo_url", sa.String(), nullable=True))
    op.add_column(
        "members",
        sa.Column("member_status", sa.String(), nullable=True, default="active"),
    )
    op.add_column("members", sa.Column("transfer_church", sa.String(), nullable=True))
    op.add_column("members", sa.Column("transfer_date", sa.Date(), nullable=True))
    op.add_column("members", sa.Column("memo", sa.Text(), nullable=True))
    op.add_column(
        "members",
        sa.Column("invitation_sent", sa.Boolean(), nullable=True, default=False),
    )
    op.add_column(
        "members",
        sa.Column("invitation_sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Update existing members status
    op.execute(
        """
        UPDATE members 
        SET member_status = CASE 
            WHEN status = 'active' THEN 'active'
            WHEN status = 'inactive' THEN 'inactive'
            ELSE 'active'
        END
        WHERE member_status IS NULL
    """
    )

    # Create SMS history table
    op.create_table(
        "sms_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_phone", sa.String(), nullable=False),
        sa.Column("recipient_member_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sms_type", sa.String(), nullable=True),  # invitation, notice, etc
        sa.Column("status", sa.String(), nullable=True),  # sent, failed, pending
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["church_id"],
            ["churches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipient_member_id"],
            ["members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create QR codes table
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("qr_type", sa.String(), nullable=True),  # attendance, member_card
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["church_id"],
            ["churches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create calendar events table
    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "event_type", sa.String(), nullable=True
        ),  # birthday, anniversary, service, etc
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=True, default=False),
        sa.Column(
            "recurrence_pattern", sa.String(), nullable=True
        ),  # yearly, monthly, weekly
        sa.Column("related_member_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["church_id"],
            ["churches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["related_member_id"],
            ["members.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "notification_type", sa.String(), nullable=True
        ),  # birthday, event, announcement
        sa.Column("is_read", sa.Boolean(), nullable=True, default=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["church_id"],
            ["churches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create family relationships table
    op.create_table(
        "family_relationships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("church_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("related_member_id", sa.Integer(), nullable=False),
        sa.Column(
            "relationship_type", sa.String(), nullable=False
        ),  # 부모, 자녀, 배우자, 형제, 자매 등
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["church_id"],
            ["churches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["members.id"],
        ),
        sa.ForeignKeyConstraint(
            ["related_member_id"],
            ["members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add indexes
    op.create_index("idx_members_status", "members", ["member_status"])
    op.create_index("idx_sms_history_church", "sms_history", ["church_id"])
    op.create_index("idx_qr_codes_member", "qr_codes", ["member_id"])
    op.create_index("idx_calendar_events_date", "calendar_events", ["event_date"])
    op.create_index("idx_notifications_user", "notifications", ["user_id", "is_read"])
    op.create_index(
        "idx_family_relationships_member", "family_relationships", ["member_id"]
    )
    op.create_index(
        "idx_family_relationships_related",
        "family_relationships",
        ["related_member_id"],
    )


def downgrade():
    # Drop indexes
    op.drop_index("idx_family_relationships_related", "family_relationships")
    op.drop_index("idx_family_relationships_member", "family_relationships")
    op.drop_index("idx_notifications_user", "notifications")
    op.drop_index("idx_calendar_events_date", "calendar_events")
    op.drop_index("idx_qr_codes_member", "qr_codes")
    op.drop_index("idx_sms_history_church", "sms_history")
    op.drop_index("idx_members_status", "members")

    # Drop tables
    op.drop_table("family_relationships")
    op.drop_table("notifications")
    op.drop_table("calendar_events")
    op.drop_table("qr_codes")
    op.drop_table("sms_history")

    # Remove columns from members
    op.drop_column("members", "invitation_sent_at")
    op.drop_column("members", "invitation_sent")
    op.drop_column("members", "memo")
    op.drop_column("members", "transfer_date")
    op.drop_column("members", "transfer_church")
    op.drop_column("members", "member_status")
    op.drop_column("members", "profile_photo_url")

    # Remove role from users
    op.drop_column("users", "role")
