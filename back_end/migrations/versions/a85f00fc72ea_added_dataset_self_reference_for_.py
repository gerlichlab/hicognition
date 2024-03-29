"""added dataset self reference for processing 

Revision ID: a85f00fc72ea
Revises: a664c3c6907c
Create Date: 2021-09-09 09:15:09.918949

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a85f00fc72ea'
down_revision = 'a664c3c6907c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dataset', sa.Column('processing_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'dataset', 'dataset', ['processing_id'], ['id'])
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
    op.drop_constraint(None, 'dataset', type_='foreignkey')
    op.drop_column('dataset', 'processing_id')
    # ### end Alembic commands ###
