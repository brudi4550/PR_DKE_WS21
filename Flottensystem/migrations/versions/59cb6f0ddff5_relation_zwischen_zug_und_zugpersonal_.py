"""Relation zwischen Zug und Zugpersonal wurde hinzugefügt

Revision ID: 59cb6f0ddff5
Revises: 9053b297cad0
Create Date: 2021-12-25 02:50:45.478093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59cb6f0ddff5'
down_revision = '9053b297cad0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('zugpersonal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('zug_nr', sa.String(length=255), nullable=False))
        batch_op.create_foreign_key('fk_zugpersonal_zug_nr_zug', 'zug', ['zug_nr'], ['nr'])
        batch_op.drop_column('zug')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('zugpersonal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('zug', sa.VARCHAR(length=255), nullable=False))
        batch_op.drop_constraint('fk_zugpersonal_zug_nr_zug', type_='foreignkey')
        batch_op.drop_column('zug_nr')

    # ### end Alembic commands ###
