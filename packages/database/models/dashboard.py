"""AEGIS Dashboard & Dashboard Widget ORM Models.

Tracks customizable analytics dashboards and metric widgets.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Integer, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class DashboardModel(Base):
    """Analytics Dashboard Layout entity."""

    __tablename__ = "dashboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="analytics_admin")
    refresh_interval_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    layout_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
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


class DashboardWidgetModel(Base):
    """Dashboard Metric Widget entity."""

    __tablename__ = "dashboard_widgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id: Mapped[str] = mapped_column(String(36), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    widget_type: Mapped[str] = mapped_column(String(32), nullable=False, default="KPI_CARD")  # KPI_CARD, TIME_SERIES, BAR_CHART, DONUT, TABLE
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    query_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    position_x: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    position_y: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    width: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    height: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    config_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
