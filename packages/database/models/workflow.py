"""Workflow and Workflow Version Database Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class WorkflowModel(AEGISBaseModel):
    """Workflow Definition Master Model."""

    __tablename__ = "workflows"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    business_domain: Mapped[str] = mapped_column(String(50), default="ENTERPRISE", nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT, VALIDATED, ACTIVE, PAUSED, SUSPENDED, RETIRED
    trigger_type: Mapped[str] = mapped_column(String(50), default="MANUAL", nullable=False)  # EVENT, SCHEDULE, API, DECISION, HUMAN
    risk_profile: Mapped[str] = mapped_column(String(50), default="MEDIUM_RISK", nullable=False)
    timeout_policy_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    retry_policy_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    compensation_policy_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    active_version_id: Mapped[str] = mapped_column(String(36), nullable=True)


class WorkflowVersionModel(AEGISBaseModel):
    """Immutable, Creation-Only Workflow Version Model storing authoritative definition."""

    __tablename__ = "workflow_versions"

    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    definition_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    graph_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    node_contracts_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
