"""Data Quality Check & Result Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DataQualityCheckModel(AEGISBaseModel):
    __tablename__ = "data_quality_checks"

    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    check_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # COMPLETENESS, UNIQUENESS, VALIDITY, CONSISTENCY, FRESHNESS, VOLUME
    configuration: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="WARNING", nullable=False)  # CRITICAL, WARNING, INFO
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class DataQualityResultModel(AEGISBaseModel):
    __tablename__ = "data_quality_results"

    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    dataset_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("dataset_versions.id"), nullable=True, index=True)
    check_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_quality_checks.id"), nullable=True, index=True)
    check_type: Mapped[str] = mapped_column(String(50), nullable=False)
    check_status: Mapped[str] = mapped_column(String(50), nullable=False)  # PASSED, FAILED, WARNING
    evaluated_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
