"""AEGIS SQLAlchemy Declarative Base with Multi-Tenant Audit Metadata."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class AEGISBaseModel(Base):
    """Abstract Base Model with mandatory audit & multi-tenancy columns."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), index=True, nullable=False, default="00000000-0000-0000-0000-000000000001"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    updated_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
