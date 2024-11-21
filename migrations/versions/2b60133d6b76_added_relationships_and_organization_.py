"""added relationships and organization users

Revision ID: 2b60133d6b76
Revises: 6175b7efb0f7
Create Date: 2024-11-21 13:18:32.855205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b60133d6b76'
down_revision = '6175b7efb0f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organization_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=False),
    sa.Column('photo_file', sa.String(length=100), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('report')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_location', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_location')

    op.create_table('report',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('location', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=300), autoincrement=False, nullable=False),
    sa.Column('photo_file', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='report_pkey')
    )
    op.drop_table('reports')
    op.drop_table('organization_user')
    # ### end Alembic commands ###
