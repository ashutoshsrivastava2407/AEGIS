"""AEGIS Governed Tool Calling System Migration.

Revision ID: 0014
Revises: 0013
Create Date: 2026-09-27 13:17:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add fields to agent_tools
    op.add_column('agent_tools', sa.Column('input_schema', sa.JSON(), nullable=True))
    op.add_column('agent_tools', sa.Column('output_schema', sa.JSON(), nullable=True))
    op.add_column('agent_tools', sa.Column('error_schema', sa.JSON(), nullable=True))
    op.add_column('agent_tools', sa.Column('version', sa.String(length=20), nullable=True))
    op.add_column('agent_tools', sa.Column('enabled', sa.Boolean(), nullable=True))

    # 2. durable_tool_calls
    op.create_table(
        'durable_tool_calls',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('call_id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('agent_run_id', sa.String(length=36), nullable=True),
        sa.Column('correlation_id', sa.String(length=64), nullable=True),
        sa.Column('trace_id', sa.String(length=64), nullable=True),
        sa.Column('tool_id', sa.String(length=100), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('tool_version', sa.String(length=20), nullable=False),
        sa.Column('arguments_hash', sa.String(length=64), nullable=True),
        sa.Column('sanitized_arguments', sa.JSON(), nullable=False),
        sa.Column('validation_status', sa.String(length=50), nullable=False),
        sa.Column('authorization_result', sa.JSON(), nullable=False),
        sa.Column('policy_result', sa.JSON(), nullable=False),
        sa.Column('risk_tier', sa.String(length=50), nullable=False),
        sa.Column('approval_status', sa.String(length=50), nullable=False),
        sa.Column('execution_status', sa.String(length=50), nullable=False),
        sa.Column('result_metadata', sa.JSON(), nullable=False),
        sa.Column('result_schema_valid', sa.Boolean(), nullable=False),
        sa.Column('error_information', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=False),
        sa.Column('token_cost', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_durable_tool_calls_call_id'), 'durable_tool_calls', ['call_id'], unique=True)
    op.create_index(op.f('ix_durable_tool_calls_tenant_id'), 'durable_tool_calls', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_durable_tool_calls_agent_run_id'), 'durable_tool_calls', ['agent_run_id'], unique=False)
    op.create_index(op.f('ix_durable_tool_calls_correlation_id'), 'durable_tool_calls', ['correlation_id'], unique=False)
    op.create_index(op.f('ix_durable_tool_calls_trace_id'), 'durable_tool_calls', ['trace_id'], unique=False)
    op.create_index(op.f('ix_durable_tool_calls_tool_id'), 'durable_tool_calls', ['tool_id'], unique=False)
    op.create_index(op.f('ix_durable_tool_calls_tool_name'), 'durable_tool_calls', ['tool_name'], unique=False)

    # 3. tool_call_events
    op.create_table(
        'tool_call_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('call_id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tool_call_events_call_id'), 'tool_call_events', ['call_id'], unique=False)
    op.create_index(op.f('ix_tool_call_events_tenant_id'), 'tool_call_events', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_tool_call_events_event_type'), 'tool_call_events', ['event_type'], unique=False)


def downgrade():
    op.drop_table('tool_call_events')
    op.drop_table('durable_tool_calls')
    op.drop_column('agent_tools', 'enabled')
    op.drop_column('agent_tools', 'version')
    op.drop_column('agent_tools', 'error_schema')
    op.drop_column('agent_tools', 'output_schema')
    op.drop_column('agent_tools', 'input_schema')
