"""added unique constraint to association tables

Revision ID: 26c3c7438f59
Revises: ee06748b98a3
Create Date: 2021-09-14 08:56:27.418734

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '26c3c7438f59'
down_revision = 'ee06748b98a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uix_1', 'collections_failed_table', ['dataset_region', 'collection_feature'])
    op.create_unique_constraint('uix_1', 'collections_preprocessing_table', ['dataset_region', 'collection_feature'])
    op.create_unique_constraint('uix_1', 'dataset_completed_table', ['dataset_region', 'dataset_feature'])
    op.create_unique_constraint('uix_1', 'dataset_dataset_preprocessing_table', ['dataset_region', 'dataset_feature'])
    op.create_unique_constraint('uix_1', 'dataset_failed_table', ['dataset_region', 'dataset_feature'])
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
    op.drop_constraint('uix_1', 'dataset_failed_table', type_='unique')
    op.drop_constraint('uix_1', 'dataset_dataset_preprocessing_table', type_='unique')
    op.drop_constraint('uix_1', 'dataset_completed_table', type_='unique')
    op.drop_constraint('uix_1', 'collections_preprocessing_table', type_='unique')
    op.drop_constraint('uix_1', 'collections_failed_table', type_='unique')
    # ### end Alembic commands ###
