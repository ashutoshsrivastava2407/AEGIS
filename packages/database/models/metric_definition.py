"""AEGIS Metric Definition ORM Model.

Tracks versioned, governed KPI and metric definitions.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, JSON, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class MetricDefinitionModel(Base):
    """Governed Metric / KPI Definition entity."""

    __tablename__ = "metric_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="analytics_lead")
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="COUNT")  # USD, COUNT, PCT, RATIO, MS
    aggregation_type: Mapped[str] = mapped_column(String(32), nullable=False, default="SUM")  # SUM, AVG, COUNT, MIN, MAX, FORMULA
    dimensions: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    time_grain: Mapped[str] = mapped_column(String(32), nullable=False, default="DAILY")  # HOURLY, DAILY, WEEKLY, MONTHLY
    source_dataset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    calculation_formula: Mapped[str] = mapped_column(Text, nullable=False, default="SUM(value)")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
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
