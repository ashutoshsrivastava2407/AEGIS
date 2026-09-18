"""AEGIS Stream Quality Metrics ORM Model.

Tracks streaming data quality metrics over time windows.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, Any
from sqlalchemy import String, DateTime, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class StreamQualityMetricsModel(Base):
    """Streaming data quality evaluation metrics entity."""

    __tablename__ = "stream_quality_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    topic_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_schema_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    late_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)  # 0.0 to 100.0%
    details_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
