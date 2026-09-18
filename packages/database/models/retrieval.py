"""Knowledge Retrieval ORM Models."""

from sqlalchemy import String, Text, JSON, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class RetrievalQueryModel(AEGISBaseModel):
    __tablename__ = "retrieval_queries"

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_strategy: Mapped[str] = mapped_column(String(50), default="HYBRID", nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class RetrievalResultModel(AEGISBaseModel):
    __tablename__ = "retrieval_results"

    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("retrieval_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(36), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieval_type: Mapped[str] = mapped_column(String(50), nullable=False)  # VECTOR, LEXICAL, HYBRID
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RerankingResultModel(AEGISBaseModel):
    __tablename__ = "reranking_results"

    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("retrieval_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    reranker_model: Mapped[str] = mapped_column(String(100), nullable=False)
    initial_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    reranked_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)


class ContextAssemblyModel(AEGISBaseModel):
    __tablename__ = "context_assemblies"

    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("retrieval_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    assembled_context: Mapped[str] = mapped_column(Text, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_ids_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
