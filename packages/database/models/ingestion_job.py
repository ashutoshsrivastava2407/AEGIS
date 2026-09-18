"""Ingestion Execution Run Database Model."""

from sqlalchemy import String, Text, JSON, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from packages.database.base import AEGISBaseModel


class IngestionJobModel(AEGISBaseModel):
    __tablename__ = "ingestion_jobs"

    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=False, index=True)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=True, index=True)
    run_identifier: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, RUNNING, SUCCEEDED, PARTIAL_SUCCESS, FAILED, CANCELLED
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    records_read: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_written: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bytes_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_details: Mapped[str] = mapped_column(Text, nullable=True)
