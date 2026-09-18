"""Cryptographically Verifiable Audit Log Database Model."""

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AuditEventModel(AEGISBaseModel):
    __tablename__ = "audit_events"

    actor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
