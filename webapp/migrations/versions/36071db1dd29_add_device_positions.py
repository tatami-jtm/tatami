"""add device positions

Revision ID: 36071db1dd29
Revises: 432227af434c
Create Date: 2023-05-18 16:46:00.948435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36071db1dd29'
down_revision = '432227af434c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device_positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('is_mat', sa.Boolean(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device_positions')
    # ### end Alembic commands ###