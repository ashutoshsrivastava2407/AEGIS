"""AEGIS Stream Source ORM Model.

Tracks real-time streaming event sources (Kafka, Redpanda, Webhook, EventHub, Kinesis).
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class StreamSourceModel(Base):
    """Real-time stream source configuration entity."""

    __tablename__ = "stream_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, default="KAFKA")
    connection_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    format: Mapped[str] = mapped_column(String(32), nullable=False, default="JSON")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE", index=True)
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
