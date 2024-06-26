"""Rename display to beamer in event roles

Revision ID: 7552fa4602c6
Revises: f3c953231c08
Create Date: 2024-04-02 02:19:02.047998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7552fa4602c6'
down_revision = 'f3c953231c08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event_role', schema=None) as batch_op:
        batch_op.add_column(sa.Column('may_use_beamer', sa.Boolean(), nullable=True))
        batch_op.drop_column('may_use_display')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event_role', schema=None) as batch_op:
        batch_op.add_column(sa.Column('may_use_display', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('may_use_beamer')

    # ### end Alembic commands ###
