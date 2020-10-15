"""added value_type field to pileup

Revision ID: 836b7ebfa399
Revises: 803c1cdf80d3
Create Date: 2020-10-14 09:39:22.166011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '836b7ebfa399'
down_revision = '803c1cdf80d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pileup', sa.Column('value_type', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pileup', 'value_type')
    # ### end Alembic commands ###