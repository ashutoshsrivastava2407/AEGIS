"""AEGIS Governed Agent Memory & LangGraph Orchestration ORM Database Models."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, JSON, Float, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentMemoryModel(AEGISBaseModel):
    """Governed agent memory record spanning episodic, semantic, procedural, short-term, and workspace context."""

    __tablename__ = "agent_memories"
    __table_args__ = {"extend_existing": True}

    memory_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    workspace_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    agent_id: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    agent_run_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    memory_namespace: Mapped[str] = mapped_column(String(100), nullable=False, default="default", index=True)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SHORT_TERM_STATE, EPISODIC_MEMORY, SEMANTIC_MEMORY, PROCEDURAL_MEMORY, USER_WORKSPACE_MEMORY
    memory_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    structured_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="TOOL_EXECUTION")  # TOOL_EXECUTION, AGENT_REASONING, HUMAN_INPUT, VERIFICATION_OUTCOME
    source_reference: Mapped[str] = mapped_column(String(100), nullable=True)
    source_trace_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.9, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    data_classification: Mapped[str] = mapped_column(String(50), nullable=False, default="INTERNAL")
    sensitivity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    retention_policy: Mapped[str] = mapped_column(String(50), nullable=False, default="INDEFINITE")
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, SUPERSEDED, REVOKED, EXPIRED
    created_by: Mapped[str] = mapped_column(String(50), nullable=False, default="system")
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AgentMemoryEventModel(AEGISBaseModel):
    """Immutable audit trail for every memory read, write, update, supersession, or revocation."""

    __tablename__ = "agent_memory_events"
    __table_args__ = {"extend_existing": True}

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    memory_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # WRITE, READ, SEARCH, SUPERSEDE, REVOKE, EXPIRE
    actor_id: Mapped[str] = mapped_column(String(50), nullable=False, default="system")
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    event_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AgentMemoryNamespaceModel(AEGISBaseModel):
    """Memory namespace isolation definition."""

    __tablename__ = "agent_memory_namespaces"
    __table_args__ = {"extend_existing": True}

    namespace_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    workspace_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    default_retention_policy: Mapped[str] = mapped_column(String(50), nullable=False, default="INDEFINITE")


class AgentMemoryRetrievalModel(AEGISBaseModel):
    """Audit log of compiled memory context lookups."""

    __tablename__ = "agent_memory_retrievals"
    __table_args__ = {"extend_existing": True}

    retrieval_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    agent_run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    query: Mapped[str] = mapped_column(String(1000), nullable=False)
    retrieved_memory_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    relevance_scores: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    compilation_budget_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AgentGraphCheckpointModel(AEGISBaseModel):
    """Durable state checkpoint model for LangGraph agent execution runs."""

    __tablename__ = "agent_graph_checkpoints"
    __table_args__ = {"extend_existing": True}

    checkpoint_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default", index=True)
    thread_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    agent_run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, default="aegis_master_graph", index=True)
    step_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    checkpoint_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, PAUSED_APPROVAL, COMPLETED, FAILED, RESUMED
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
