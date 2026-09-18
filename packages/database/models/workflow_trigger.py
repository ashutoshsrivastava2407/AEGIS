"""Workflow Trigger, Schedule, and Event Inbox Database Models."""

from sqlalchemy import String, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class WorkflowTriggerModel(AEGISBaseModel):
    """Workflow Trigger Registration Model."""

    __tablename__ = "workflow_triggers"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # EVENT, SCHEDULE, API, DECISION, HUMAN
    event_topic: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    deduplication_key: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    trigger_config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WorkflowScheduleModel(AEGISBaseModel):
    """Workflow Cron & Interval Schedule Model."""

    __tablename__ = "workflow_schedules"

    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    schedule_cron: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    dst_behavior: Mapped[str] = mapped_column(String(50), default="ADJUST", nullable=False)
    misfire_policy: Mapped[str] = mapped_column(String(50), default="RUN_IMMEDIATELY", nullable=False)
    catch_up_policy: Mapped[str] = mapped_column(String(50), default="IGNORE", nullable=False)
    overlap_policy: Mapped[str] = mapped_column(String(50), default="SKIP", nullable=False)  # SKIP, QUEUE, ALLOW_CONCURRENT, REPLACE
    max_concurrent_runs: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_run_at: Mapped[str] = mapped_column(String(50), nullable=True)
    next_run_at: Mapped[str] = mapped_column(String(50), nullable=True)


class WorkflowEventInboxModel(AEGISBaseModel):
    """Transactional Event Inbox Deduplication Model."""

    __tablename__ = "workflow_event_inbox"

    event_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    deduplication_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False)
    processed_at: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PROCESSED", nullable=False)
