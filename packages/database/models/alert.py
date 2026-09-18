"""AEGIS Alert Rule & Alert Event ORM Models.

Tracks governed analytical alert conditions and triggered alert event logs.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class AlertRuleModel(Base):
    """Governed Alert Rule entity."""

    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    metric_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    condition_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="THRESHOLD_GREATER"
    )  # THRESHOLD_GREATER, THRESHOLD_LESS, PCT_CHANGE, ANOMALY_DETECTED, QUALITY_DEGRADED
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evaluation_frequency_min: Mapped[int] = mapped_column(Float, nullable=False, default=15)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="HIGH", index=True)  # INFO, WARNING, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE", index=True)
    notification_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
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


class AlertEventModel(Base):
    """Triggered Alert Event entity."""

    __tablename__ = "alert_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_id: Mapped[str] = mapped_column(String(36), nullable=False)
    triggered_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="HIGH")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN", index=True)  # OPEN, ACKNOWLEDGED, RESOLVED
    details_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
