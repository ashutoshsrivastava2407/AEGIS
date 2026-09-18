"""Embedding Platform ORM Models."""

from sqlalchemy import String, Text, JSON, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class EmbeddingModelModel(AEGISBaseModel):
    __tablename__ = "embedding_models"

    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Integer, default=True, nullable=False)


class EmbeddingRecordModel(AEGISBaseModel):
    __tablename__ = "embedding_records"

    chunk_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    vector_json: Mapped[dict] = mapped_column(JSON, nullable=False)  # Raw vector list representation
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
