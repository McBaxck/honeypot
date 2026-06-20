"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'accounts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=True),
        sa.Column('name', sa.String, nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('type', sa.String, nullable=True),
        sa.Column('source_ip', sa.String, nullable=True),
        sa.Column('source_port', sa.Integer, nullable=True),
        sa.Column('data', sa.Text, nullable=True),
        sa.Column('dest_port', sa.Integer, nullable=True),
        sa.Column('dest_ip', sa.String, nullable=True),
        sa.Column('protocol', sa.String, nullable=True),
        sa.Column('country', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'ssh_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('source_ip', sa.String, nullable=True),
        sa.Column('source_port', sa.Integer, nullable=True),
        sa.Column('dest_ip', sa.String, nullable=True),
        sa.Column('dest_port', sa.Integer, nullable=True),
        sa.Column('command', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'http_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('source_ip', sa.String, nullable=True),
        sa.Column('source_port', sa.Integer, nullable=True),
        sa.Column('dest_ip', sa.String, nullable=True),
        sa.Column('dest_port', sa.Integer, nullable=True),
        sa.Column('user_agent', sa.String, nullable=True),
        sa.Column('url', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'modules_conf',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('module', sa.String, nullable=True),
        sa.Column('conf', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'state',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('honeypot_id', sa.String, nullable=True),
        sa.Column('ip', sa.String, nullable=True),
        sa.Column('run', sa.Boolean, nullable=True),
        sa.Column('extra', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_state_honeypot_id', 'state', ['honeypot_id'])

    op.create_table(
        'network_conf',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('honeypot_id', sa.String, nullable=False),
        sa.Column('conf', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_network_conf_honeypot_id', 'network_conf', ['honeypot_id'])


def downgrade() -> None:
    op.drop_table('network_conf')
    op.drop_table('state')
    op.drop_table('modules_conf')
    op.drop_table('http_logs')
    op.drop_table('ssh_logs')
    op.drop_table('logs')
    op.drop_table('accounts')
