"""empty message

Revision ID: 8231959f871a
Revises: efc80107167c
Create Date: 2018-07-14 18:52:25.134633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8231959f871a'
down_revision = 'efc80107167c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity', sa.Column('added_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activity', 'added_date')
    # ### end Alembic commands ###
