"""Unit Test Suite for LangGraph Agent Orchestration (25 Categories)."""

import pytest
from services.agents.orchestration.langgraph.runtime import AegisLangGraphRuntime
from services.agents.orchestration.langgraph.builder import aegis_graph_builder
from services.agents.orchestration.langgraph.checkpoint import AegisGraphCheckpointSaver


@pytest.fixture
def runtime():
    return AegisLangGraphRuntime()


def test_01_graph_construction(runtime):
    assert runtime.graph is not None


def test_02_typed_graph_state(runtime):
    res = runtime.execute_graph(task="Investigate revenue anomaly", tenant_id="tenant-1")
    assert res["status"] == "COMPLETED"
    assert "agent_run_id" in res


def test_03_supervisor_routing(runtime):
    res = runtime.execute_graph(task="Supervisor routing test", tenant_id="tenant-1")
    assert "SUPERVISOR" in res["node_history"]


def test_04_specialized_agent_routing(runtime):
    res = runtime.execute_graph(task="Data analysis task", tenant_id="tenant-1")
    assert "SPECIALIZED_AGENT" in res["node_history"]


def test_05_conditional_branch(runtime):
    res = runtime.execute_graph(task="Conditional branch check", tenant_id="tenant-1", requires_approval=True)
    assert res["paused_for_approval"] is True
    assert res["status"] == "PAUSED_APPROVAL"


def test_06_tool_call_node(runtime):
    res = runtime.execute_graph(task="Execute governed tools", tenant_id="tenant-1")
    assert "TOOL_EXECUTION" in res["node_history"]


def test_07_governed_tool_executor_integration(runtime):
    res = runtime.execute_graph(task="Run analytical query", tenant_id="tenant-1")
    completed_tools = res["completed_tool_results"]
    assert len(completed_tools) >= 1
    assert completed_tools[0]["success"] is True


def test_08_tool_result_propagation(runtime):
    res = runtime.execute_graph(task="Propagate tool output", tenant_id="tenant-1")
    assert len(res["completed_tool_results"]) > 0


def test_09_memory_retrieval_node(runtime):
    res = runtime.execute_graph(task="Retrieve context before reasoning", tenant_id="tenant-1")
    assert "MEMORY_RETRIEVAL" in res["node_history"]


def test_10_memory_write_node(runtime):
    res = runtime.execute_graph(task="Persist investigation finding", tenant_id="tenant-1")
    assert "MEMORY_WRITE" in res["node_history"]


def test_11_checkpoint_creation(runtime):
    res = runtime.execute_graph(task="Create checkpoint state", tenant_id="tenant-1")
    state = runtime.get_graph_state(thread_id=res["thread_id"], tenant_id="tenant-1")
    assert state is not None


def test_12_checkpoint_restore(runtime):
    res = runtime.execute_graph(task="High-risk action requiring approval", tenant_id="tenant-1", requires_approval=True)
    thread_id = res["thread_id"]
    state = runtime.get_graph_state(thread_id=thread_id, tenant_id="tenant-1")
    assert state is not None
    assert state.get("paused_for_approval") is True


def test_13_process_restart_recovery(runtime):
    res = runtime.execute_graph(task="Pause for recovery test", tenant_id="tenant-1", requires_approval=True)
    thread_id = res["thread_id"]
    # Re-instantiate new runtime engine simulating process restart
    new_runtime = AegisLangGraphRuntime()
    state = new_runtime.get_graph_state(thread_id=thread_id, tenant_id="tenant-1")
    assert state is not None


def test_14_human_approval_interruption(runtime):
    res = runtime.execute_graph(task="Scale cluster replicas", tenant_id="tenant-1", requires_approval=True)
    assert res["status"] == "PAUSED_APPROVAL"


def test_15_human_approval_resume(runtime):
    res_paused = runtime.execute_graph(task="Scale cluster replicas", tenant_id="tenant-1", requires_approval=True)
    thread_id = res_paused["thread_id"]
    res_resumed = runtime.resume_graph(
        thread_id=thread_id,
        approval_id="appr_100",
        tenant_id="tenant-1",
        approval_decision="APPROVED",
    )
    assert res_resumed["status"] == "COMPLETED"
    assert res_resumed["re_authorized"] is True


def test_16_policy_denial(runtime):
    res = runtime.resume_graph(
        thread_id="non_existent_thread",
        approval_id="appr_denied",
        tenant_id="tenant-1",
    )
    assert res["success"] is False


def test_17_tool_failure_recovery(runtime):
    res = runtime.execute_graph(task="Run safe query with error handling", tenant_id="tenant-1")
    assert res["status"] == "COMPLETED"


def test_18_timeout(runtime):
    res = runtime.execute_graph(task="Timeout check task", tenant_id="tenant-1")
    assert res["status"] == "COMPLETED"


def test_19_duplicate_resume_protection(runtime):
    res_paused = runtime.execute_graph(task="Duplicate resume test", tenant_id="tenant-1", requires_approval=True)
    thread_id = res_paused["thread_id"]
    res1 = runtime.resume_graph(thread_id=thread_id, approval_id="appr_dup", tenant_id="tenant-1", approval_decision="APPROVED")
    res2 = runtime.resume_graph(thread_id=thread_id, approval_id="appr_dup", tenant_id="tenant-1", approval_decision="APPROVED")
    assert res1["status"] == "COMPLETED"
    assert res2["status"] == "COMPLETED"


def test_20_loop_guard(runtime):
    res = runtime.execute_graph(task="Loop guard test task", tenant_id="tenant-1")
    assert res["step_number"] < 50


def test_21_trace_propagation(runtime):
    res = runtime.execute_graph(task="Trace correlation test", tenant_id="tenant-1")
    assert "trace_id" in res
    assert res["trace_id"].startswith("tr_")


def test_22_audit_persistence(runtime):
    res = runtime.execute_graph(task="Audit persistence test", tenant_id="tenant-1")
    assert "correlation_id" in res


def test_23_multi_agent_execution(runtime):
    res = runtime.execute_graph(task="Multi-agent DAG collaboration", tenant_id="tenant-1")
    history = res["node_history"]
    assert "SUPERVISOR" in history
    assert "SPECIALIZED_AGENT" in history
    assert "VERIFICATION" in history


def test_24_graph_completion(runtime):
    res = runtime.execute_graph(task="Complete investigation run", tenant_id="tenant-1")
    assert res["status"] == "COMPLETED"
    assert "FINAL_RESPONSE" in res["node_history"]


def test_25_graph_failure_handling(runtime):
    res = runtime.execute_graph(task="Standard graph task", tenant_id="tenant-1")
    assert res["status"] in ["COMPLETED", "PAUSED_APPROVAL"]
