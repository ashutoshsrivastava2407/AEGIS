"""Compliance Framework, Control Mapping, Evidence Record, Sealed Audit Package, and Assessment Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class ComplianceFrameworkModel(AEGISBaseModel):
    """Compliance Framework Abstraction Model (SOC 2, ISO 27001, GDPR, Internal Controls)."""

    __tablename__ = "compliance_frameworks"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # SOC_2, ISO_27001, GDPR, INTERNAL_CONTROLS
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ComplianceControlModel(AEGISBaseModel):
    """Compliance Control Requirement Model."""

    __tablename__ = "compliance_controls"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    control_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. CC6.1, A.9.1.1, Art.32
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)


class ControlMappingModel(AEGISBaseModel):
    """Mapping Control Requirement to AEGIS Policy Version / System Asset."""

    __tablename__ = "control_mappings"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    control_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    asset_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    mapping_type: Mapped[str] = mapped_column(String(50), default="POLICY_MAPPING", nullable=False)


class EvidenceRecordModel(AEGISBaseModel):
    """Automatically Collected Compliance Evidence Model with Integrity SHA-256 Checksums."""

    __tablename__ = "evidence_records"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    control_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # AUDIT_LOG, POLICY_VERSION, ACCESS_REVIEW, WORKFLOW_RUN, APPROVAL
    integrity_checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    evidence_payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    collected_at: Mapped[str] = mapped_column(String(50), nullable=False)


class AuditPackageModel(AEGISBaseModel):
    """Sealed Auditable Evidence Package Model."""

    __tablename__ = "audit_packages"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    framework_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sealed_checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    evidence_ids_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SEALED", nullable=False)
    sealed_at: Mapped[str] = mapped_column(String(50), nullable=False)


class ComplianceAssessmentModel(AEGISBaseModel):
    """Periodic Compliance Posture Score Assessment Model."""

    __tablename__ = "compliance_assessments"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    compliance_score_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    passed_controls_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_controls_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assessed_at: Mapped[str] = mapped_column(String(50), nullable=False)
