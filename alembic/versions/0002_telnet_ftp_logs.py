"""telnet/ftp logs

Revision ID: 0002_telnet_ftp_logs
Revises: 0001_initial
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_telnet_ftp_logs'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'telnet_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('source_ip', sa.String, nullable=True),
        sa.Column('source_port', sa.Integer, nullable=True),
        sa.Column('dest_ip', sa.String, nullable=True),
        sa.Column('dest_port', sa.Integer, nullable=True),
        sa.Column('command', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'ftp_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('source_ip', sa.String, nullable=True),
        sa.Column('source_port', sa.Integer, nullable=True),
        sa.Column('event', sa.String, nullable=True),
        sa.Column('username', sa.String, nullable=True),
        sa.Column('filename', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('ftp_logs')
    op.drop_table('telnet_logs')
