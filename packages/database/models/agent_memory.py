"""Agent Contextual & Episodic Memory Database Model."""

from sqlalchemy import String, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentMemoryModel(AEGISBaseModel):
    """Agent persistent episodic and semantic memory store."""

    __tablename__ = "agent_memories"

    agent_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    run_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SHORT_TERM, LONG_TERM, EPISODIC, WORKING
    memory_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    tags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
