"""AEGIS Stream Topic ORM Model.

Tracks streaming topics, partition configurations, retention settings, and schema bindings.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Integer, BigInteger, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class StreamTopicModel(Base):
    """Real-time topic entity."""

    __tablename__ = "stream_topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("stream_sources.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    partitions: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    replication_factor: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    retention_ms: Mapped[int] = mapped_column(BigInteger, nullable=False, default=604800000)  # 7 days
    retention_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1073741824)  # 1 GB
    cleanup_policy: Mapped[str] = mapped_column(String(32), nullable=False, default="delete")
    schema_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE", index=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
