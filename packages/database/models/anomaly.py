"""AEGIS Statistical Anomaly Record ORM Model.

Stores detected metric outliers, z-score deviations, expected value bounds, and evidence lineage.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class AnomalyModel(Base):
    """Statistical Anomaly Event entity."""

    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    metric_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    dataset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    observed_value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_min: Mapped[float] = mapped_column(Float, nullable=False)
    expected_max: Mapped[float] = mapped_column(Float, nullable=False)
    z_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    detection_method: Mapped[str] = mapped_column(String(64), nullable=False, default="Z_SCORE")  # Z_SCORE, EWMA, ROLLING_THRESHOLD, SEASONAL
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE", index=True)  # ACTIVE, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    lineage_ref: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
