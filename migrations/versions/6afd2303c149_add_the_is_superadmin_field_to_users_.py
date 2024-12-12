"""Add the is_superadmin field to users table

Revision ID: 6afd2303c149
Revises: 6d420c53bf2a
Create Date: 2024-12-08 14:05:13.025664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6afd2303c149'
down_revision = '6d420c53bf2a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_superadmin', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_superadmin')
