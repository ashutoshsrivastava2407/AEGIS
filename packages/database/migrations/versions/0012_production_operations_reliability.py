"""AEGIS Production Operations, Reliability, and FinOps Foundation Migration.

Revision ID: 0012
Revises: 0011
Create Date: 2026-09-18 22:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    # 1. service_catalog
    op.create_table(
        'service_catalog',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('owner_team', sa.String(length=100), nullable=False),
        sa.Column('tier', sa.String(length=50), nullable=False),
        sa.Column('criticality', sa.String(length=50), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False),
        sa.Column('escalation_policy', sa.String(length=100), nullable=False),
        sa.Column('repo_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_name'),
    )
    op.create_index('ix_service_catalog_tenant_id', 'service_catalog', ['tenant_id'])
    op.create_index('ix_service_catalog_service_name', 'service_catalog', ['service_name'])
    op.create_index('ix_service_catalog_owner_team', 'service_catalog', ['owner_team'])

    # 2. production_readiness
    op.create_table(
        'production_readiness',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('readiness_score', sa.Float(), nullable=False),
        sa.Column('slo_coverage', sa.Boolean(), nullable=False),
        sa.Column('backup_coverage', sa.Boolean(), nullable=False),
        sa.Column('observability_coverage', sa.Boolean(), nullable=False),
        sa.Column('security_controls_passed', sa.Boolean(), nullable=False),
        sa.Column('dr_readiness_passed', sa.Boolean(), nullable=False),
        sa.Column('checklist_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 3. service_health
    op.create_table(
        'service_health',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('liveness', sa.Boolean(), nullable=False),
        sa.Column('readiness', sa.Boolean(), nullable=False),
        sa.Column('startup', sa.Boolean(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('error_rate', sa.Float(), nullable=False),
        sa.Column('active_version', sa.String(length=50), nullable=False),
        sa.Column('last_probe_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_service_health_service_name', 'service_health', ['service_name'])

    # 4. incidents
    op.create_table(
        'incidents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('incident_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('owner_id', sa.String(length=100), nullable=False),
        sa.Column('incident_commander', sa.String(length=100), nullable=False),
        sa.Column('affected_services_json', sa.JSON(), nullable=False),
        sa.Column('linked_alerts_json', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.String(length=50), nullable=False),
        sa.Column('resolved_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_number'),
    )

    # 5. durable_remediation_evidence
    op.create_table(
        'durable_remediation_evidence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('remediation_id', sa.String(length=36), nullable=False),
        sa.Column('trigger_alert_id', sa.String(length=100), nullable=False),
        sa.Column('target_service', sa.String(length=100), nullable=False),
        sa.Column('action_contract_id', sa.String(length=100), nullable=False),
        sa.Column('governance_decision_id', sa.String(length=36), nullable=False),
        sa.Column('policy_evaluation_id', sa.String(length=36), nullable=False),
        sa.Column('before_state_json', sa.JSON(), nullable=False),
        sa.Column('after_state_json', sa.JSON(), nullable=False),
        sa.Column('verification_result', sa.String(length=50), nullable=False),
        sa.Column('executed_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('remediation_id'),
    )

    # 6. deployments
    op.create_table(
        'deployments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('deployment_number', sa.String(length=50), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('release_version', sa.String(length=50), nullable=False),
        sa.Column('artifact_checksum', sa.String(length=64), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False),
        sa.Column('config_version', sa.String(length=50), nullable=False),
        sa.Column('policy_version_id', sa.String(length=36), nullable=False),
        sa.Column('rollout_strategy', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('deployed_by', sa.String(length=100), nullable=False),
        sa.Column('deployed_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deployment_number'),
    )


def downgrade():
    op.drop_table('deployments')
    op.drop_table('durable_remediation_evidence')
    op.drop_table('incidents')
    op.drop_table('service_health')
    op.drop_table('production_readiness')
    op.drop_table('service_catalog')
