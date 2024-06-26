"""add registrations and associations

Revision ID: 7a3121a7283b
Revises: b33a69452dc5
Create Date: 2023-11-10 15:44:36.881187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a3121a7283b'
down_revision = 'b33a69452dc5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('association',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('short_name', sa.String(length=10), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('registration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=80), nullable=True),
    sa.Column('last_name', sa.String(length=80), nullable=True),
    sa.Column('contact_details', sa.Text(), nullable=True),
    sa.Column('club', sa.String(length=150), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('event_class_id', sa.Integer(), nullable=True),
    sa.Column('association_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('registered_at', sa.DateTime(), nullable=True),
    sa.Column('weighed_in_at', sa.DateTime(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('registered', sa.Boolean(), nullable=True),
    sa.Column('weighed_in', sa.Boolean(), nullable=True),
    sa.Column('suggested_group', sa.String(length=150), nullable=True),
    sa.Column('verified_weight', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['association_id'], ['association.id'], ),
    sa.ForeignKeyConstraint(['event_class_id'], ['event_class.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('registration')
    op.drop_table('association')
    # ### end Alembic commands ###
