"""Add team team (participant) model

Revision ID: fcb3696f5c43
Revises: 10e4dca47c46
Create Date: 2024-10-12 22:33:30.597287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcb3696f5c43'
down_revision = '10e4dca47c46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_name', sa.String(length=80), nullable=True),
    sa.Column('team_registration_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('event_class_id', sa.Integer(), nullable=True),
    sa.Column('placement_index', sa.Integer(), nullable=True),
    sa.Column('manually_placed', sa.Boolean(), nullable=True),
    sa.Column('final_placement', sa.Integer(), nullable=True),
    sa.Column('final_points', sa.Integer(), nullable=True),
    sa.Column('final_score', sa.Integer(), nullable=True),
    sa.Column('removed', sa.Boolean(), nullable=True),
    sa.Column('disqualified', sa.Boolean(), nullable=True),
    sa.Column('removal_cause', sa.Text(length=250), nullable=True),
    sa.ForeignKeyConstraint(['event_class_id'], ['event_class.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['team_registration_id'], ['team_registration.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team')
    # ### end Alembic commands ###