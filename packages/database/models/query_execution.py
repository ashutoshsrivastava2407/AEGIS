"""AEGIS Query Execution & Saved Query ORM Models.

Tracks analytical query execution history, audit logs, and authorized saved queries.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import Base


class QueryExecutionModel(Base):
    """Query Execution Audit & Log entity."""

    __tablename__ = "query_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system_user")
    sql_text: Mapped[str] = mapped_column(Text, nullable=False)
    parameters_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCESS", index=True)  # SUCCESS, FAILED, TIMEOUT, REJECTED
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_type: Mapped[str] = mapped_column(String(32), nullable=False, default="ANALYTICAL_SELECT")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


class SavedQueryModel(Base):
    """Saved Analytical Query View entity."""

    __tablename__ = "saved_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sql_text: Mapped[str] = mapped_column(Text, nullable=False)
    parameters_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="analytics_user")
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
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
