"""Knowledge Indexing ORM Models."""

from sqlalchemy import String, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class KnowledgeIndexModel(AEGISBaseModel):
    __tablename__ = "knowledge_indexes"

    index_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    index_type: Mapped[str] = mapped_column(String(50), nullable=False)  # VECTOR, LEXICAL, HYBRID
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
