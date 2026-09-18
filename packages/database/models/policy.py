"""Declarative Policy Engine, Immutable Versioning, Evaluation Trace, Conflict, and Exception Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class SecurityPolicyModel(AEGISBaseModel):
    """Declarative Policy Master Model."""

    __tablename__ = "security_policies"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # AUTHENTICATION, AUTHORIZATION, DATA_ACCESS, NETWORK, CONNECTOR, AI, AGENT, WORKFLOW, ACTION, MODEL, RETENTION, EXPORT, AUDIT, PRIVILEGED_ACCESS
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT, VALIDATED, APPROVED, ACTIVE, PAUSED, RETIRED
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    active_version_id: Mapped[str] = mapped_column(String(36), nullable=True)


class SecurityPolicyVersionModel(AEGISBaseModel):
    """Immutable, Creation-Only Published Security Policy Version Model."""

    __tablename__ = "security_policy_versions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    rules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SecurityPolicyRuleModel(AEGISBaseModel):
    """Declarative ABAC/RBAC Policy Rule Model."""

    __tablename__ = "security_policy_rules"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    rule_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subject_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    action_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    condition_expression: Mapped[str] = mapped_column(Text, nullable=True)
    effect: Mapped[str] = mapped_column(String(50), default="ALLOW", nullable=False)  # ALLOW, DENY, REQUIRE_APPROVAL, REQUIRE_STEP_UP, RESTRICT


class SecurityPolicyEvaluationModel(AEGISBaseModel):
    """Auditable Server-Side Policy Evaluation Record Model (No Chain-of-Thought)."""

    __tablename__ = "security_policy_evaluations"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    policy_version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ALLOW, DENY, REQUIRE_APPROVAL, REQUIRE_STEP_UP, RESTRICT
    reason_code: Mapped[str] = mapped_column(String(100), nullable=False)
    matched_rules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_score: Mapped[float] = mapped_column(JSON, default=dict, nullable=False)  # Float or Dict
    evaluated_at: Mapped[str] = mapped_column(String(50), nullable=False)


class SecurityPolicyConflictModel(AEGISBaseModel):
    """Detected Policy Contradiction and Shadowing Record Model."""

    __tablename__ = "security_policy_conflicts"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    policy_a_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_b_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CONTRADICTION, OVERLAP, UNREACHABLE, SHADOWED
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="UNRESOLVED", nullable=False)


class SecurityPolicyExceptionModel(AEGISBaseModel):
    """Time-Bounded, Governed Policy Exception Model."""

    __tablename__ = "security_policy_exceptions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_scope: Mapped[str] = mapped_column(String(255), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    approved_by: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="REQUESTED", nullable=False, index=True)  # REQUESTED, UNDER_REVIEW, APPROVED, ACTIVE, EXPIRED, REVOKED, REJECTED
    expires_at: Mapped[str] = mapped_column(String(50), nullable=False)


class DurablePolicyDecisionModel(AEGISBaseModel):
    """Immutable, Durable Historical Policy Decision Record Model."""

    __tablename__ = "durable_policy_decisions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    evaluation_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(50), default="USER", nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    requested_action: Mapped[str] = mapped_column(String(100), nullable=False)

    policy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    rbac_result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    abac_result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    approval_requirement: Mapped[str] = mapped_column(String(50), default="NONE", nullable=False)
    authentication_strength: Mapped[str] = mapped_column(String(50), default="NORMAL_AUTH", nullable=False)
    classification_context: Mapped[str] = mapped_column(String(50), default="INTERNAL", nullable=False)

    final_effect: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ALLOW, DENY, REQUIRE_APPROVAL, REQUIRE_STEP_UP, RESTRICT
    reason_codes_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    matched_rule_ids_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    evidence_references_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    evaluated_at: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_expiration_at: Mapped[str] = mapped_column(String(50), nullable=True)

    correlation_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    workflow_run_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    decision_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    action_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)

    input_context_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    output_decision_hash: Mapped[str] = mapped_column(String(64), nullable=False)

