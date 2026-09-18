"""Quarantine Record Database Model."""

from sqlalchemy import String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class QuarantineRecordModel(AEGISBaseModel):
    __tablename__ = "quarantine_records"

    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    ingestion_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("ingestion_jobs.id"), nullable=True, index=True)
    dataset_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("dataset_versions.id"), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=False)
    validation_rule: Mapped[str] = mapped_column(String(255), nullable=False)
    source_record_reference: Mapped[str] = mapped_column(String(255), nullable=True)
