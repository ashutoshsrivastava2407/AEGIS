"""AEGIS Decision Intelligence & Autonomous Decision Engine Foundation Migration.

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-18 08:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Remediate agent_steps (Chain-of-thought storage remediation)
    op.add_column('agent_steps', sa.Column('rationale_summary', sa.Text(), nullable=True))
    op.add_column('agent_steps', sa.Column('decision_factors_json', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('agent_steps', sa.Column('evidence_references_json', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('agent_steps', sa.Column('tool_results_json', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('agent_steps', sa.Column('verification_results_json', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('agent_steps', sa.Column('policy_results_json', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('agent_steps', sa.Column('assumptions_json', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('agent_steps', sa.Column('constraints_json', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('agent_steps', sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'))
    op.add_column('agent_steps', sa.Column('action_summary', sa.Text(), nullable=True))
    op.add_column('agent_steps', sa.Column('outcome_summary', sa.Text(), nullable=True))

    # 2. Add alignment metrics to agent_evaluations
    op.add_column('agent_evaluations', sa.Column('rationale_evidence_alignment', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('agent_evaluations', sa.Column('evidence_support_score', sa.Float(), nullable=False, server_default='0.0'))

    # 3. Create decisions
    op.create_table(
        'decisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('requester', sa.String(length=100), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('decision_type', sa.String(length=50), nullable=False),
        sa.Column('business_domain', sa.String(length=50), nullable=False),
        sa.Column('decision_status', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('risk_tier', sa.String(length=50), nullable=False),
        sa.Column('due_at', sa.String(length=50), nullable=True),
        sa.Column('affected_resources_json', sa.JSON(), nullable=False),
        sa.Column('approval_required', sa.Boolean(), nullable=False),
        sa.Column('execution_required', sa.Boolean(), nullable=False),
        sa.Column('integrity_status', sa.String(length=50), nullable=False),
        sa.Column('integrity_rationale', sa.Text(), nullable=True),
        sa.Column('eligibility_status', sa.String(length=50), nullable=False),
        sa.Column('eligibility_rationale', sa.Text(), nullable=True),
        sa.Column('active_version_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decisions_tenant_id'), 'decisions', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_decisions_owner'), 'decisions', ['owner'], unique=False)
    op.create_index(op.f('ix_decisions_decision_type'), 'decisions', ['decision_type'], unique=False)
    op.create_index(op.f('ix_decisions_business_domain'), 'decisions', ['business_domain'], unique=False)
    op.create_index(op.f('ix_decisions_decision_status'), 'decisions', ['decision_status'], unique=False)

    # 4. Create decision_versions
    op.create_table(
        'decision_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('manifest_version', sa.String(length=20), nullable=False),
        sa.Column('schema_version', sa.String(length=20), nullable=False),
        sa.Column('manifest_hash', sa.String(length=64), nullable=False),
        sa.Column('context_fingerprint', sa.String(length=64), nullable=False),
        sa.Column('manifest_json', sa.JSON(), nullable=False),
        sa.Column('is_frozen', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decision_versions_decision_id'), 'decision_versions', ['decision_id'], unique=False)
    op.create_index(op.f('ix_decision_versions_version_number'), 'decision_versions', ['version_number'], unique=False)
    op.create_index(op.f('ix_decision_versions_manifest_hash'), 'decision_versions', ['manifest_hash'], unique=False)
    op.create_index(op.f('ix_decision_versions_context_fingerprint'), 'decision_versions', ['context_fingerprint'], unique=False)

    # 5. Create decision_contexts
    op.create_table(
        'decision_contexts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('context_fingerprint', sa.String(length=64), nullable=False),
        sa.Column('datasets_json', sa.JSON(), nullable=False),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('anomalies_json', sa.JSON(), nullable=False),
        sa.Column('models_json', sa.JSON(), nullable=False),
        sa.Column('documents_json', sa.JSON(), nullable=False),
        sa.Column('policies_json', sa.JSON(), nullable=False),
        sa.Column('agent_runs_json', sa.JSON(), nullable=False),
        sa.Column('scenarios_json', sa.JSON(), nullable=False),
        sa.Column('constraints_json', sa.JSON(), nullable=False),
        sa.Column('data_freshness_seconds', sa.Float(), nullable=False),
        sa.Column('data_quality_score', sa.Float(), nullable=False),
        sa.Column('is_stale', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decision_contexts_decision_id'), 'decision_contexts', ['decision_id'], unique=False)
    op.create_index(op.f('ix_decision_contexts_context_fingerprint'), 'decision_contexts', ['context_fingerprint'], unique=False)

    # 6. Create decision_evidences
    op.create_table(
        'decision_evidences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('evidence_summary', sa.Text(), nullable=False),
        sa.Column('source_ref', sa.String(length=255), nullable=False),
        sa.Column('source_authority', sa.String(length=50), nullable=False),
        sa.Column('freshness_timestamp', sa.String(length=50), nullable=False),
        sa.Column('is_fresh', sa.Boolean(), nullable=False),
        sa.Column('confidence_weight', sa.Float(), nullable=False),
        sa.Column('is_conflicting', sa.Boolean(), nullable=False),
        sa.Column('conflict_details_json', sa.JSON(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decision_evidences_decision_id'), 'decision_evidences', ['decision_id'], unique=False)
    op.create_index(op.f('ix_decision_evidences_source_type'), 'decision_evidences', ['source_type'], unique=False)

    # 7. Create decision_options
    op.create_table(
        'decision_options',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('option_key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('option_type', sa.String(length=50), nullable=False),
        sa.Column('actions_json', sa.JSON(), nullable=False),
        sa.Column('assumptions_json', sa.JSON(), nullable=False),
        sa.Column('expected_impact_json', sa.JSON(), nullable=False),
        sa.Column('cost_estimate_usd', sa.Float(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('reversibility_score', sa.Float(), nullable=False),
        sa.Column('affected_resources_json', sa.JSON(), nullable=False),
        sa.Column('constraints_satisfied', sa.Boolean(), nullable=False),
        sa.Column('is_feasible', sa.Boolean(), nullable=False),
        sa.Column('is_recommended', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decision_options_decision_id'), 'decision_options', ['decision_id'], unique=False)
    op.create_index(op.f('ix_decision_options_option_key'), 'decision_options', ['option_key'], unique=False)

    # 8. Create decision_criteria, decision_evaluations, decision_constraints
    op.create_table(
        'decision_criteria',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('criterion_key', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('scale', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('time_period', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('normalization_method', sa.String(length=50), nullable=False),
        sa.Column('normalization_version', sa.String(length=20), nullable=False),
        sa.Column('criterion_version', sa.String(length=20), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('option_id', sa.String(length=36), nullable=False),
        sa.Column('mcda_score', sa.Float(), nullable=False),
        sa.Column('expected_value', sa.Float(), nullable=False),
        sa.Column('net_value', sa.Float(), nullable=False),
        sa.Column('risk_adjusted_value', sa.Float(), nullable=False),
        sa.Column('is_pareto_efficient', sa.Boolean(), nullable=False),
        sa.Column('is_dominated', sa.Boolean(), nullable=False),
        sa.Column('sensitivity_score', sa.Float(), nullable=False),
        sa.Column('criterion_breakdown_json', sa.JSON(), nullable=False),
        sa.Column('evaluation_metadata_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_constraints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('constraint_key', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('constraint_type', sa.String(length=50), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=False),
        sa.Column('operator', sa.String(length=20), nullable=False),
        sa.Column('is_satisfied', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Create decision_risk_assessments, decision_uncertainties
    op.create_table(
        'decision_risk_assessments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('option_id', sa.String(length=36), nullable=True),
        sa.Column('methodology_version', sa.String(length=20), nullable=False),
        sa.Column('probability', sa.Float(), nullable=False),
        sa.Column('impact', sa.Float(), nullable=False),
        sa.Column('severity_score', sa.Float(), nullable=False),
        sa.Column('expected_loss_usd', sa.Float(), nullable=False),
        sa.Column('blast_radius', sa.String(length=50), nullable=False),
        sa.Column('reversibility', sa.String(length=50), nullable=False),
        sa.Column('policy_sensitivity', sa.Float(), nullable=False),
        sa.Column('risk_factors_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_uncertainties',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('adapter_name', sa.String(length=100), nullable=False),
        sa.Column('methodology_version', sa.String(length=20), nullable=False),
        sa.Column('uncertainty_type', sa.String(length=50), nullable=False),
        sa.Column('aleatoric_score', sa.Float(), nullable=False),
        sa.Column('epistemic_score', sa.Float(), nullable=False),
        sa.Column('confidence_interval_low', sa.Float(), nullable=False),
        sa.Column('confidence_interval_high', sa.Float(), nullable=False),
        sa.Column('calibration_state', sa.String(length=50), nullable=False),
        sa.Column('assumptions_json', sa.JSON(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Create decision_simulations, decision_scenarios
    op.create_table(
        'decision_simulations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('option_id', sa.String(length=36), nullable=True),
        sa.Column('simulation_type', sa.String(length=50), nullable=False),
        sa.Column('has_valid_stochastic_basis', sa.Boolean(), nullable=False),
        sa.Column('iterations', sa.Integer(), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=False),
        sa.Column('percentile_p10', sa.Float(), nullable=False),
        sa.Column('percentile_p50', sa.Float(), nullable=False),
        sa.Column('percentile_p90', sa.Float(), nullable=False),
        sa.Column('mean_outcome', sa.Float(), nullable=False),
        sa.Column('std_dev', sa.Float(), nullable=False),
        sa.Column('simulation_engine_version', sa.String(length=20), nullable=False),
        sa.Column('results_distribution_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_scenarios',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('scenario_key', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameter_overrides_json', sa.JSON(), nullable=False),
        sa.Column('probability_weight', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. Create decision_policy_evaluations, decision_approvals
    op.create_table(
        'decision_policy_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('policy_name', sa.String(length=100), nullable=False),
        sa.Column('policy_version', sa.String(length=20), nullable=False),
        sa.Column('policy_result', sa.String(length=50), nullable=False),
        sa.Column('evaluated_conditions_json', sa.JSON(), nullable=False),
        sa.Column('matched_rules_json', sa.JSON(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_approvals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('required_role', sa.String(length=50), nullable=False),
        sa.Column('approver_id', sa.String(length=100), nullable=True),
        sa.Column('approval_status', sa.String(length=50), nullable=False),
        sa.Column('approval_rationale', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.String(length=50), nullable=True),
        sa.Column('revalidated_at', sa.String(length=50), nullable=True),
        sa.Column('is_revalidated', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. Create decision_actions, decision_outcomes, decision_feedbacks, decision_trace_events, decision_outbox_events
    op.create_table(
        'decision_actions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=True),
        sa.Column('option_id', sa.String(length=36), nullable=True),
        sa.Column('contract_version', sa.String(length=20), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('target_resource', sa.String(length=255), nullable=False),
        sa.Column('parameters_json', sa.JSON(), nullable=False),
        sa.Column('risk_classification', sa.String(length=50), nullable=False),
        sa.Column('side_effects_json', sa.JSON(), nullable=False),
        sa.Column('reversibility', sa.String(length=50), nullable=False),
        sa.Column('idempotency_key', sa.String(length=100), nullable=False),
        sa.Column('preconditions_json', sa.JSON(), nullable=False),
        sa.Column('postconditions_json', sa.JSON(), nullable=False),
        sa.Column('compensation_method', sa.String(length=100), nullable=True),
        sa.Column('execution_status', sa.String(length=50), nullable=False),
        sa.Column('execution_result_json', sa.JSON(), nullable=False),
        sa.Column('postconditions_verified', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key')
    )

    op.create_table(
        'decision_outcomes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('action_id', sa.String(length=36), nullable=True),
        sa.Column('attribution_classification', sa.String(length=50), nullable=False),
        sa.Column('expected_impact_usd', sa.Float(), nullable=False),
        sa.Column('actual_impact_usd', sa.Float(), nullable=False),
        sa.Column('variance_usd', sa.Float(), nullable=False),
        sa.Column('observed_kpis_json', sa.JSON(), nullable=False),
        sa.Column('attribution_confidence', sa.Float(), nullable=False),
        sa.Column('measurement_window_days', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_feedbacks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('outcome_id', sa.String(length=36), nullable=True),
        sa.Column('proposal_version', sa.String(length=20), nullable=False),
        sa.Column('target_component', sa.String(length=100), nullable=False),
        sa.Column('previous_config_json', sa.JSON(), nullable=False),
        sa.Column('proposed_config_json', sa.JSON(), nullable=False),
        sa.Column('offline_evaluation_json', sa.JSON(), nullable=False),
        sa.Column('shadow_evaluation_json', sa.JSON(), nullable=False),
        sa.Column('governance_status', sa.String(length=50), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('is_rolled_out', sa.Boolean(), nullable=False),
        sa.Column('rollback_target_version', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_trace_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('stage_number', sa.Integer(), nullable=False),
        sa.Column('stage_name', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'decision_outbox_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.Column('dispatch_status', sa.String(length=50), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('decision_outbox_events')
    op.drop_table('decision_trace_events')
    op.drop_table('decision_feedbacks')
    op.drop_table('decision_outcomes')
    op.drop_table('decision_actions')
    op.drop_table('decision_approvals')
    op.drop_table('decision_policy_evaluations')
    op.drop_table('decision_scenarios')
    op.drop_table('decision_simulations')
    op.drop_table('decision_uncertainties')
    op.drop_table('decision_risk_assessments')
    op.drop_table('decision_constraints')
    op.drop_table('decision_evaluations')
    op.drop_table('decision_criteria')
    op.drop_table('decision_options')
    op.drop_table('decision_evidences')
    op.drop_table('decision_contexts')
    op.drop_table('decision_versions')
    op.drop_table('decisions')
    op.drop_column('agent_evaluations', 'evidence_support_score')
    op.drop_column('agent_evaluations', 'rationale_evidence_alignment')
    op.drop_column('agent_steps', 'outcome_summary')
    op.drop_column('agent_steps', 'action_summary')
    op.drop_column('agent_steps', 'confidence')
    op.drop_column('agent_steps', 'constraints_json')
    op.drop_column('agent_steps', 'assumptions_json')
    op.drop_column('agent_steps', 'policy_results_json')
    op.drop_column('agent_steps', 'verification_results_json')
    op.drop_column('agent_steps', 'tool_results_json')
    op.drop_column('agent_steps', 'evidence_references_json')
    op.drop_column('agent_steps', 'decision_factors_json')
    op.drop_column('agent_steps', 'rationale_summary')
