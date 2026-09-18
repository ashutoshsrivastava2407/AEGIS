"""Data Contract Database Model."""

from sqlalchemy import String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DataContractModel(AEGISBaseModel):
    __tablename__ = "data_contracts"

    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    sla_freshness_minutes: Mapped[int] = mapped_column(default=60, nullable=False)
    quality_rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    contract_status: Mapped[str] = mapped_column(String(50), default="VERIFIED", nullable=False)
