"""Create policy recommendation table

Revision ID: 88c638181c3a
Revises: e519d6e5aa6b
Create Date: 2019-12-07 14:45:26.038661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "88c638181c3a"
down_revision = "e519d6e5aa6b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "policy_recommendation",
        sa.Column(
            "user_uuid",
            sa.String(36),
            sa.ForeignKey("user.uuid"),
            unique=True,
            nullable=False,
        ),
        sa.Column("data", sa.JSON, nullable=True),
    )


def downgrade():
    op.drop_table("policy_recommendation")
