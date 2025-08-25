"""add daily_verses table

Revision ID: add_daily_verses_001
Revises: 7d9cf906b957
Create Date: 2024-08-01 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_daily_verses_001"
down_revision = "7d9cf906b957"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create daily_verses table
    op.create_table(
        "daily_verses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("verse", sa.Text(), nullable=False, comment="성경 구절 내용"),
        sa.Column(
            "reference",
            sa.String(length=100),
            nullable=False,
            comment="성경 구절 출처 (예: 시편 23:1)",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
            server_default="true",
            comment="활성 상태",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_verses_id"), "daily_verses", ["id"], unique=False)
    op.create_index(
        op.f("ix_daily_verses_is_active"), "daily_verses", ["is_active"], unique=False
    )


def downgrade() -> None:
    # Drop daily_verses table
    op.drop_index(op.f("ix_daily_verses_is_active"), table_name="daily_verses")
    op.drop_index(op.f("ix_daily_verses_id"), table_name="daily_verses")
    op.drop_table("daily_verses")
