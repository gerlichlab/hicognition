"""Added feature values file_path to EmbeddingIntervalData

Revision ID: e1be82c2252a
Revises: c57bedb77252
Create Date: 2021-08-16 11:04:01.297651

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e1be82c2252a'
down_revision = 'c57bedb77252'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('embedding_interval_data', sa.Column('file_path_feature_values', sa.String(length=512), nullable=True))
    op.create_index(op.f('ix_embedding_interval_data_file_path_feature_values'), 'embedding_interval_data', ['file_path_feature_values'], unique=False)
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
    op.drop_index(op.f('ix_embedding_interval_data_file_path_feature_values'), table_name='embedding_interval_data')
    op.drop_column('embedding_interval_data', 'file_path_feature_values')
    # ### end Alembic commands ###