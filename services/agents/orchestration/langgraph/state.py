"""AEGIS Typed LangGraph State Definition."""

from typing import TypedDict, Optional, List, Dict, Any


class AegisGraphState(TypedDict, total=False):
    """Typed State object passed between LangGraph nodes during agent orchestration.

    Contains execution context, correlation IDs, messages, memory context, tool calls,
    decision parameters, approval status, and verification metrics.
    """

    # Multi-tenant & Security Context
    tenant_id: str
    workspace_id: str
    user_role: str
    actor_id: str

    # Identifiers & Tracing
    agent_id: str
    agent_run_id: str
    thread_id: str
    correlation_id: str
    trace_id: str
    graph_id: str

    # Execution State
    task: str
    messages: List[Dict[str, Any]]
    current_node: str
    step_number: int
    node_history: List[str]
    status: str  # INITIALIZED, RUNNING, PAUSED_APPROVAL, RESUMED, COMPLETED, FAILED

    # Domain Subsystem Contexts
    memory_context: Dict[str, Any]
    retrieved_memories: List[Dict[str, Any]]
    available_tools: List[str]
    pending_tool_calls: List[Dict[str, Any]]
    completed_tool_results: List[Dict[str, Any]]

    # Decision, Governance, Approval & Workflow Contexts
    decision_context: Dict[str, Any]
    approval_context: Dict[str, Any]
    workflow_context: Dict[str, Any]
    verification_context: Dict[str, Any]

    # Flags & Controls
    requires_approval: bool
    approval_granted: bool
    approval_id: Optional[str]
    paused_for_approval: bool
    errors: List[str]
    final_output: Optional[Dict[str, Any]]
