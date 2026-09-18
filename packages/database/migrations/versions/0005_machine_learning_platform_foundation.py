"""AEGIS Machine Learning Platform Foundation Migration.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-18 00:38:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # 1. ml_feature_definitions
    op.create_table(
        'ml_feature_definitions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('entity_key', sa.String(length=100), nullable=False),
        sa.Column('transformation_definition', sa.Text(), nullable=False),
        sa.Column('source_dataset_id', sa.String(), nullable=True),
        sa.Column('source_columns_json', sa.JSON(), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_feature_definitions_name'), 'ml_feature_definitions', ['name'], unique=False)
    op.create_index(op.f('ix_ml_feature_definitions_tenant_id'), 'ml_feature_definitions', ['tenant_id'], unique=False)

    # 2. ml_feature_sets
    op.create_table(
        'ml_feature_sets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('feature_ids_json', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('source_dataset_versions_json', sa.JSON(), nullable=False),
        sa.Column('purpose', sa.String(length=100), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_feature_sets_name'), 'ml_feature_sets', ['name'], unique=False)
    op.create_index(op.f('ix_ml_feature_sets_tenant_id'), 'ml_feature_sets', ['tenant_id'], unique=False)

    # 3. ml_feature_snapshots
    op.create_table(
        'ml_feature_snapshots',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('feature_set_id', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('feature_values_json', sa.JSON(), nullable=False),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('feature_version', sa.Integer(), nullable=False),
        sa.Column('source_version', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_feature_snapshots_tenant_id'), 'ml_feature_snapshots', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_ml_feature_snapshots_feature_set_id'), 'ml_feature_snapshots', ['feature_set_id'], unique=False)

    # 4. ml_experiments
    op.create_table(
        'ml_experiments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('objective', sa.String(length=255), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. ml_experiment_runs
    op.create_table(
        'ml_experiment_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('experiment_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('dataset_version', sa.String(length=50), nullable=False),
        sa.Column('feature_set_version', sa.Integer(), nullable=False),
        sa.Column('algorithm', sa.String(length=100), nullable=False),
        sa.Column('hyperparameters_json', sa.JSON(), nullable=False),
        sa.Column('parameters_json', sa.JSON(), nullable=False),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('artifacts_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('training_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('training_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. ml_training_jobs
    op.create_table(
        'ml_training_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('experiment_id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('dataset_id', sa.String(), nullable=True),
        sa.Column('feature_set_id', sa.String(), nullable=True),
        sa.Column('algorithm', sa.String(length=100), nullable=False),
        sa.Column('configuration_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resource_metadata_json', sa.JSON(), nullable=False),
        sa.Column('error_info', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. ml_models
    op.create_table(
        'ml_models',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. ml_model_versions
    op.create_table(
        'ml_model_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('experiment_run_id', sa.String(), nullable=False),
        sa.Column('dataset_version', sa.String(length=50), nullable=False),
        sa.Column('feature_set_version', sa.Integer(), nullable=False),
        sa.Column('algorithm', sa.String(length=100), nullable=False),
        sa.Column('hyperparameters_json', sa.JSON(), nullable=False),
        sa.Column('artifact_reference_json', sa.JSON(), nullable=False),
        sa.Column('evaluation_summary_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. ml_evaluations
    op.create_table(
        'ml_evaluations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('model_version', sa.Integer(), nullable=False),
        sa.Column('dataset_version', sa.String(length=50), nullable=False),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('evaluation_config_json', sa.JSON(), nullable=False),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. ml_deployments
    op.create_table(
        'ml_deployments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('model_version_id', sa.String(), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False),
        sa.Column('deployment_status', sa.String(length=20), nullable=False),
        sa.Column('endpoint_reference', sa.String(length=255), nullable=False),
        sa.Column('replica_config_json', sa.JSON(), nullable=False),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retired_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. ml_inference_logs
    op.create_table(
        'ml_inference_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('model_version_id', sa.String(), nullable=False),
        sa.Column('feature_set_id', sa.String(), nullable=True),
        sa.Column('inference_type', sa.String(length=20), nullable=False),
        sa.Column('input_payload_json', sa.JSON(), nullable=False),
        sa.Column('prediction_result_json', sa.JSON(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. ml_drift_records
    op.create_table(
        'ml_drift_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('reference_period', sa.String(length=100), nullable=False),
        sa.Column('current_period', sa.String(length=100), nullable=False),
        sa.Column('method', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('evidence_json', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('ml_drift_records')
    op.drop_table('ml_inference_logs')
    op.drop_table('ml_deployments')
    op.drop_table('ml_evaluations')
    op.drop_table('ml_model_versions')
    op.drop_table('ml_models')
    op.drop_table('ml_training_jobs')
    op.drop_table('ml_experiment_runs')
    op.drop_table('ml_experiments')
    op.drop_table('ml_feature_snapshots')
    op.drop_table('ml_feature_sets')
    op.drop_table('ml_feature_definitions')
