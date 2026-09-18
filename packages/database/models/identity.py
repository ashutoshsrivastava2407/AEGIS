"""Identity, Non-Human Service Identity, Session, and Authentication Method Database Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class ServiceIdentityModel(AEGISBaseModel):
    """Non-Human Service Identity Model for Workflows, Agents, Services, Connectors, and Scheduled Jobs."""

    __tablename__ = "service_identities"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    identity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # WORKFLOW, AGENT, SERVICE, CONNECTOR, SCHEDULED_JOB
    description: Mapped[str] = mapped_column(Text, nullable=True)
    roles_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    permissions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    allowed_domains_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_ceiling: Mapped[str] = mapped_column(String(50), default="HIGH_RISK", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SessionModel(AEGISBaseModel):
    """User & Identity Active Session Management Model."""

    __tablename__ = "user_sessions"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    auth_provider: Mapped[str] = mapped_column(String(50), default="LOCAL", nullable=False)
    auth_strength: Mapped[str] = mapped_column(String(50), default="NORMAL_AUTH", nullable=False)  # NORMAL_AUTH, MFA_REQUIRED, STEP_UP_REQUIRED, PRIVILEGED_AUTH
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)  # ACTIVE, EXPIRED, REVOKED
    expires_at: Mapped[str] = mapped_column(String(50), nullable=False)


class AuthMethodModel(AEGISBaseModel):
    """Enterprise Authentication Provider Configuration Model (Local, OIDC, SAML, OAuth2)."""

    __tablename__ = "auth_methods"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)  # LOCAL, OIDC, SAML2, OAUTH2
    config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
