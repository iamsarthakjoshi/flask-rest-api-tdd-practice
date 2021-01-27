"""Create insurance questionnaire table

Revision ID: e519d6e5aa6b
Revises: 2b01d69e855f
Create Date: 2019-12-06 22:33:42.574417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e519d6e5aa6b"
down_revision = "2b01d69e855f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "insurance_questionnaire",
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
    op.drop_table("insurance_questionnaire")
