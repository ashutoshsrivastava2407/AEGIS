"""AEGIS Agent Memory and LangGraph Orchestration Migration.

Revision ID: 0015
Revises: 0014
Create Date: 2026-09-27 14:25:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade():
    # 1. agent_memory_events
    op.create_table(
        'agent_memory_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('memory_id', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('trace_id', sa.String(length=64), nullable=True),
        sa.Column('event_payload', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_memory_events_event_id'), 'agent_memory_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_agent_memory_events_memory_id'), 'agent_memory_events', ['memory_id'], unique=False)
    op.create_index(op.f('ix_agent_memory_events_tenant_id'), 'agent_memory_events', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_agent_memory_events_action_type'), 'agent_memory_events', ['action_type'], unique=False)

    # 2. agent_memory_namespaces
    op.create_table(
        'agent_memory_namespaces',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('namespace_id', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('workspace_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('default_retention_policy', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_memory_namespaces_namespace_id'), 'agent_memory_namespaces', ['namespace_id'], unique=True)
    op.create_index(op.f('ix_agent_memory_namespaces_tenant_id'), 'agent_memory_namespaces', ['tenant_id'], unique=False)

    # 3. agent_memory_retrievals
    op.create_table(
        'agent_memory_retrievals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('retrieval_id', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('agent_run_id', sa.String(length=64), nullable=False),
        sa.Column('query', sa.String(length=1000), nullable=False),
        sa.Column('retrieved_memory_ids', sa.JSON(), nullable=False),
        sa.Column('relevance_scores', sa.JSON(), nullable=False),
        sa.Column('compilation_budget_used', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_memory_retrievals_retrieval_id'), 'agent_memory_retrievals', ['retrieval_id'], unique=True)
    op.create_index(op.f('ix_agent_memory_retrievals_tenant_id'), 'agent_memory_retrievals', ['tenant_id'], unique=False)

    # 4. agent_graph_checkpoints
    op.create_table(
        'agent_graph_checkpoints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('checkpoint_id', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('thread_id', sa.String(length=64), nullable=False),
        sa.Column('agent_run_id', sa.String(length=64), nullable=False),
        sa.Column('graph_id', sa.String(length=100), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('node_name', sa.String(length=100), nullable=False),
        sa.Column('checkpoint_payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_graph_checkpoints_checkpoint_id'), 'agent_graph_checkpoints', ['checkpoint_id'], unique=True)
    op.create_index(op.f('ix_agent_graph_checkpoints_tenant_id'), 'agent_graph_checkpoints', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_agent_graph_checkpoints_thread_id'), 'agent_graph_checkpoints', ['thread_id'], unique=False)
    op.create_index(op.f('ix_agent_graph_checkpoints_agent_run_id'), 'agent_graph_checkpoints', ['agent_run_id'], unique=False)


def downgrade():
    op.drop_table('agent_graph_checkpoints')
    op.drop_table('agent_memory_retrievals')
    op.drop_table('agent_memory_namespaces')
    op.drop_table('agent_memory_events')
