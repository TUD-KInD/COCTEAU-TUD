"""add mode to the scenario table

Revision ID: db5c45af24c7
Revises: c2a8bbbbabc1
Create Date: 2021-11-21 15:45:53.947311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db5c45af24c7'
down_revision = 'c2a8bbbbabc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scenario', sa.Column('mode', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scenario', 'mode')
    # ### end Alembic commands ###
