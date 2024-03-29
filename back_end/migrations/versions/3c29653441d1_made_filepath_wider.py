"""made filepath wider

Revision ID: 3c29653441d1
Revises: 40bed80bef7c
Create Date: 2021-10-19 09:46:19.473990

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3c29653441d1'
down_revision = '40bed80bef7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('dataset', 'file_path',
               existing_type=mysql.VARCHAR(length=128),
               type_=sa.String(length=512),
               existing_nullable=True)
    op.alter_column('session', 'session_object',
               existing_type=mysql.LONGTEXT(),
               type_=sa.Text(length=1000000000),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'session_object',
               existing_type=sa.Text(length=1000000000),
               type_=mysql.LONGTEXT(),
               existing_nullable=True)
    op.alter_column('dataset', 'file_path',
               existing_type=sa.String(length=512),
               type_=mysql.VARCHAR(length=128),
               existing_nullable=True)
    # ### end Alembic commands ###
