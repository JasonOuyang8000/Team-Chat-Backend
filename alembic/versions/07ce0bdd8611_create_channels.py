"""create channels

Revision ID: 07ce0bdd8611
Revises: a9710257709c
Create Date: 2021-05-21 07:51:05.828887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07ce0bdd8611'
down_revision = 'a9710257709c'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'channels',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, ),
        sa.Column('workspaceId',sa.Integer),
        sa.Column('created',sa.DateTime,  server_default=sa.func.now()),
        sa.Column('updated',sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    )


def downgrade():
    op.drop_table('channels')