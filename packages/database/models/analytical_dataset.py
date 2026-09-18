"""AEGIS Analytical Dataset ORM Model.

Tracks governed analytical datasets derived from Gold or Silver data layers with lineage provenance.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class AnalyticalDatasetModel(Base):
    """Governed Analytical Dataset entity."""

    __tablename__ = "analytical_datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_dataset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    source_layer: Mapped[str] = mapped_column(String(32), nullable=False, default="GOLD")  # GOLD, SILVER, REALTIME_SILVER
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    schema_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="analytics_team")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE", index=True)
    refresh_info: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
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
