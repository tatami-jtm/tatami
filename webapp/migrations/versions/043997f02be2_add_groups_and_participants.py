"""add groups and participants

Revision ID: 043997f02be2
Revises: 7a3121a7283b
Create Date: 2023-11-25 17:47:42.755993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '043997f02be2'
down_revision = '7a3121a7283b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('event_class_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_class_id'], ['event_class.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('participant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=80), nullable=True),
    sa.Column('association_name', sa.String(length=80), nullable=True),
    sa.Column('final_placement', sa.Integer(), nullable=True),
    sa.Column('final_points', sa.Integer(), nullable=True),
    sa.Column('final_score', sa.Integer(), nullable=True),
    sa.Column('removed', sa.Boolean(), nullable=True),
    sa.Column('disqualified', sa.Boolean(), nullable=True),
    sa.Column('removal_cause', sa.Text(length=250), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registration.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('participant')
    op.drop_table('group')
    # ### end Alembic commands ###