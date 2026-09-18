"""AEGIS Dead-Letter Queue (DLQ) Record ORM Model.

Stores rejected, malformed, or un-processable streaming events with complete context and replay state.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Integer, BigInteger, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class DLQRecordModel(Base):
    """Dead-Letter Queue record entity."""

    __tablename__ = "dlq_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    topic_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    partition_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    offset: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    error_category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="SCHEMA_VALIDATION_FAILED",
        index=True
    )  # SCHEMA_VALIDATION_FAILED, DESERIALIZATION_ERROR, CONTRACT_VIOLATION, PROCESSOR_EXCEPTION
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING", index=True)  # PENDING, REPLAYED, DISCARDED
    replayed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
