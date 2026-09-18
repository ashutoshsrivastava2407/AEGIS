"""AEGIS Step 10 Security Hardening Additive Migration.

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-18 20:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    # 1. durable_policy_decisions
    op.create_table(
        'durable_policy_decisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('evaluation_id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=100), nullable=False),
        sa.Column('subject_type', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('requested_action', sa.String(length=100), nullable=False),
        sa.Column('policy_id', sa.String(length=36), nullable=False),
        sa.Column('policy_version_id', sa.String(length=36), nullable=False),
        sa.Column('policy_fingerprint', sa.String(length=64), nullable=False),
        sa.Column('rbac_result_json', sa.JSON(), nullable=False),
        sa.Column('abac_result_json', sa.JSON(), nullable=False),
        sa.Column('risk_result_json', sa.JSON(), nullable=False),
        sa.Column('approval_requirement', sa.String(length=50), nullable=False),
        sa.Column('authentication_strength', sa.String(length=50), nullable=False),
        sa.Column('classification_context', sa.String(length=50), nullable=False),
        sa.Column('final_effect', sa.String(length=50), nullable=False),
        sa.Column('reason_codes_json', sa.JSON(), nullable=False),
        sa.Column('matched_rule_ids_json', sa.JSON(), nullable=False),
        sa.Column('evidence_references_json', sa.JSON(), nullable=False),
        sa.Column('evaluated_at', sa.String(length=50), nullable=False),
        sa.Column('decision_expiration_at', sa.String(length=50), nullable=True),
        sa.Column('correlation_id', sa.String(length=36), nullable=True),
        sa.Column('workflow_run_id', sa.String(length=36), nullable=True),
        sa.Column('decision_id', sa.String(length=36), nullable=True),
        sa.Column('action_id', sa.String(length=36), nullable=True),
        sa.Column('input_context_hash', sa.String(length=64), nullable=False),
        sa.Column('output_decision_hash', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evaluation_id'),
    )
    op.create_index('ix_durable_policy_decisions_tenant_id', 'durable_policy_decisions', ['tenant_id'])
    op.create_index('ix_durable_policy_decisions_evaluation_id', 'durable_policy_decisions', ['evaluation_id'])
    op.create_index('ix_durable_policy_decisions_subject_id', 'durable_policy_decisions', ['subject_id'])
    op.create_index('ix_durable_policy_decisions_resource_id', 'durable_policy_decisions', ['resource_id'])
    op.create_index('ix_durable_policy_decisions_final_effect', 'durable_policy_decisions', ['final_effect'])

    # 2. audit_integrity_checkpoints
    op.create_table(
        'audit_integrity_checkpoints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('checkpoint_id', sa.String(length=36), nullable=False),
        sa.Column('first_event_id', sa.String(length=100), nullable=False),
        sa.Column('last_event_id', sa.String(length=100), nullable=False),
        sa.Column('first_hash', sa.String(length=64), nullable=False),
        sa.Column('final_hash', sa.String(length=64), nullable=False),
        sa.Column('checkpoint_digest', sa.String(length=64), nullable=False),
        sa.Column('event_count', sa.Integer(), nullable=False),
        sa.Column('algorithm', sa.String(length=50), nullable=False),
        sa.Column('trust_boundary', sa.String(length=50), nullable=False),
        sa.Column('anchor_status', sa.String(length=50), nullable=False),
        sa.Column('anchor_reference', sa.String(length=255), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('checkpoint_id'),
    )
    op.create_index('ix_audit_integrity_checkpoints_tenant_id', 'audit_integrity_checkpoints', ['tenant_id'])
    op.create_index('ix_audit_integrity_checkpoints_checkpoint_id', 'audit_integrity_checkpoints', ['checkpoint_id'])
    op.create_index('ix_audit_integrity_checkpoints_digest', 'audit_integrity_checkpoints', ['checkpoint_digest'])

    # 3. break_glass_reviews
    op.create_table(
        'break_glass_reviews',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('resources_touched_json', sa.JSON(), nullable=False),
        sa.Column('actions_executed_json', sa.JSON(), nullable=False),
        sa.Column('policies_overridden_json', sa.JSON(), nullable=False),
        sa.Column('activated_at', sa.String(length=50), nullable=False),
        sa.Column('expired_at', sa.String(length=50), nullable=False),
        sa.Column('reviewer_id', sa.String(length=100), nullable=True),
        sa.Column('review_status', sa.String(length=50), nullable=False),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('closed_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('review_id'),
    )
    op.create_index('ix_break_glass_reviews_tenant_id', 'break_glass_reviews', ['tenant_id'])
    op.create_index('ix_break_glass_reviews_review_id', 'break_glass_reviews', ['review_id'])
    op.create_index('ix_break_glass_reviews_session_id', 'break_glass_reviews', ['session_id'])

    # 4. legal_holds
    op.create_table(
        'legal_holds',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('hold_id', sa.String(length=36), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('case_reference', sa.String(length=100), nullable=False),
        sa.Column('matter_name', sa.String(length=255), nullable=False),
        sa.Column('custodian', sa.String(length=100), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('active_status', sa.Boolean(), nullable=False),
        sa.Column('applied_at', sa.String(length=50), nullable=False),
        sa.Column('applied_by', sa.String(length=100), nullable=False),
        sa.Column('released_at', sa.String(length=50), nullable=True),
        sa.Column('released_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hold_id'),
    )
    op.create_index('ix_legal_holds_tenant_id', 'legal_holds', ['tenant_id'])
    op.create_index('ix_legal_holds_hold_id', 'legal_holds', ['hold_id'])
    op.create_index('ix_legal_holds_resource_id', 'legal_holds', ['resource_id'])


def downgrade():
    op.drop_table('legal_holds')
    op.drop_table('break_glass_reviews')
    op.drop_table('audit_integrity_checkpoints')
    op.drop_table('durable_policy_decisions')
