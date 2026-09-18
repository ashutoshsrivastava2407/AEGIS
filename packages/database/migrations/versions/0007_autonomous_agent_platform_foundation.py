"""AEGIS Autonomous Agent Platform Foundation Migration.

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-18 01:25:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    # 1. agents
    op.create_table(
        'agents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role_prompt', sa.Text(), nullable=False),
        sa.Column('risk_profile', sa.String(length=50), nullable=False),
        sa.Column('lifecycle_state', sa.String(length=50), nullable=False),
        sa.Column('current_version_id', sa.String(length=36), nullable=True),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=False)
    op.create_index(op.f('ix_agents_agent_type'), 'agents', ['agent_type'], unique=False)
    op.create_index(op.f('ix_agents_lifecycle_state'), 'agents', ['lifecycle_state'], unique=False)
    op.create_index(op.f('ix_agents_tenant_id'), 'agents', ['tenant_id'], unique=False)

    # 2. agent_versions
    op.create_table(
        'agent_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('role_prompt', sa.Text(), nullable=False),
        sa.Column('system_instructions', sa.Text(), nullable=True),
        sa.Column('tools_configured', sa.JSON(), nullable=False),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_versions_agent_id'), 'agent_versions', ['agent_id'], unique=False)

    # 3. agent_capabilities
    op.create_table(
        'agent_capabilities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=False),
        sa.Column('capability_name', sa.String(length=100), nullable=False),
        sa.Column('capability_category', sa.String(length=50), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('constraints_json', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_capabilities_agent_id'), 'agent_capabilities', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_capabilities_capability_name'), 'agent_capabilities', ['capability_name'], unique=False)

    # 4. agent_tools
    op.create_table(
        'agent_tools',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('risk_tier', sa.String(length=50), nullable=False),
        sa.Column('schema_json', sa.JSON(), nullable=False),
        sa.Column('is_governed', sa.Boolean(), nullable=False),
        sa.Column('rate_limit_per_min', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_tools_tool_name'), 'agent_tools', ['tool_name'], unique=True)
    op.create_index(op.f('ix_agent_tools_category'), 'agent_tools', ['category'], unique=False)

    # 5. agent_tool_permissions
    op.create_table(
        'agent_tool_permissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('tool_id', sa.String(length=36), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=True),
        sa.Column('agent_type', sa.String(length=50), nullable=True),
        sa.Column('permission_level', sa.String(length=50), nullable=False),
        sa.Column('conditions_json', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tool_id'], ['agent_tools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_tool_permissions_tool_id'), 'agent_tool_permissions', ['tool_id'], unique=False)
    op.create_index(op.f('ix_agent_tool_permissions_agent_id'), 'agent_tool_permissions', ['agent_id'], unique=False)

    # 6. agent_plans
    op.create_table(
        'agent_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=True),
        sa.Column('goal_statement', sa.Text(), nullable=False),
        sa.Column('plan_status', sa.String(length=50), nullable=False),
        sa.Column('total_nodes', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('context_snapshot_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_plans_run_id'), 'agent_plans', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_plans_plan_status'), 'agent_plans', ['plan_status'], unique=False)

    # 7. agent_plan_nodes
    op.create_table(
        'agent_plan_nodes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('node_key', sa.String(length=100), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('task_description', sa.Text(), nullable=False),
        sa.Column('dependencies_json', sa.JSON(), nullable=False),
        sa.Column('assigned_agent_type', sa.String(length=50), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('tool_params_json', sa.JSON(), nullable=False),
        sa.Column('node_status', sa.String(length=50), nullable=False),
        sa.Column('result_json', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['agent_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_plan_nodes_plan_id'), 'agent_plan_nodes', ['plan_id'], unique=False)
    op.create_index(op.f('ix_agent_plan_nodes_node_key'), 'agent_plan_nodes', ['node_key'], unique=False)

    # 8. agent_steps
    op.create_table(
        'agent_steps',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('thought_process', sa.Text(), nullable=True),
        sa.Column('input_payload_json', sa.JSON(), nullable=False),
        sa.Column('output_payload_json', sa.JSON(), nullable=False),
        sa.Column('step_status', sa.String(length=50), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['run_id'], ['agent_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_steps_run_id'), 'agent_steps', ['run_id'], unique=False)

    # 9. agent_tool_executions
    op.create_table(
        'agent_tool_executions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('step_id', sa.String(length=36), nullable=True),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('input_arguments_json', sa.JSON(), nullable=False),
        sa.Column('output_result_json', sa.JSON(), nullable=False),
        sa.Column('execution_status', sa.String(length=50), nullable=False),
        sa.Column('risk_tier', sa.String(length=50), nullable=False),
        sa.Column('is_authorized', sa.Boolean(), nullable=False),
        sa.Column('authorization_reason', sa.String(length=255), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_tool_executions_run_id'), 'agent_tool_executions', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_tool_executions_tool_name'), 'agent_tool_executions', ['tool_name'], unique=False)

    # 10. agent_policy_decisions
    op.create_table(
        'agent_policy_decisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('policy_name', sa.String(length=100), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('evaluated_context_json', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_policy_decisions_run_id'), 'agent_policy_decisions', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_policy_decisions_policy_name'), 'agent_policy_decisions', ['policy_name'], unique=False)

    # 11. agent_trace_events
    op.create_table(
        'agent_trace_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_trace_events_run_id'), 'agent_trace_events', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_trace_events_event_type'), 'agent_trace_events', ['event_type'], unique=False)

    # 12. agent_approvals
    op.create_table(
        'agent_approvals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=True),
        sa.Column('node_key', sa.String(length=100), nullable=True),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('requested_action', sa.Text(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('approval_status', sa.String(length=50), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_approvals_run_id'), 'agent_approvals', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_approvals_risk_level'), 'agent_approvals', ['risk_level'], unique=False)
    op.create_index(op.f('ix_agent_approvals_approval_status'), 'agent_approvals', ['approval_status'], unique=False)

    # 13. agent_memories
    op.create_table(
        'agent_memories',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=True),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('memory_type', sa.String(length=50), nullable=False),
        sa.Column('memory_key', sa.String(length=100), nullable=False),
        sa.Column('content_json', sa.JSON(), nullable=False),
        sa.Column('importance_score', sa.Float(), nullable=False),
        sa.Column('tags_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_memories_agent_id'), 'agent_memories', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_memories_run_id'), 'agent_memories', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_memories_memory_type'), 'agent_memories', ['memory_type'], unique=False)
    op.create_index(op.f('ix_agent_memories_memory_key'), 'agent_memories', ['memory_key'], unique=False)

    # 14. agent_evaluations
    op.create_table(
        'agent_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('goal_completion_score', sa.Float(), nullable=False),
        sa.Column('tool_accuracy_score', sa.Float(), nullable=False),
        sa.Column('reasoning_quality_score', sa.Float(), nullable=False),
        sa.Column('safety_compliance_score', sa.Float(), nullable=False),
        sa.Column('total_cost_usd', sa.Float(), nullable=False),
        sa.Column('total_latency_ms', sa.Float(), nullable=False),
        sa.Column('evaluation_summary_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_evaluations_run_id'), 'agent_evaluations', ['run_id'], unique=False)
    op.create_index(op.f('ix_agent_evaluations_agent_type'), 'agent_evaluations', ['agent_type'], unique=False)


def downgrade():
    op.drop_table('agent_evaluations')
    op.drop_table('agent_memories')
    op.drop_table('agent_approvals')
    op.drop_table('agent_trace_events')
    op.drop_table('agent_policy_decisions')
    op.drop_table('agent_tool_executions')
    op.drop_table('agent_steps')
    op.drop_table('agent_plan_nodes')
    op.drop_table('agent_plans')
    op.drop_table('agent_tool_permissions')
    op.drop_table('agent_tools')
    op.drop_table('agent_capabilities')
    op.drop_table('agent_versions')
    op.drop_table('agents')
