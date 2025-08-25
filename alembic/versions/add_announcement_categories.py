"""Add announcement categories

Revision ID: add_announcement_categories
Revises: 
Create Date: 2024-08-01

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_announcement_categories"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add category and subcategory columns
    op.add_column("announcements", sa.Column("category", sa.String(), nullable=True))
    op.add_column("announcements", sa.Column("subcategory", sa.String(), nullable=True))

    # Set default values for existing records
    op.execute("UPDATE announcements SET category = 'event' WHERE category IS NULL")

    # Make category non-nullable after setting defaults
    op.alter_column("announcements", "category", nullable=False)


def downgrade():
    op.drop_column("announcements", "subcategory")
    op.drop_column("announcements", "category")
