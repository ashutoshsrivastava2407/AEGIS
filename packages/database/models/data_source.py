"""Data Source Database Model."""

from sqlalchemy import String, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from packages.database.base import AEGISBaseModel


class DataSourceModel(AEGISBaseModel):
    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # CSV, JSON, POSTGRESQL, REST_API
    description: Mapped[str] = mapped_column(Text, nullable=True)
    config_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_successful_ingestion_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
