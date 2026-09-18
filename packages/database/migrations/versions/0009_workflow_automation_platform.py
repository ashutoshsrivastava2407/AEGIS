"""AEGIS Action & Workflow Automation Platform Foundation Migration.

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-18 12:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    # 1. workflows
    op.create_table(
        'workflows',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('business_domain', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('risk_profile', sa.String(length=50), nullable=False),
        sa.Column('timeout_policy_json', sa.JSON(), nullable=False),
        sa.Column('retry_policy_json', sa.JSON(), nullable=False),
        sa.Column('compensation_policy_json', sa.JSON(), nullable=False),
        sa.Column('active_version_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflows_tenant_id', 'workflows', ['tenant_id'])
    op.create_index('ix_workflows_name', 'workflows', ['name'])
    op.create_index('ix_workflows_business_domain', 'workflows', ['business_domain'])
    op.create_index('ix_workflows_owner', 'workflows', ['owner'])
    op.create_index('ix_workflows_status', 'workflows', ['status'])

    # 2. workflow_versions
    op.create_table(
        'workflow_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('definition_fingerprint', sa.String(length=64), nullable=False),
        sa.Column('graph_json', sa.JSON(), nullable=False),
        sa.Column('node_contracts_json', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_frozen', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_versions_workflow_id', 'workflow_versions', ['workflow_id'])
    op.create_index('ix_workflow_versions_version_number', 'workflow_versions', ['version_number'])
    op.create_index('ix_workflow_versions_definition_fingerprint', 'workflow_versions', ['definition_fingerprint'])

    # 3. workflow_nodes
    op.create_table(
        'workflow_nodes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('workflow_version_id', sa.String(length=36), nullable=False),
        sa.Column('node_key', sa.String(length=100), nullable=False),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('action_contract_id', sa.String(length=100), nullable=True),
        sa.Column('action_contract_version', sa.String(length=20), nullable=True),
        sa.Column('inputs_schema_json', sa.JSON(), nullable=False),
        sa.Column('outputs_schema_json', sa.JSON(), nullable=False),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('retry_policy_json', sa.JSON(), nullable=False),
        sa.Column('compensation_node_key', sa.String(length=100), nullable=True),
        sa.Column('risk_metadata_json', sa.JSON(), nullable=False),
        sa.Column('data_classification', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_nodes_workflow_id', 'workflow_nodes', ['workflow_id'])
    op.create_index('ix_workflow_nodes_workflow_version_id', 'workflow_nodes', ['workflow_version_id'])
    op.create_index('ix_workflow_nodes_node_key', 'workflow_nodes', ['node_key'])
    op.create_index('ix_workflow_nodes_node_type', 'workflow_nodes', ['node_type'])

    # 4. workflow_edges
    op.create_table(
        'workflow_edges',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('workflow_version_id', sa.String(length=36), nullable=False),
        sa.Column('source_node_key', sa.String(length=100), nullable=False),
        sa.Column('target_node_key', sa.String(length=100), nullable=False),
        sa.Column('condition_expression', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_edges_workflow_id', 'workflow_edges', ['workflow_id'])
    op.create_index('ix_workflow_edges_workflow_version_id', 'workflow_edges', ['workflow_version_id'])
    op.create_index('ix_workflow_edges_source_node_key', 'workflow_edges', ['source_node_key'])
    op.create_index('ix_workflow_edges_target_node_key', 'workflow_edges', ['target_node_key'])

    # 5. workflow_triggers
    op.create_table(
        'workflow_triggers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('event_topic', sa.String(length=100), nullable=True),
        sa.Column('deduplication_key', sa.String(length=100), nullable=True),
        sa.Column('trigger_config_json', sa.JSON(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_triggers_tenant_id', 'workflow_triggers', ['tenant_id'])
    op.create_index('ix_workflow_triggers_workflow_id', 'workflow_triggers', ['workflow_id'])
    op.create_index('ix_workflow_triggers_trigger_type', 'workflow_triggers', ['trigger_type'])
    op.create_index('ix_workflow_triggers_event_topic', 'workflow_triggers', ['event_topic'])
    op.create_index('ix_workflow_triggers_deduplication_key', 'workflow_triggers', ['deduplication_key'])

    # 6. workflow_schedules
    op.create_table(
        'workflow_schedules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('schedule_cron', sa.String(length=100), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('dst_behavior', sa.String(length=50), nullable=False),
        sa.Column('misfire_policy', sa.String(length=50), nullable=False),
        sa.Column('catch_up_policy', sa.String(length=50), nullable=False),
        sa.Column('overlap_policy', sa.String(length=50), nullable=False),
        sa.Column('max_concurrent_runs', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('last_run_at', sa.String(length=50), nullable=True),
        sa.Column('next_run_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_schedules_tenant_id', 'workflow_schedules', ['tenant_id'])
    op.create_index('ix_workflow_schedules_workflow_id', 'workflow_schedules', ['workflow_id'])

    # 7. workflow_event_inbox
    op.create_table(
        'workflow_event_inbox',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.String(length=100), nullable=False),
        sa.Column('deduplication_key', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('payload_hash', sa.String(length=64), nullable=False),
        sa.Column('processed_at', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_event_inbox_event_id', 'workflow_event_inbox', ['event_id'], unique=True)
    op.create_index('ix_workflow_event_inbox_deduplication_key', 'workflow_event_inbox', ['deduplication_key'])

    # 8. workflow_runs
    op.create_table(
        'workflow_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.String(length=36), nullable=False),
        sa.Column('workflow_version_id', sa.String(length=36), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('trigger_payload_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_step_key', sa.String(length=100), nullable=True),
        sa.Column('workflow_manifest_hash', sa.String(length=64), nullable=True),
        sa.Column('worker_id', sa.String(length=100), nullable=True),
        sa.Column('lease_id', sa.String(length=100), nullable=True),
        sa.Column('lease_expires_at', sa.String(length=50), nullable=True),
        sa.Column('fencing_token', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.String(length=50), nullable=True),
        sa.Column('completed_at', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('compensation_status', sa.String(length=50), nullable=True),
        sa.Column('cost_cents', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_runs_tenant_id', 'workflow_runs', ['tenant_id'])
    op.create_index('ix_workflow_runs_workflow_id', 'workflow_runs', ['workflow_id'])
    op.create_index('ix_workflow_runs_workflow_version_id', 'workflow_runs', ['workflow_version_id'])
    op.create_index('ix_workflow_runs_status', 'workflow_runs', ['status'])

    # 9. workflow_node_runs
    op.create_table(
        'workflow_node_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('workflow_run_id', sa.String(length=36), nullable=False),
        sa.Column('node_key', sa.String(length=100), nullable=False),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('inputs_json', sa.JSON(), nullable=False),
        sa.Column('outputs_json', sa.JSON(), nullable=False),
        sa.Column('error_json', sa.JSON(), nullable=False),
        sa.Column('started_at', sa.String(length=50), nullable=True),
        sa.Column('completed_at', sa.String(length=50), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('worker_id', sa.String(length=100), nullable=True),
        sa.Column('fencing_token', sa.Integer(), nullable=False),
        sa.Column('action_contract_id', sa.String(length=100), nullable=True),
        sa.Column('governed_execution_id', sa.String(length=100), nullable=True),
        sa.Column('postcondition_verified', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_node_runs_workflow_run_id', 'workflow_node_runs', ['workflow_run_id'])
    op.create_index('ix_workflow_node_runs_node_key', 'workflow_node_runs', ['node_key'])
    op.create_index('ix_workflow_node_runs_status', 'workflow_node_runs', ['status'])

    # 10. workflow_human_tasks
    op.create_table(
        'workflow_human_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('workflow_run_id', sa.String(length=36), nullable=False),
        sa.Column('node_run_id', sa.String(length=36), nullable=False),
        sa.Column('task_key', sa.String(length=100), nullable=False),
        sa.Column('assignee', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('form_schema_json', sa.JSON(), nullable=False),
        sa.Column('submitted_data_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.String(length=50), nullable=True),
        sa.Column('escalated_to', sa.String(length=100), nullable=True),
        sa.Column('completed_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_human_tasks_tenant_id', 'workflow_human_tasks', ['tenant_id'])
    op.create_index('ix_workflow_human_tasks_workflow_run_id', 'workflow_human_tasks', ['workflow_run_id'])
    op.create_index('ix_workflow_human_tasks_node_run_id', 'workflow_human_tasks', ['node_run_id'])
    op.create_index('ix_workflow_human_tasks_task_key', 'workflow_human_tasks', ['task_key'])
    op.create_index('ix_workflow_human_tasks_assignee', 'workflow_human_tasks', ['assignee'])
    op.create_index('ix_workflow_human_tasks_status', 'workflow_human_tasks', ['status'])

    # 11. workflow_connectors
    op.create_table(
        'workflow_connectors',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('connector_type', sa.String(length=50), nullable=False),
        sa.Column('auth_type', sa.String(length=50), nullable=False),
        sa.Column('non_secret_config_json', sa.JSON(), nullable=False),
        sa.Column('secret_refs_json', sa.JSON(), nullable=False),
        sa.Column('egress_allowlist_json', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_connectors_tenant_id', 'workflow_connectors', ['tenant_id'])
    op.create_index('ix_workflow_connectors_name', 'workflow_connectors', ['name'])
    op.create_index('ix_workflow_connectors_connector_type', 'workflow_connectors', ['connector_type'])

    # 12. workflow_trace_events
    op.create_table(
        'workflow_trace_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('workflow_run_id', sa.String(length=36), nullable=False),
        sa.Column('node_run_id', sa.String(length=36), nullable=True),
        sa.Column('trace_id', sa.String(length=100), nullable=False),
        sa.Column('span_id', sa.String(length=100), nullable=False),
        sa.Column('parent_span_id', sa.String(length=100), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('details_json', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_trace_events_workflow_run_id', 'workflow_trace_events', ['workflow_run_id'])
    op.create_index('ix_workflow_trace_events_node_run_id', 'workflow_trace_events', ['node_run_id'])
    op.create_index('ix_workflow_trace_events_trace_id', 'workflow_trace_events', ['trace_id'])
    op.create_index('ix_workflow_trace_events_span_id', 'workflow_trace_events', ['span_id'])
    op.create_index('ix_workflow_trace_events_event_type', 'workflow_trace_events', ['event_type'])

    # 13. workflow_outbox
    op.create_table(
        'workflow_outbox',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_outbox_tenant_id', 'workflow_outbox', ['tenant_id'])
    op.create_index('ix_workflow_outbox_topic', 'workflow_outbox', ['topic'])
    op.create_index('ix_workflow_outbox_event_type', 'workflow_outbox', ['event_type'])
    op.create_index('ix_workflow_outbox_status', 'workflow_outbox', ['status'])


def downgrade():
    op.drop_table('workflow_outbox')
    op.drop_table('workflow_trace_events')
    op.drop_table('workflow_connectors')
    op.drop_table('workflow_human_tasks')
    op.drop_table('workflow_node_runs')
    op.drop_table('workflow_runs')
    op.drop_table('workflow_event_inbox')
    op.drop_table('workflow_schedules')
    op.drop_table('workflow_triggers')
    op.drop_table('workflow_edges')
    op.drop_table('workflow_nodes')
    op.drop_table('workflow_versions')
    op.drop_table('workflows')
