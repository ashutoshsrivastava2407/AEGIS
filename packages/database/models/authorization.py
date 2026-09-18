"""RBAC, ABAC, Resource Permission, Role Binding, and Access Review Database Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class RoleModel(AEGISBaseModel):
    """System, Tenant, Domain, and Custom Security Role Model."""

    __tablename__ = "security_roles"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role_type: Mapped[str] = mapped_column(String(50), default="CUSTOM", nullable=False)  # SYSTEM, TENANT, DOMAIN, CUSTOM
    description: Mapped[str] = mapped_column(Text, nullable=True)
    permissions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class PermissionModel(AEGISBaseModel):
    """Security Capability Permission Registry Model."""

    __tablename__ = "security_permissions"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class RoleBindingModel(AEGISBaseModel):
    """Subject-to-Role Assignment Binding Model."""

    __tablename__ = "role_bindings"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(50), default="USER", nullable=False)  # USER, SERVICE_IDENTITY, GROUP
    role_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    domain_scope: Mapped[str] = mapped_column(String(50), default="GLOBAL", nullable=False)
    expires_at: Mapped[str] = mapped_column(String(50), nullable=True)


class ResourcePermissionModel(AEGISBaseModel):
    """Resource-Level Authorization Model."""

    __tablename__ = "resource_permissions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # WORKSPACE, DATASET, DOCUMENT, MODEL, AGENT, WORKFLOW, DECISION, CONNECTOR, POLICY
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    capability: Mapped[str] = mapped_column(String(50), nullable=False)  # VIEW, EDIT, EXECUTE, APPROVE, ADMINISTER
    effect: Mapped[str] = mapped_column(String(50), default="ALLOW", nullable=False)


class AccessReviewModel(AEGISBaseModel):
    """Access Certification Review Campaign Model."""

    __tablename__ = "access_reviews"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    review_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_subject_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="REVIEW_OPENED", nullable=False, index=True)  # REVIEW_OPENED, REVIEWED, APPROVED, REMEDIATION, CLOSED
    findings_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    due_at: Mapped[str] = mapped_column(String(50), nullable=True)
