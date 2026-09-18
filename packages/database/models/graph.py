"""Knowledge Graph ORM Models."""

from sqlalchemy import String, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class KnowledgeEntityModel(AEGISBaseModel):
    __tablename__ = "knowledge_entities"

    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aliases_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    provenance_doc_id: Mapped[str] = mapped_column(String(36), nullable=True)


class KnowledgeRelationModel(AEGISBaseModel):
    __tablename__ = "knowledge_relations"

    source_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    provenance_chunk_id: Mapped[str] = mapped_column(String(36), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
