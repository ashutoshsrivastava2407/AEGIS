"""Dataset Domain Models (Medallion Architecture & Immutable Versioning)."""

from sqlalchemy import String, Text, JSON, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DatasetModel(AEGISBaseModel):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    layer: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # BRONZE, SILVER, GOLD
    domain: Mapped[str] = mapped_column(String(100), default="GENERAL", nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(100), default="data_eng", nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    schema_definition: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    latest_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    freshness: Mapped[str] = mapped_column(String(100), default="UP_TO_DATE", nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=True)


class DatasetVersionModel(AEGISBaseModel):
    __tablename__ = "dataset_versions"

    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    schema_snapshot: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    storage_location: Mapped[str] = mapped_column(String(512), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_version: Mapped[int] = mapped_column(Integer, nullable=True)
