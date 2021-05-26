"""create-workspace

Revision ID: 4803697bb40a
Revises: e8773af7c7c0
Create Date: 2021-05-20 21:53:03.853932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4803697bb40a'
down_revision = 'e8773af7c7c0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=True),
        sa.Column('protected', sa.Boolean, default=False),
        sa.Column('image',sa.Text,nullable=False),
        sa.Column('ownerId', sa.Integer),
        sa.Column('created',sa.DateTime,  server_default=sa.func.now()),
        sa.Column('updated',sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    )


def downgrade():
    op.drop_table('workspaces')