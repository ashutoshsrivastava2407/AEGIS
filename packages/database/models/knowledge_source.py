"""Knowledge Source ORM Model."""

from sqlalchemy import String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class KnowledgeSourceModel(AEGISBaseModel):
    __tablename__ = "knowledge_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # FILE, S3, REST, DATABASE
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
