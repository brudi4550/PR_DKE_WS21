"""changed warnings

Revision ID: 1d88e03130fe
Revises: 525d218d69ec
Create Date: 2022-01-13 14:17:52.524073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d88e03130fe'
down_revision = '525d218d69ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('route_warning',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('msg', sa.String(length=512), nullable=True),
    sa.Column('route_start', sa.String(length=128), nullable=True),
    sa.Column('route_end', sa.String(length=128), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('system_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['system_id'], ['system.id'], name=op.f('fk_route_warning_system_id_system')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_route_warning'))
    )
    op.create_table('train_warning',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('msg', sa.String(length=512), nullable=True),
    sa.Column('type', sa.String(length=64), nullable=True),
    sa.Column('train', sa.String(length=128), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('system_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['system_id'], ['system.id'], name=op.f('fk_train_warning_system_id_system')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_train_warning'))
    )
    op.drop_table('system_warning')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('system_warning',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('msg', sa.VARCHAR(length=512), nullable=True),
    sa.Column('type', sa.VARCHAR(length=64), nullable=True),
    sa.Column('start', sa.DATETIME(), nullable=True),
    sa.Column('end', sa.DATETIME(), nullable=True),
    sa.Column('system_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['system_id'], ['system.id'], name='fk_system_warning_system_id_system'),
    sa.PrimaryKeyConstraint('id', name='pk_system_warning')
    )
    op.drop_table('train_warning')
    op.drop_table('route_warning')
    # ### end Alembic commands ###
