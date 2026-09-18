"""Enterprise Knowledge Document Models."""

from sqlalchemy import String, Text, JSON, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DocumentModel(AEGISBaseModel):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    collection: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PDF, DOCX, HTML, PPTX, TXT
    mime_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RECEIVED", nullable=False, index=True)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vector_index_id: Mapped[str] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DocumentVersionModel(AEGISBaseModel):
    __tablename__ = "document_versions"

    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    parser_name: Mapped[str] = mapped_column(String(100), default="default_parser", nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="READY", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DocumentCollectionModel(AEGISBaseModel):
    __tablename__ = "document_collections"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    access_policy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class DocumentCollectionMemberModel(AEGISBaseModel):
    __tablename__ = "document_collection_members"

    collection_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_collections.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)


class DocumentChunkModel(AEGISBaseModel):
    __tablename__ = "document_chunks"

    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str] = mapped_column(String(255), nullable=True)
    provenance_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
