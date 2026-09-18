"""Agent Execution Step, Tool Execution, Policy Decision, and Trace Event Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class AgentStepModel(AEGISBaseModel):
    """Agent execution step trace model."""

    __tablename__ = "agent_steps"

    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # THINK, TOOL_CALL, PLAN, VERIFY, HANDOFF
    rationale_summary: Mapped[str] = mapped_column(Text, nullable=True)
    decision_factors_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    evidence_references_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    tool_results_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    verification_results_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    policy_results_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    assumptions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    constraints_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    action_summary: Mapped[str] = mapped_column(Text, nullable=True)
    outcome_summary: Mapped[str] = mapped_column(Text, nullable=True)
    input_payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    step_status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class AgentToolExecutionModel(AEGISBaseModel):
    """Governed tool execution record model."""

    __tablename__ = "agent_tool_executions"

    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    input_arguments_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    execution_status: Mapped[str] = mapped_column(String(50), default="SUCCESS", nullable=False)  # SUCCESS, DENIED, FAILED, TIMED_OUT
    risk_tier: Mapped[str] = mapped_column(String(50), default="LOW_RISK", nullable=False)
    is_authorized: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    authorization_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class AgentPolicyDecisionModel(AEGISBaseModel):
    """Policy decision audit model."""

    __tablename__ = "agent_policy_decisions"

    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)  # ALLOW, DENY, REQUIRE_APPROVAL, REWRITE
    evaluated_context_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)


class AgentTraceEventModel(AEGISBaseModel):
    """Real-time observability trace event model."""

    __tablename__ = "agent_trace_events"

    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
