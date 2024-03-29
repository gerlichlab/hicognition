"""added public flag to collections

Revision ID: 5ea96c0a7508
Revises: 56fdb3b41c8f
Create Date: 2021-07-26 14:01:07.982002

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "5ea96c0a7508"
down_revision = "56fdb3b41c8f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("collection", sa.Column("public", sa.Boolean(), nullable=True))
    op.alter_column(
        "session",
        "session_object",
        existing_type=mysql.LONGTEXT(),
        type_=sa.Text(length=1000000000),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "session",
        "session_object",
        existing_type=sa.Text(length=1000000000),
        type_=mysql.LONGTEXT(),
        existing_nullable=True,
    )
    op.drop_column("collection", "public")
    # ### end Alembic commands ###
