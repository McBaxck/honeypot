"""blocked ips

Revision ID: 0003_blocked_ips
Revises: 0002_telnet_ftp_logs
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_blocked_ips'
down_revision = '0002_telnet_ftp_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'blocked_ips',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ip', sa.String, nullable=False, unique=True),
        sa.Column('reason', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('blocked_ips')
