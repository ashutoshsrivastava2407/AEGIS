"""AEGIS Enterprise Command Center, Continuous Learning, and Outcome Attribution Migration.

Revision ID: 0013
Revises: 0012
Create Date: 2026-09-19 02:30:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade():
    # 1. command_center_snapshots
    op.create_table(
        'command_center_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('snapshot_id', sa.String(length=100), nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False),
        sa.Column('health_breakdown_json', sa.JSON(), nullable=False),
        sa.Column('active_incidents_count', sa.Integer(), nullable=False),
        sa.Column('pending_approvals_count', sa.Integer(), nullable=False),
        sa.Column('active_learning_signals_count', sa.Integer(), nullable=False),
        sa.Column('snapshot_timestamp', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('snapshot_id'),
    )
    op.create_index('ix_command_center_snapshots_tenant_id', 'command_center_snapshots', ['tenant_id'])

    # 2. learning_signals
    op.create_table(
        'learning_signals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('signal_id', sa.String(length=100), nullable=False),
        sa.Column('dimension', sa.String(length=50), nullable=False),
        sa.Column('signal_type', sa.String(length=100), nullable=False),
        sa.Column('source_component', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('signal_id'),
    )
    op.create_index('ix_learning_signals_tenant_id', 'learning_signals', ['tenant_id'])
    op.create_index('ix_learning_signals_dimension', 'learning_signals', ['dimension'])

    # 3. improvement_candidates
    op.create_table(
        'improvement_candidates',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.String(length=100), nullable=False),
        sa.Column('target_subsystem', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('proposal_json', sa.JSON(), nullable=False),
        sa.Column('evaluation_result_json', sa.JSON(), nullable=False),
        sa.Column('policy_evaluation_id', sa.String(length=100), nullable=True),
        sa.Column('approval_id', sa.String(length=100), nullable=True),
        sa.Column('promoted_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('candidate_id'),
    )
    op.create_index('ix_improvement_candidates_tenant_id', 'improvement_candidates', ['tenant_id'])
    op.create_index('ix_improvement_candidates_status', 'improvement_candidates', ['status'])

    # 4. outcome_observations
    op.create_table(
        'outcome_observations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('observation_id', sa.String(length=100), nullable=False),
        sa.Column('action_id', sa.String(length=100), nullable=False),
        sa.Column('decision_id', sa.String(length=100), nullable=True),
        sa.Column('methodology', sa.String(length=100), nullable=False),
        sa.Column('pre_period_avg', sa.Float(), nullable=False),
        sa.Column('post_period_avg', sa.Float(), nullable=False),
        sa.Column('did_estimate', sa.Float(), nullable=False),
        sa.Column('p_value', sa.Float(), nullable=False),
        sa.Column('is_statistically_significant', sa.Boolean(), nullable=False),
        sa.Column('diagnostics_json', sa.JSON(), nullable=False),
        sa.Column('observed_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('observation_id'),
    )
    op.create_index('ix_outcome_observations_tenant_id', 'outcome_observations', ['tenant_id'])

    # 5. enterprise_health_snapshots
    op.create_table(
        'enterprise_health_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('snapshot_id', sa.String(length=100), nullable=False),
        sa.Column('overall_status', sa.String(length=50), nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False),
        sa.Column('calculation_version', sa.String(length=50), nullable=False),
        sa.Column('dimensions_json', sa.JSON(), nullable=False),
        sa.Column('underlying_evidence_json', sa.JSON(), nullable=False),
        sa.Column('unavailable_dimensions_json', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('snapshot_id'),
    )
    op.create_index('ix_enterprise_health_snapshots_tenant_id', 'enterprise_health_snapshots', ['tenant_id'])

    # 6. executive_reports
    op.create_table(
        'executive_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('observed_facts_json', sa.JSON(), nullable=False),
        sa.Column('model_predictions_json', sa.JSON(), nullable=False),
        sa.Column('system_recommendations_json', sa.JSON(), nullable=False),
        sa.Column('decisions_executed_json', sa.JSON(), nullable=False),
        sa.Column('attributions_json', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_id'),
    )
    op.create_index('ix_executive_reports_tenant_id', 'executive_reports', ['tenant_id'])

    # 7. scenario_analyses
    op.create_table(
        'scenario_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('scenario_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('baseline_scenario_json', sa.JSON(), nullable=False),
        sa.Column('alternative_scenarios_json', sa.JSON(), nullable=False),
        sa.Column('sensitivity_analysis_json', sa.JSON(), nullable=False),
        sa.Column('recommended_option_id', sa.String(length=100), nullable=True),
        sa.Column('created_at_str', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scenario_id'),
    )
    op.create_index('ix_scenario_analyses_tenant_id', 'scenario_analyses', ['tenant_id'])


def downgrade():
    op.drop_table('scenario_analyses')
    op.drop_table('executive_reports')
    op.drop_table('enterprise_health_snapshots')
    op.drop_table('outcome_observations')
    op.drop_table('improvement_candidates')
    op.drop_table('learning_signals')
    op.drop_table('command_center_snapshots')
