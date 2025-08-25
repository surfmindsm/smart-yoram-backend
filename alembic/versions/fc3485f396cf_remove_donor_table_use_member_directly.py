"""remove donor table use member directly

Revision ID: fc3485f396cf
Revises: 720469148d76
Create Date: 2024-08-20

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fc3485f396cf"
down_revision = "720469148d76"
branch_labels = None
depends_on = None


def upgrade():
    # First add member_id column as nullable
    op.add_column("offerings", sa.Column("member_id", sa.Integer(), nullable=True))
    op.add_column("receipts", sa.Column("member_id", sa.Integer(), nullable=True))

    # Copy donor's member_id to the new member_id column
    op.execute(
        """
        UPDATE offerings 
        SET member_id = donors.member_id 
        FROM donors 
        WHERE offerings.donor_id = donors.id
    """
    )

    op.execute(
        """
        UPDATE receipts 
        SET member_id = donors.member_id 
        FROM donors 
        WHERE receipts.donor_id = donors.id
    """
    )

    # Drop foreign key constraints that reference donors table
    op.drop_constraint("offerings_donor_id_fkey", "offerings", type_="foreignkey")
    op.drop_constraint("receipts_donor_id_fkey", "receipts", type_="foreignkey")

    # Drop donor_id columns
    op.drop_column("offerings", "donor_id")
    op.drop_column("receipts", "donor_id")

    # Now make member_id not nullable and add foreign keys
    op.alter_column("offerings", "member_id", nullable=False)
    op.create_foreign_key(
        "offerings_member_id_fkey", "offerings", "members", ["member_id"], ["id"]
    )

    op.alter_column("receipts", "member_id", nullable=False)
    op.create_foreign_key(
        "receipts_member_id_fkey", "receipts", "members", ["member_id"], ["id"]
    )

    # Update receipt_snapshots to use member instead of donor
    op.add_column(
        "receipt_snapshots", sa.Column("member_name", sa.String(), nullable=True)
    )
    op.add_column(
        "receipt_snapshots", sa.Column("member_rrn_masked", sa.String(), nullable=True)
    )
    op.add_column(
        "receipt_snapshots", sa.Column("member_address", sa.String(), nullable=True)
    )

    # Copy data from donor columns to member columns
    op.execute(
        """
        UPDATE receipt_snapshots 
        SET member_name = donor_name,
            member_rrn_masked = donor_rrn_masked,
            member_address = donor_address
    """
    )

    # Make member_name not nullable
    op.alter_column("receipt_snapshots", "member_name", nullable=False)

    # Drop donor columns
    op.drop_column("receipt_snapshots", "donor_name")
    op.drop_column("receipt_snapshots", "donor_rrn_masked")
    op.drop_column("receipt_snapshots", "donor_address")

    # Drop donors table
    op.drop_index("ix_donors_id", table_name="donors")
    op.drop_table("donors")


def downgrade():
    # Create donors table
    op.create_table(
        "donors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("legal_name", sa.String(), nullable=False),
        sa.Column("rrn_encrypted", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_donors_id", "donors", ["id"], unique=False)

    # Revert receipt_snapshots
    op.drop_column("receipt_snapshots", "member_address")
    op.drop_column("receipt_snapshots", "member_rrn_masked")
    op.drop_column("receipt_snapshots", "member_name")
    op.add_column(
        "receipt_snapshots",
        sa.Column("donor_address", sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "receipt_snapshots",
        sa.Column("donor_rrn_masked", sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "receipt_snapshots",
        sa.Column("donor_name", sa.String(), autoincrement=False, nullable=False),
    )

    # Revert receipts
    op.drop_constraint("receipts_member_id_fkey", "receipts", type_="foreignkey")
    op.drop_column("receipts", "member_id")
    op.add_column(
        "receipts",
        sa.Column("donor_id", sa.Integer(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "receipts_donor_id_fkey", "receipts", "donors", ["donor_id"], ["id"]
    )

    # Revert offerings
    op.drop_constraint("offerings_member_id_fkey", "offerings", type_="foreignkey")
    op.drop_column("offerings", "member_id")
    op.add_column(
        "offerings",
        sa.Column("donor_id", sa.Integer(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "offerings_donor_id_fkey", "offerings", "donors", ["donor_id"], ["id"]
    )
