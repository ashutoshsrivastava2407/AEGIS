"""Agent Tool & Permission Database Models."""

from sqlalchemy import String, Text, JSON, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentToolModel(AEGISBaseModel):
    """Tool definition catalog model."""

    __tablename__ = "agent_tools"
    __table_args__ = {"extend_existing": True}

    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DATA_PLATFORM, ANALYTICS, ML_PLATFORM, KNOWLEDGE_RAG, STREAMING, WORKFLOW, NOTIFICATION
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(50), default="LOW_RISK", nullable=False)  # READ_ONLY, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
    schema_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    input_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    is_governed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AgentToolPermissionModel(AEGISBaseModel):
    """Agent tool permission mapping model."""

    __tablename__ = "agent_tool_permissions"
    __table_args__ = {"extend_existing": True}

    tool_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_tools.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    permission_level: Mapped[str] = mapped_column(String(50), default="EXECUTE", nullable=False)  # READ, EXECUTE, ADMIN
    conditions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DurableToolCallModel(AEGISBaseModel):
    """Governed tool call lifecycle model adhering to server-authoritative state machine."""

    __tablename__ = "durable_tool_calls"
    __table_args__ = {"extend_existing": True}

    call_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    agent_run_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    tool_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tool_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    arguments_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    sanitized_arguments: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(50), default="VALIDATED", nullable=False)
    authorization_result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    policy_result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(50), default="LOW_RISK", nullable=False)
    approval_status: Mapped[str] = mapped_column(String(50), default="NOT_REQUIRED", nullable=False)
    execution_status: Mapped[str] = mapped_column(String(50), default="REQUESTED", nullable=False)  # Follows 9-stage state machine
    result_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    result_schema_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_information: Mapped[str] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    token_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class ToolCallEventModel(AEGISBaseModel):
    """Tool execution real-time event model for telemetry streams."""

    __tablename__ = "tool_call_events"
    __table_args__ = {"extend_existing": True}

    call_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
