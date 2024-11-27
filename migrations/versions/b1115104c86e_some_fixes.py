"""some fixes

Revision ID: b1115104c86e
Revises: c9d3f236b811
Create Date: 2024-11-21 15:46:52.664109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1115104c86e'
down_revision = 'c9d3f236b811'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('task_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'tasks', ['task_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('task_id')

    # ### end Alembic commands ###