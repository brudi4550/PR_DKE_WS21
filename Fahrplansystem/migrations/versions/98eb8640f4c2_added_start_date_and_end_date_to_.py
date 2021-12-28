"""added start_date and end_date to interval

Revision ID: 98eb8640f4c2
Revises: 69fb789ab2eb
Create Date: 2021-12-28 12:23:18.075248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98eb8640f4c2'
down_revision = '69fb789ab2eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interval', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interval', schema=None) as batch_op:
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')

    # ### end Alembic commands ###
