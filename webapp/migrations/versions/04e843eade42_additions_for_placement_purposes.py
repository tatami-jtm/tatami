"""additions for placement purposes

Revision ID: 04e843eade42
Revises: 043997f02be2
Create Date: 2023-11-25 18:26:38.444769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04e843eade42'
down_revision = '043997f02be2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('participant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('placement_index', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('manually_placed', sa.Boolean(), nullable=True))

    with op.batch_alter_table('registration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('placed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('placed', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registration', schema=None) as batch_op:
        batch_op.drop_column('placed')
        batch_op.drop_column('placed_at')

    with op.batch_alter_table('participant', schema=None) as batch_op:
        batch_op.drop_column('manually_placed')
        batch_op.drop_column('placement_index')

    # ### end Alembic commands ###
