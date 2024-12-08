"""Rename organizations to organisations

Revision ID: 6d420c53bf2a
Revises: df1e4450d48c
Create Date: 2024-12-01 16:45:04.278062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d420c53bf2a'
down_revision = 'df1e4450d48c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'organisations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('token', sa.String(length=100), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['owner_id'], ['users.uid'], name='fk_organisation_owner_id', ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id', name='unique_organisation_id'),
        sa.UniqueConstraint('token')
    )

    op.execute('DROP TABLE IF EXISTS organizations CASCADE')

    with op.batch_alter_table('users', schema=None) as batch_op:
        # Check and create the unique constraint if it does not exist
        existing_constraints = sa.inspect(op.get_bind()).get_unique_constraints('users')
        if any(c['name'] == 'unique_owner_organisation' for c in existing_constraints):
            batch_op.drop_constraint('unique_owner_organisation', type_='unique')
        batch_op.create_unique_constraint('unique_owner_organisation', ['organisation_id', 'is_owner'])

        # Check and create the foreign key if it does not exist
        existing_foreign_keys = sa.inspect(op.get_bind()).get_foreign_keys('users')
        if not any(fk['name'] == 'fk_user_organisation_id' for fk in existing_foreign_keys):
            batch_op.create_foreign_key(
                'fk_user_organisation_id',
                'organisations',
                ['organisation_id'],
                ['id'],
                ondelete='SET NULL'
            )


def downgrade():
    # Drop foreign key constraint in 'users'
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_organisation_id', type_='foreignkey')
        batch_op.drop_constraint('unique_owner_organisation', type_='unique')

    # Nullify or update the 'organisation_id' column in 'users' to prevent violations
    op.execute('UPDATE users SET organisation_id = NULL')

    # Recreate the 'organizations' table
    op.create_table(
        'organizations',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('token', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.uid'], name='fk_organisation_owner_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='unique_organization_id'),
        sa.UniqueConstraint('token', name='organizations_token_key')
    )

    # Drop the 'organisations' table
    op.execute('DROP TABLE IF EXISTS organisations CASCADE')

    # Restore foreign key constraints in 'users'
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_user_organisation_id',
            'organizations',
            ['organisation_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_unique_constraint('unique_owner_organisation', ['organisation_id', 'is_owner'])
