"""adiciona coluna is_hidden para posts

Revision ID: a26549d4f779
Revises: 0cae1e934c69
Create Date: 2025-03-16 07:04:21.897513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a26549d4f779'
down_revision = '0cae1e934c69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_hidden', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('is_hidden')

    # ### end Alembic commands ###
