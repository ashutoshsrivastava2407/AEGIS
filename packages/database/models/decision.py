"""Decision, Decision Version, and Decision Context Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionModel(AEGISBaseModel):
    """Core Decision enterprise model with optimistic concurrency control."""

    __tablename__ = "decisions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    requester: Mapped[str] = mapped_column(String(100), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    business_domain: Mapped[str] = mapped_column(String(50), default="ENTERPRISE", nullable=False, index=True)
    decision_status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(50), default="MEDIUM_RISK", nullable=False)
    due_at: Mapped[str] = mapped_column(String(50), nullable=True)
    affected_resources_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    execution_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    integrity_status: Mapped[str] = mapped_column(String(50), default="VALID", nullable=False)
    integrity_rationale: Mapped[str] = mapped_column(Text, nullable=True)
    eligibility_status: Mapped[str] = mapped_column(String(50), default="APPROVAL_REQUIRED", nullable=False)
    eligibility_rationale: Mapped[str] = mapped_column(Text, nullable=True)
    active_version_id: Mapped[str] = mapped_column(String(36), nullable=True)


class DecisionVersionModel(AEGISBaseModel):
    """Immutable, creation-only Decision Version storing full Decision Manifest."""

    __tablename__ = "decision_versions"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    manifest_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    context_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    manifest_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class DecisionContextModel(AEGISBaseModel):
    """Decision Context Snapshot model storing input dataset & metric references."""

    __tablename__ = "decision_contexts"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False)
    context_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    datasets_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    metrics_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    anomalies_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    models_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    documents_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    policies_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    agent_runs_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    scenarios_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    constraints_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    data_freshness_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    data_quality_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
