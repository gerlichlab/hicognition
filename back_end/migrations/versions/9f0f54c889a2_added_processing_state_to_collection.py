"""Added processing state to collection

Revision ID: 9f0f54c889a2
Revises: 096e3802a6db
Create Date: 2021-07-28 08:57:20.346093

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "9f0f54c889a2"
down_revision = "096e3802a6db"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "collection", sa.Column("processing_state", sa.String(length=64), nullable=True)
    )
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
    op.drop_column("collection", "processing_state")
    # ### end Alembic commands ###
