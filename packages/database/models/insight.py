"""AEGIS Factual Insight Record ORM Model.

Stores analytical insights and dimensional root-cause decompositions derived from metrics and anomalies.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class InsightModel(Base):
    """Factual Analytical Insight entity."""

    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    insight_type: Mapped[str] = mapped_column(String(64), nullable=False, default="METRIC_TREND")  # METRIC_TREND, ANOMALY_BREAKDOWN, CROSS_DIMENSION
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metric_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    dataset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="INFO")  # INFO, WARNING, CRITICAL
    evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    lineage_ref: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN", index=True)  # OPEN, REVIEWED, ACTIONED, ARCHIVED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
