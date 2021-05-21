"""channel alerts

Revision ID: f74ce0f45888
Revises: 2dedbe776dc4
Create Date: 2021-05-21 08:25:41.298304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f74ce0f45888'
down_revision = '2dedbe776dc4'
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
            'channel_alerts',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('read', sa.Boolean, nullable=False ),
            sa.Column('userId',sa.Integer),
            sa.Column('channelId',sa.Integer),
            sa.Column('created',sa.DateTime,  server_default=sa.func.now()),
            sa.Column('updated',sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
        )


def downgrade():
    op.drop_table('channel_alerts')