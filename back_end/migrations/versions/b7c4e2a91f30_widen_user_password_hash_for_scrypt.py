"""widen user.password_hash for scrypt hashes

An scrypt hash, as Werkzeug 3 writes it, takes 162 characters. Downgrading needs those hashes
gone first: MySQL refuses to cut them to 128 characters.

Revision ID: b7c4e2a91f30
Revises: 64da9d7b3859
Create Date: 2026-11-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7c4e2a91f30'
down_revision = '64da9d7b3859'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'password_hash',
               existing_type=sa.String(length=128),
               type_=sa.String(length=255),
               existing_nullable=True)


def downgrade():
    op.alter_column('user', 'password_hash',
               existing_type=sa.String(length=255),
               type_=sa.String(length=128),
               existing_nullable=True)
