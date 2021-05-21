"""channel_messages

Revision ID: 2dedbe776dc4
Revises: 07ce0bdd8611
Create Date: 2021-05-21 08:04:24.456483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2dedbe776dc4'
down_revision = '07ce0bdd8611'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'channel_messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('text', sa.String, nullable=False),
        sa.Column('channelId',sa.Integer),
        sa.Column('userId',sa.Integer),
        sa.Column('created',sa.DateTime,  server_default=sa.func.now()),
        sa.Column('updated',sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    )


def downgrade():
    op.drop_table('channel_messages')