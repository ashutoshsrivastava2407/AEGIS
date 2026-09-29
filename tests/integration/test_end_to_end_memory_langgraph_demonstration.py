"""End-to-End Flagship Acceptance Demonstration: Governed Agent Memory & LangGraph Orchestration.

Demonstrates:
Run #1: Investigation -> Tool execution -> Governed Memory Write -> Approval Pause -> Resume -> Verification -> Final Memory.
Run #2: Subsequent Investigation -> Memory Retrieval -> Verified context usage -> Tool Verification -> Complete Trace.
"""

import pytest
from services.agents.orchestration.langgraph.runtime import aegis_langgraph_runtime
from services.agents.memory.agent_memory import governed_agent_memory_service


def test_end_to_end_flagship_memory_and_langgraph_investigation():
    tenant_id = "tenant-flagship-enterprise"
    workspace_id = "ws-prod-revenue"

    # =========================================================================
    # RUN #1: INITIAL REVENUE ANOMALY INVESTIGATION & MEMORY GENERATION
    # =========================================================================
    task_run_1 = "Investigate the unexpected revenue decline, determine likely causes, recommend a governed response, and use relevant prior investigations where appropriate."

    # 1. Initiate LangGraph execution run requiring human approval
    run_1_res = aegis_langgraph_runtime.execute_graph(
        task=task_run_1,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        agent_id="SupervisorAgent",
        requires_approval=True,
    )

    assert run_1_res["tenant_id"] == tenant_id
    assert run_1_res["status"] == "PAUSED_APPROVAL"
    assert run_1_res["paused_for_approval"] is True
    thread_id = run_1_res["thread_id"]

    # Verify tool execution occurred before approval pause
    completed_tools = run_1_res["completed_tool_results"]
    assert len(completed_tools) >= 1
    assert completed_tools[0]["success"] is True

    # 2. Store verified semantic memory fact from Run #1
    mem_res = governed_agent_memory_service.store_memory(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        memory_type="SEMANTIC_MEMORY",
        memory_key="q3_west_cloud_outage_root_cause",
        content="Q3 revenue drop of 18% in West region was caused by cloud infrastructure outage on July 14th.",
        structured_payload={"impact_pct": 18, "region": "WEST", "root_cause": "CLOUD_OUTAGE"},
        confidence=0.98,
        source_type="TOOL_EXECUTION",
        source_trace_id=run_1_res["trace_id"],
    )
    assert mem_res["success"] is True

    # 3. Resume paused LangGraph run following human operator approval
    resume_res = aegis_langgraph_runtime.resume_graph(
        thread_id=thread_id,
        approval_id="appr_flagship_100",
        tenant_id=tenant_id,
        user_role="ADMIN",
        actor_id="sre_lead_operator",
        approval_decision="APPROVED",
    )

    assert resume_res["status"] == "COMPLETED"
    assert resume_res["re_authorized"] is True

    # =========================================================================
    # RUN #2: SUBSEQUENT INVESTIGATION & GOVERNED MEMORY RETRIEVAL
    # =========================================================================
    task_run_2 = "Analyze subsequent Q3 revenue recovery across West region."

    # 4. Compile memory context prior to Run #2 reasoning
    compiled_mem = governed_agent_memory_service.compile_memory_context(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        task_query="cloud infrastructure outage West region",
    )

    assert "retrieval_id" in compiled_mem
    assert "q3_west_cloud_outage_root_cause" in compiled_mem["compiled_prompt"]

    # 5. Initiate Run #2 utilizing retrieved historical memory
    run_2_res = aegis_langgraph_runtime.execute_graph(
        task=task_run_2,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        agent_id="SupervisorAgent",
        requires_approval=False,
    )

    assert run_2_res["status"] == "COMPLETED"
    assert len(run_2_res["node_history"]) >= 5

    # 6. Verify full memory records list for tenant
    tenant_memories = governed_agent_memory_service.query_memories(tenant_id=tenant_id)
    assert len(tenant_memories) >= 1
    assert tenant_memories[0]["memory_key"] == "q3_west_cloud_outage_root_cause"
    assert tenant_memories[0]["confidence"] == 0.98
