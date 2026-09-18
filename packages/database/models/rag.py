"""Grounded RAG ORM Models."""

from sqlalchemy import String, Text, JSON, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class CitationModel(AEGISBaseModel):
    __tablename__ = "citations"

    rag_request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    citation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    chunk_id: Mapped[str] = mapped_column(String(36), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str] = mapped_column(String(255), nullable=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RAGRequestModel(AEGISBaseModel):
    __tablename__ = "rag_requests"

    question: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version_id: Mapped[str] = mapped_column(String(36), nullable=True)
    retrieval_query_id: Mapped[str] = mapped_column(String(36), nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(100), default="system", nullable=False)


class RAGResponseModel(AEGISBaseModel):
    __tablename__ = "rag_responses"

    rag_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("rag_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    groundedness_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    citation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class GroundednessEvaluationModel(AEGISBaseModel):
    __tablename__ = "groundedness_evaluations"

    rag_response_id: Mapped[str] = mapped_column(String(36), ForeignKey("rag_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    groundedness_score: Mapped[float] = mapped_column(Float, nullable=False)
    citation_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    unsupported_claim_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evaluation_details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
