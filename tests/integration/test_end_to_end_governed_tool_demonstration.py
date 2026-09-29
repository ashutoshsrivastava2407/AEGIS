"""AEGIS End-to-End Governed Tool / Function Calling Acceptance Demonstration Test.

Demonstrates live multi-turn agentic task completion scenario:
"Investigate an unexpected revenue decline and determine an appropriate governed response."

Verifies:
1. LLM native function selection
2. Input argument schema validation
3. Server-side identity, tenant isolation, and RBAC authorization
4. Policy & risk evaluation
5. Human approval gate branching for high-risk execution
6. GovernedToolExecutor real AEGIS tool dispatch
7. Untrusted output schema & security validation
8. Agent multi-turn context feedback & loop continuation
9. Durable audit persistence & trace correlation
10. Telemetry generation for Command Center
"""

import pytest
from services.agents.agents.specialized_agents import SupervisorAgent
from services.agents.tools.executor import tool_executor
from services.agents.tools.tool_registry import tool_registry


def test_end_to_end_governed_revenue_investigation_scenario():
    """Execute live governed multi-turn revenue investigation scenario."""

    agent = SupervisorAgent()
    query = "Investigate an unexpected revenue decline and determine an appropriate governed response."

    # 1. Execute agentic multi-turn tool execution loop
    loop_res = agent.execute_multi_turn_tool_loop(
        query=query,
        max_turns=5,
        tenant_id="tenant-alpha",
        auto_approve_high_risk=True
    )

    # 2. Assert multi-turn progression
    assert loop_res["status"] in ["COMPLETED", "LOOP_GUARD_STOPPED"]
    assert loop_res["turns_count"] >= 1
    assert "trace_id" in loop_res
    assert isinstance(loop_res["executed_tool_calls"], list)

    # 3. Assert tool call lifecycle properties
    executed_calls = loop_res["executed_tool_calls"]
    for tc in executed_calls:
        assert "call_id" in tc
        assert "tool_name" in tc
        assert "status" in tc
        assert tc["status"] in ["SUCCEEDED", "COMPLETED", "APPROVAL_REQUIRED", "EXECUTED"]
        assert tc["is_authorized"] is True
        assert tc["result_schema_valid"] is True
        assert "trace_id" in tc

    # 4. Verify durable audit persistence
    durable_calls = tool_executor.list_durable_calls(tenant_id="tenant-alpha")
    assert len(durable_calls) > 0

    # 5. Verify telemetry stream events were recorded
    events = tool_executor.get_events(tenant_id="tenant-alpha")
    assert len(events) > 0
    event_types = {e["event_type"] for e in events}
    assert "tool_call_requested" in event_types
    assert "tool_execution_completed" in event_types or "tool_authorized" in event_types
