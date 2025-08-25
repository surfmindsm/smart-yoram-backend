"""Update default GPT model to gpt-4o-mini

Revision ID: update_default_gpt_model
Revises: b4075dd9aed3
Create Date: 2025-01-11 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "update_default_gpt_model"
down_revision = "b4075dd9aed3"
branch_labels = None
depends_on = None


def upgrade():
    # Update existing churches to use gpt-4o-mini if they're using the old default
    op.execute(
        """
        UPDATE churches 
        SET gpt_model = 'gpt-4o-mini' 
        WHERE gpt_model = 'gpt-4' OR gpt_model IS NULL
    """
    )

    # Update the column default
    op.alter_column(
        "churches",
        "gpt_model",
        server_default="gpt-4o-mini",
        existing_type=sa.String(50),
    )


def downgrade():
    # Revert to gpt-4
    op.execute(
        """
        UPDATE churches 
        SET gpt_model = 'gpt-4' 
        WHERE gpt_model = 'gpt-4o-mini'
    """
    )

    # Update the column default
    op.alter_column(
        "churches", "gpt_model", server_default="gpt-4", existing_type=sa.String(50)
    )
