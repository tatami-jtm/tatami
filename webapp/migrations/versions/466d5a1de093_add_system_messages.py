"""Add system messages

Revision ID: 466d5a1de093
Revises: 166afb57d575
Create Date: 2024-12-05 09:06:29.857169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '466d5a1de093'
down_revision = '166afb57d575'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('system_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('removed', sa.Boolean(), nullable=True),
    sa.Column('removed_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('system_message')
    # ### end Alembic commands ###