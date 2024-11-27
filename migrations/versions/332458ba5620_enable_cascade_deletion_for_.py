"""Enable CASCADE deletion for organisation owner_id

Revision ID: 332458ba5620
Revises: 77c203bacb71
Create Date: 2024-11-27 20:05:57.202553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '332458ba5620'
down_revision = '77c203bacb71'
branch_labels = None
depends_on = None


def upgrade():
    # Modify the organizations table
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        # Drop the existing foreign key
        batch_op.drop_constraint('fk_organisation_owner_id', type_='foreignkey')

        # Add a new foreign key with CASCADE
        batch_op.create_foreign_key(
            'fk_organisation_owner_id',
            'users',
            ['owner_id'],
            ['uid'],
            ondelete='CASCADE'
        )


def downgrade():
    # Reverse changes made in the upgrade
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        # Drop the CASCADE foreign key
        batch_op.drop_constraint('fk_organisation_owner_id', type_='foreignkey')

        # Recreate the original foreign key without CASCADE
        batch_op.create_foreign_key(
            'fk_organisation_owner_id',
            'users',
            ['owner_id'],
            ['uid']
        )
