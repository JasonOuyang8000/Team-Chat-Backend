"""create-users

Revision ID: e8773af7c7c0
Revises: 
Create Date: 2021-05-20 21:14:18.706426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8773af7c7c0'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('limit', sa.Integer,server_default='2'),
        sa.Column('created',sa.DateTime,  server_default=sa.func.now()),
        sa.Column('updated',sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    )


def downgrade():
    op.drop_table('users')