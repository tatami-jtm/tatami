"""add reference to positions to registrations

Revision ID: 9fc0ffe2f89a
Revises: f345ad49aa08
Create Date: 2023-05-18 16:47:14.104314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fc0ffe2f89a'
down_revision = 'f345ad49aa08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device_registration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('position_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key("device_registration_positions", 'device_position', ['position_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device_registration', schema=None) as batch_op:
        batch_op.drop_constraint("device_registration_positions", type_='foreignkey')
        batch_op.drop_column('position_id')

    # ### end Alembic commands ###
