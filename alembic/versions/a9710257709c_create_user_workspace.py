"""create-user_workspace

Revision ID: a9710257709c
Revises: 4803697bb40a
Create Date: 2021-05-21 00:17:21.803668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9710257709c'
down_revision = '4803697bb40a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user_workspaces',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('userId', sa.Integer),
        sa.Column('workspaceId', sa.Integer),
        sa.Column('created',sa.DateTime,  server_default=sa.func.now()),
        sa.Column('updated',sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    )


def downgrade():
    op.drop_table('user_workspaces')