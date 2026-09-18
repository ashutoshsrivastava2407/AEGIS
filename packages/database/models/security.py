"""Security Event Audit, Security Finding, Incident Investigation, and Break-Glass Emergency Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class SecurityEventModel(AEGISBaseModel):
    """Dedicated Security Audit Event Log Model."""

    __tablename__ = "security_events"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # AUTH_FAILURE, LOGIN, LOGOUT, MFA_EVENT, ROLE_CHANGED, POLICY_CHANGED, PRIVILEGE_ELEVATED, DATA_EXPORT, CONNECTOR_BLOCKED, SSRF_BLOCKED, AGENT_POLICY_DENIED, BREAK_GLASS_USED
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(50), default="INFO", nullable=False, index=True)  # INFO, WARNING, HIGH, CRITICAL
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class SecurityFindingModel(AEGISBaseModel):
    """Security Threat & Anomaly Finding Model."""

    __tablename__ = "security_findings"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    finding_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), default="HIGH", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False, index=True)  # OPEN, TRIAGED, INVESTIGATING, CONTAINED, REMEDIATED, ACCEPTED_RISK, CLOSED
    affected_asset_id: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    remediation_notes: Mapped[str] = mapped_column(Text, nullable=True)


class SecurityInvestigationModel(AEGISBaseModel):
    """Security Incident Investigation Case Model."""

    __tablename__ = "security_investigations"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    case_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    lead_investigator: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    findings_ids_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class BreakGlassSessionModel(AEGISBaseModel):
    """Emergency Break-Glass Elevated Session Model."""

    __tablename__ = "break_glass_sessions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    scope_restricted: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)  # ACTIVE, EXPIRED, CLOSED
    activated_at: Mapped[str] = mapped_column(String(50), nullable=False)
    expires_at: Mapped[str] = mapped_column(String(50), nullable=False)


class AuditIntegrityCheckpointModel(AEGISBaseModel):
    """Deterministic Audit Hash Chain Segment Checkpoint Model."""

    __tablename__ = "audit_integrity_checkpoints"

    checkpoint_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    first_event_id: Mapped[str] = mapped_column(String(100), nullable=False)
    last_event_id: Mapped[str] = mapped_column(String(100), nullable=False)
    first_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    final_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    checkpoint_digest: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), default="SHA-256", nullable=False)

    trust_boundary: Mapped[str] = mapped_column(String(50), default="LOCAL_TRANSACTIONAL", nullable=False, index=True)  # LOCAL_TRANSACTIONAL, SIMULATED_EXTERNAL_ANCHOR, EXTERNALLY_ANCHORED
    anchor_status: Mapped[str] = mapped_column(String(50), default="UNANCHORED", nullable=False)
    anchor_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="VALID", nullable=False)


class BreakGlassReviewModel(AEGISBaseModel):
    """Post-Use Audit & Justification Review Model for Break-Glass Emergencies."""

    __tablename__ = "break_glass_reviews"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    justification: Mapped[str] = mapped_column(Text, nullable=False)

    resources_touched_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    actions_executed_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    policies_overridden_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    activated_at: Mapped[str] = mapped_column(String(50), nullable=False)
    expired_at: Mapped[str] = mapped_column(String(50), nullable=False)

    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=True)
    review_status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False, index=True)  # PENDING_REVIEW, UNDER_REVIEW, ACCEPTED, REQUIRES_REMEDIATION, CLOSED
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)
    closed_at: Mapped[str] = mapped_column(String(50), nullable=True)

