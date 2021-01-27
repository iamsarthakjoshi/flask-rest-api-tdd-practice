"""create_insurance_policy_wordings_table

Revision ID: a82ed66e47ff
Revises: 88c638181c3a
Create Date: 2020-01-15 15:02:25.395868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a82ed66e47ff"
down_revision = "88c638181c3a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "insurance_policy_wordings",
        sa.Column(
            "user_uuid",
            sa.String(36),
            sa.ForeignKey("user.uuid"),
            unique=True,
            nullable=False,
        ),
        sa.Column("teaser_data", sa.JSON, nullable=True),
        sa.Column("full_data", sa.JSON, nullable=True),
    )


def downgrade():
    op.drop_table("insurance_policy_wordings")
