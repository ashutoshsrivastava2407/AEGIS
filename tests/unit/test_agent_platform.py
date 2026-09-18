"""AEGIS Autonomous Agent Platform Unit Test Suite."""

import pytest
from services.agents.planning.planner import dag_planner, ExecutionPlan
from services.agents.tools.authorization import authorization_engine
from services.agents.tools.tool_registry import tool_registry
from services.agents.tools.executor import tool_executor
from services.agents.orchestration.loop_guard import loop_guard
from services.agents.verification.verification_agent import verification_agent
from services.agents.approvals.approval_engine import approval_engine
from services.agents.evaluation.evaluator import agent_evaluator
from services.agents.registry.agent_registry import agent_registry


def test_dag_planner_decomposition():
    """Verify DAG planner decomposes goal statement into valid acyclic graph."""
    plan: ExecutionPlan = dag_planner.create_plan(
        goal_statement="Investigate revenue drop anomaly in Q3",
        run_id="test_run_001"
    )
    assert plan.plan_id is not None
    assert len(plan.nodes) >= 4
    assert len(plan.execution_order) == len(plan.nodes)
    assert plan.risk_score > 0.0


def test_dag_planner_topological_sort():
    """Verify topological execution sequence respects dependencies."""
    nodes = {
        "step_a": type("Node", (), {"dependencies": []})(),
        "step_b": type("Node", (), {"dependencies": ["step_a"]})(),
    }
    # Planner internal sort check
    order = dag_planner._topological_sort({
        "step_a": type("PlanNode", (), {"dependencies": []})(),
        "step_b": type("PlanNode", (), {"dependencies": ["step_a"]})()
    })
    assert order == ["step_a", "step_b"]


def test_server_side_tool_authorization_allowed():
    """Verify authorized agent type can call read-only tool."""
    res = authorization_engine.authorize_tool_call(
        tool_name="dataset_search",
        params={"query": "sales"},
        agent_type="DATA",
        tenant_id="tenant-a"
    )
    assert res.is_authorized is True
    assert res.risk_tier == "READ_ONLY"
    assert res.sanitized_params["tenant_id"] == "tenant-a"


def test_server_side_tool_authorization_denied():
    """Verify unauthorized agent type cannot invoke restricted tool."""
    res = authorization_engine.authorize_tool_call(
        tool_name="model_predict",
        params={"model_id": "m1", "features_json": {}},
        agent_type="RESEARCH_RAG",  # RAG agent cannot call ML predict tool
        tenant_id="tenant-a"
    )
    assert res.is_authorized is False
    assert "not granted permission" in res.reason


def test_sql_parameter_sanitization_blocks_ddl():
    """Verify server-side authorization blocks destructive SQL statements."""
    res = authorization_engine.authorize_tool_call(
        tool_name="analytical_query",
        params={"sql": "DROP TABLE revenue_tx;"},
        agent_type="SQL",
        tenant_id="tenant-a"
    )
    assert res.is_authorized is False
    assert "illegal DDL/DML keyword" in res.reason


def test_loop_guard_step_limit():
    """Verify loop guard halts runs exceeding maximum step limit."""
    res = loop_guard.evaluate_step(
        run_id="run_overflow",
        current_step=30,  # Max steps is 25
        tool_name="dataset_search",
        params={"query": "test"}
    )
    assert res.allowed is False
    assert "step limit exceeded" in res.reason


def test_loop_guard_repeated_calls():
    """Verify loop guard detects repeated tool calls with identical parameters."""
    run_id = "run_loop_repeat"
    params = {"query": "duplicate"}

    loop_guard.evaluate_step(run_id, 1, "dataset_search", params)
    loop_guard.evaluate_step(run_id, 2, "dataset_search", params)
    loop_guard.evaluate_step(run_id, 3, "dataset_search", params)
    
    # 4th call with same params should be blocked
    res = loop_guard.evaluate_step(run_id, 4, "dataset_search", params)
    assert res.allowed is False
    assert "repeated tool call" in res.reason

    loop_guard.clear_run(run_id)


def test_verification_agent_scoring():
    """Verify independent verification agent evaluates groundedness."""
    res = verification_agent.verify_execution(
        claim="Revenue drop was caused by system maintenance",
        evidence_references=[{"chunk_id": "c1"}],
        dataset_ids=["ds1"],
        deployment_ids=["dep1"]
    )
    assert res.is_verified is True
    assert res.groundedness_score >= 0.70
    assert res.data_quality_passed is True


def test_human_approval_lifecycle():
    """Verify approval request creation, approval, and rejection lifecycle."""
    req = approval_engine.create_approval_request(
        run_id="run_app_01",
        tool_name="workflow_start",
        risk_level="HIGH_RISK",
        requested_action="Trigger automated database rollback"
    )
    assert req.approval_status == "PENDING"

    approved = approval_engine.approve_request(req.approval_id, approved_by="admin_user")
    assert approved.approval_status == "APPROVED"
    assert approved.approved_by == "admin_user"


def test_agent_evaluator_metrics():
    """Verify quantitative evaluator calculates goal and cost scores."""
    metrics = agent_evaluator.evaluate_run(
        run_id="run_eval_01",
        agent_type="SUPERVISOR",
        executed_steps=5,
        is_successful=True,
        groundedness_score=0.95
    )
    assert metrics.goal_completion_score == 1.0
    assert metrics.tool_accuracy_score >= 0.90
    assert metrics.total_cost_usd > 0.0


def test_agent_registry_state_machine():
    """Verify agent lifecycle state transitions."""
    ag = agent_registry.register_agent("Test Agent", "DATA", "Role prompt")
    assert ag.lifecycle_state == "DRAFT"

    ag_val = agent_registry.transition_state(ag.agent_id, "VALIDATED")
    assert ag_val.lifecycle_state == "VALIDATED"

    ag_act = agent_registry.transition_state(ag.agent_id, "ACTIVE")
    assert ag_act.lifecycle_state == "ACTIVE"

    with pytest.raises(ValueError):
        agent_registry.transition_state(ag.agent_id, "DRAFT")  # ACTIVE -> DRAFT invalid
