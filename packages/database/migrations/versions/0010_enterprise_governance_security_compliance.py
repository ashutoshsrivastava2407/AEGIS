"""AEGIS Enterprise Governance, Security, Compliance, and Policy Control Plane Foundation Migration.

Revision ID: 0010
Revises: 0009
Create Date: 2026-09-18 16:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    # 1. service_identities
    op.create_table(
        'service_identities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('identity_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('roles_json', sa.JSON(), nullable=False),
        sa.Column('permissions_json', sa.JSON(), nullable=False),
        sa.Column('allowed_domains_json', sa.JSON(), nullable=False),
        sa.Column('risk_ceiling', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_service_identities_tenant_id', 'service_identities', ['tenant_id'])
    op.create_index('ix_service_identities_name', 'service_identities', ['name'])
    op.create_index('ix_service_identities_identity_type', 'service_identities', ['identity_type'])

    # 2. user_sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('session_token_hash', sa.String(length=64), nullable=False),
        sa.Column('auth_provider', sa.String(length=50), nullable=False),
        sa.Column('auth_strength', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_sessions_tenant_id', 'user_sessions', ['tenant_id'])
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_session_token_hash', 'user_sessions', ['session_token_hash'], unique=True)
    op.create_index('ix_user_sessions_status', 'user_sessions', ['status'])

    # 3. auth_methods
    op.create_table(
        'auth_methods',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_auth_methods_tenant_id', 'auth_methods', ['tenant_id'])

    # 4. security_roles
    op.create_table(
        'security_roles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions_json', sa.JSON(), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_roles_tenant_id', 'security_roles', ['tenant_id'])
    op.create_index('ix_security_roles_name', 'security_roles', ['name'])

    # 5. security_permissions
    op.create_table(
        'security_permissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_permissions_name', 'security_permissions', ['name'], unique=True)

    # 6. role_bindings
    op.create_table(
        'role_bindings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.String(length=100), nullable=False),
        sa.Column('subject_type', sa.String(length=50), nullable=False),
        sa.Column('role_id', sa.String(length=36), nullable=False),
        sa.Column('domain_scope', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_role_bindings_tenant_id', 'role_bindings', ['tenant_id'])
    op.create_index('ix_role_bindings_subject_id', 'role_bindings', ['subject_id'])
    op.create_index('ix_role_bindings_role_id', 'role_bindings', ['role_id'])

    # 7. resource_permissions
    op.create_table(
        'resource_permissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('subject_id', sa.String(length=100), nullable=False),
        sa.Column('capability', sa.String(length=50), nullable=False),
        sa.Column('effect', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_resource_permissions_tenant_id', 'resource_permissions', ['tenant_id'])
    op.create_index('ix_resource_permissions_resource_type', 'resource_permissions', ['resource_type'])
    op.create_index('ix_resource_permissions_resource_id', 'resource_permissions', ['resource_id'])
    op.create_index('ix_resource_permissions_subject_id', 'resource_permissions', ['subject_id'])

    # 8. access_reviews
    op.create_table(
        'access_reviews',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('review_name', sa.String(length=255), nullable=False),
        sa.Column('reviewer_id', sa.String(length=100), nullable=False),
        sa.Column('target_subject_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('findings_json', sa.JSON(), nullable=False),
        sa.Column('due_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_access_reviews_tenant_id', 'access_reviews', ['tenant_id'])
    op.create_index('ix_access_reviews_status', 'access_reviews', ['status'])

    # 9. security_policies
    op.create_table(
        'security_policies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('active_version_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_policies_tenant_id', 'security_policies', ['tenant_id'])
    op.create_index('ix_security_policies_category', 'security_policies', ['category'])
    op.create_index('ix_security_policies_status', 'security_policies', ['status'])

    # 10. security_policy_versions
    op.create_table(
        'security_policy_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('fingerprint', sa.String(length=64), nullable=False),
        sa.Column('rules_json', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_policy_versions_policy_id', 'security_policy_versions', ['policy_id'])
    op.create_index('ix_security_policy_versions_fingerprint', 'security_policy_versions', ['fingerprint'])

    # 11. security_policy_rules
    op.create_table(
        'security_policy_rules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.String(length=36), nullable=False),
        sa.Column('policy_version_id', sa.String(length=36), nullable=False),
        sa.Column('rule_key', sa.String(length=100), nullable=False),
        sa.Column('subject_pattern', sa.String(length=255), nullable=False),
        sa.Column('resource_pattern', sa.String(length=255), nullable=False),
        sa.Column('action_pattern', sa.String(length=255), nullable=False),
        sa.Column('condition_expression', sa.Text(), nullable=True),
        sa.Column('effect', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_policy_rules_policy_id', 'security_policy_rules', ['policy_id'])
    op.create_index('ix_security_policy_rules_policy_version_id', 'security_policy_rules', ['policy_version_id'])

    # 12. security_policy_evaluations
    op.create_table(
        'security_policy_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('policy_version_id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('reason_code', sa.String(length=100), nullable=False),
        sa.Column('matched_rules_json', sa.JSON(), nullable=False),
        sa.Column('risk_score', sa.JSON(), nullable=False),
        sa.Column('evaluated_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_policy_evaluations_tenant_id', 'security_policy_evaluations', ['tenant_id'])
    op.create_index('ix_security_policy_evaluations_policy_version_id', 'security_policy_evaluations', ['policy_version_id'])
    op.create_index('ix_security_policy_evaluations_subject_id', 'security_policy_evaluations', ['subject_id'])
    op.create_index('ix_security_policy_evaluations_decision', 'security_policy_evaluations', ['decision'])

    # 13. security_policy_conflicts
    op.create_table(
        'security_policy_conflicts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('policy_a_id', sa.String(length=36), nullable=False),
        sa.Column('policy_b_id', sa.String(length=36), nullable=False),
        sa.Column('conflict_type', sa.String(length=50), nullable=False),
        sa.Column('details_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 14. security_policy_exceptions
    op.create_table(
        'security_policy_exceptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=100), nullable=False),
        sa.Column('resource_scope', sa.String(length=255), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_policy_exceptions_tenant_id', 'security_policy_exceptions', ['tenant_id'])
    op.create_index('ix_security_policy_exceptions_policy_id', 'security_policy_exceptions', ['policy_id'])
    op.create_index('ix_security_policy_exceptions_status', 'security_policy_exceptions', ['status'])

    # 15. governance_assets
    op.create_table(
        'governance_assets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.String(length=100), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('steward', sa.String(length=100), nullable=True),
        sa.Column('classification', sa.String(length=50), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_governance_assets_tenant_id', 'governance_assets', ['tenant_id'])
    op.create_index('ix_governance_assets_asset_id', 'governance_assets', ['asset_id'])
    op.create_index('ix_governance_assets_asset_type', 'governance_assets', ['asset_type'])

    # 16. data_classifications
    op.create_table(
        'data_classifications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('classification_level', sa.String(length=50), nullable=False),
        sa.Column('contains_pii', sa.Boolean(), nullable=False),
        sa.Column('residency_region', sa.String(length=50), nullable=False),
        sa.Column('policy_tags_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_data_classifications_tenant_id', 'data_classifications', ['tenant_id'])
    op.create_index('ix_data_classifications_resource_id', 'data_classifications', ['resource_id'])

    # 17. retention_policies
    op.create_table(
        'retention_policies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('resource_category', sa.String(length=50), nullable=False),
        sa.Column('retention_days', sa.Integer(), nullable=False),
        sa.Column('action_on_expire', sa.String(length=50), nullable=False),
        sa.Column('legal_hold', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 18. sod_rules
    op.create_table(
        'sod_rules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(length=255), nullable=False),
        sa.Column('conflicting_permissions_json', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 19. privileged_access_requests
    op.create_table(
        'privileged_access_requests',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.String(length=100), nullable=False),
        sa.Column('role_requested', sa.String(length=100), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('expires_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 20. security_events
    op.create_table(
        'security_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('actor_id', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('correlation_id', sa.String(length=100), nullable=False),
        sa.Column('details_json', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_security_events_tenant_id', 'security_events', ['tenant_id'])
    op.create_index('ix_security_events_event_type', 'security_events', ['event_type'])
    op.create_index('ix_security_events_actor_id', 'security_events', ['actor_id'])

    # 21. security_findings
    op.create_table(
        'security_findings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('finding_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('affected_asset_id', sa.String(length=100), nullable=False),
        sa.Column('evidence_json', sa.JSON(), nullable=False),
        sa.Column('remediation_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 22. security_investigations
    op.create_table(
        'security_investigations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('case_number', sa.String(length=100), nullable=False),
        sa.Column('lead_investigator', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('findings_ids_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 23. break_glass_sessions
    op.create_table(
        'break_glass_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.String(length=100), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('scope_restricted', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('activated_at', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 24. compliance_frameworks
    op.create_table(
        'compliance_frameworks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version_str', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 25. compliance_controls
    op.create_table(
        'compliance_controls',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('framework_id', sa.String(length=36), nullable=False),
        sa.Column('control_code', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 26. control_mappings
    op.create_table(
        'control_mappings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('control_id', sa.String(length=36), nullable=False),
        sa.Column('policy_version_id', sa.String(length=36), nullable=True),
        sa.Column('asset_id', sa.String(length=100), nullable=True),
        sa.Column('mapping_type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 27. evidence_records
    op.create_table(
        'evidence_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('control_id', sa.String(length=36), nullable=False),
        sa.Column('source_system', sa.String(length=100), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('integrity_checksum', sa.String(length=64), nullable=False),
        sa.Column('evidence_payload_json', sa.JSON(), nullable=False),
        sa.Column('collected_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 28. audit_packages
    op.create_table(
        'audit_packages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('package_name', sa.String(length=255), nullable=False),
        sa.Column('framework_id', sa.String(length=36), nullable=False),
        sa.Column('sealed_checksum', sa.String(length=64), nullable=False),
        sa.Column('evidence_ids_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('sealed_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 29. compliance_assessments
    op.create_table(
        'compliance_assessments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('framework_id', sa.String(length=36), nullable=False),
        sa.Column('compliance_score_percent', sa.Float(), nullable=False),
        sa.Column('passed_controls_count', sa.Integer(), nullable=False),
        sa.Column('failed_controls_count', sa.Integer(), nullable=False),
        sa.Column('assessed_at', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('compliance_assessments')
    op.drop_table('audit_packages')
    op.drop_table('evidence_records')
    op.drop_table('control_mappings')
    op.drop_table('compliance_controls')
    op.drop_table('compliance_frameworks')
    op.drop_table('break_glass_sessions')
    op.drop_table('security_investigations')
    op.drop_table('security_findings')
    op.drop_table('security_events')
    op.drop_table('privileged_access_requests')
    op.drop_table('sod_rules')
    op.drop_table('retention_policies')
    op.drop_table('data_classifications')
    op.drop_table('governance_assets')
    op.drop_table('security_policy_exceptions')
    op.drop_table('security_policy_conflicts')
    op.drop_table('security_policy_evaluations')
    op.drop_table('security_policy_rules')
    op.drop_table('security_policy_versions')
    op.drop_table('security_policies')
    op.drop_table('access_reviews')
    op.drop_table('resource_permissions')
    op.drop_table('role_bindings')
    op.drop_table('security_permissions')
    op.drop_table('security_roles')
    op.drop_table('auth_methods')
    op.drop_table('user_sessions')
    op.drop_table('service_identities')
