"""initial migration

Revision ID: 77c203bacb71
Revises: 
Create Date: 2024-11-27 19:36:20.550468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77c203bacb71'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the users table first without the foreign key to organizations
    op.create_table(
        'users',
        sa.Column('uid', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('last_location', sa.String(length=100), nullable=True),
        sa.Column('is_owner', sa.Boolean(), nullable=True),
        sa.Column('organisation_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('uid'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('organisation_id', 'is_owner', name='unique_owner_organization')
    )

    # Create the organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('token', sa.String(length=100), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id', name='unique_organization_id'),
        sa.UniqueConstraint('token')
    )

    # Add the foreign key from users to organizations
    op.create_foreign_key(
        'fk_user_organisation_id', 'users', 'organizations',
        ['organisation_id'], ['id']
    )

    # Add the foreign key from organizations to users
    op.create_foreign_key(
        'fk_organisation_owner_id', 'organizations', 'users',
        ['owner_id'], ['uid']
    )

    # Create the agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.uid']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create the managers table
    op.create_table(
        'managers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.uid']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create the reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=300), nullable=False),
        sa.Column('photo_file', sa.String(length=100), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['approver_id'], ['managers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.uid']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop dependent tables and constraints in the correct order
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.drop_constraint('fk_organisation_owner_id', type_='foreignkey')

    # Drop tables in reverse order of creation
    op.drop_table('reports')
    op.drop_table('managers')
    op.drop_table('agents')
    op.drop_table('users')
    op.drop_table('organizations')
