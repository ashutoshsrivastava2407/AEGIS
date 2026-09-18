"""Governance Asset, Data Classification, Retention Policy, SoD Rule, and Privileged Access Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class GovernanceAssetModel(AEGISBaseModel):
    """Universal Governance Asset Registry Model (Datasets, Models, Agents, Workflows, Decisions, Connectors)."""

    __tablename__ = "governance_assets"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    asset_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DATASET, MODEL, AGENT, WORKFLOW, DECISION, CONNECTOR
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    steward: Mapped[str] = mapped_column(String(100), nullable=True)
    classification: Mapped[str] = mapped_column(String(50), default="INTERNAL", nullable=False)  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DataClassificationModel(AEGISBaseModel):
    """Data Classification & Sensitivity Mapping Model."""

    __tablename__ = "data_classifications"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    classification_level: Mapped[str] = mapped_column(String(50), nullable=False)  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    contains_pii: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    residency_region: Mapped[str] = mapped_column(String(50), default="US", nullable=False)
    policy_tags_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RetentionPolicyModel(AEGISBaseModel):
    """Data & Artifact Retention Policy Model."""

    __tablename__ = "retention_policies"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    resource_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DATASETS, DOCUMENTS, WORKFLOWS, DECISIONS, AUDIT_LOGS, MODELS
    retention_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)
    action_on_expire: Mapped[str] = mapped_column(String(50), default="ANONYMIZE", nullable=False)  # DELETE, ANONYMIZE, ARCHIVE
    legal_hold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SoDRuleModel(AEGISBaseModel):
    """Policy-based Segregation of Duties Rule Model."""

    __tablename__ = "sod_rules"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    conflicting_permissions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # e.g., ["requester", "approver"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PrivilegedAccessRequestModel(AEGISBaseModel):
    """Temporary Privileged Access Elevation Request Model."""

    __tablename__ = "privileged_access_requests"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    requester_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role_requested: Mapped[str] = mapped_column(String(100), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, ACTIVE, EXPIRED, REVOKED
    approved_by: Mapped[str] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[str] = mapped_column(String(50), nullable=True)


class LegalHoldModel(AEGISBaseModel):
    """Legal Hold Protection Model Overriding Retention Deletion."""

    __tablename__ = "legal_holds"

    hold_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    case_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    matter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    custodian: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    active_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    applied_at: Mapped[str] = mapped_column(String(50), nullable=False)
    applied_by: Mapped[str] = mapped_column(String(100), nullable=False)
    released_at: Mapped[str] = mapped_column(String(50), nullable=True)
    released_by: Mapped[str] = mapped_column(String(100), nullable=True)

