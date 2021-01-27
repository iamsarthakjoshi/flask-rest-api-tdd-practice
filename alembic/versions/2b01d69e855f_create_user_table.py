"""Create user table

Revision ID: 2b01d69e855f
Revises: 
Create Date: 2019-12-06 21:57:05.585134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b01d69e855f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("uuid", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(16), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(77)),
    )


def downgrade():
    op.drop_table("user")
