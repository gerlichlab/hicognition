"""removed Intervals filepath

Revision ID: 5d8dd6f7a612
Revises: 26c3c7438f59
Create Date: 2021-09-15 09:42:02.379737

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5d8dd6f7a612'
down_revision = '26c3c7438f59'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_intervals_file_path', table_name='intervals')
    op.drop_column('intervals', 'file_path')
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
    op.add_column('intervals', sa.Column('file_path', mysql.VARCHAR(length=512), nullable=True))
    op.create_index('ix_intervals_file_path', 'intervals', ['file_path'], unique=False)
    # ### end Alembic commands ###
