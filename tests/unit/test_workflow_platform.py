"""Unit Test Suite for AEGIS Workflow Platform Services."""

import pytest
import uuid
from datetime import datetime, timezone
from services.workflows.registry import WorkflowRegistry
from services.workflows.validation import WorkflowValidator, RestrictedASTEvaluator, SecurityError
from services.workflows.engine import WorkflowEngine
from services.workflows.scheduler import WorkflowScheduler
from services.workflows.retries import WorkflowRetryEngine
from services.workflows.compensation import WorkflowCompensationEngine
from services.workflows.human_tasks import WorkflowHumanTaskManager
from services.workflows.connectors import GovernedConnectorManager, SecurityError as EgressSecurityError
from services.workflows.recovery import WorkflowRecoveryEngine
from services.workflows.finops import WorkflowFinOpsEngine
from services.workflows.lineage import WorkflowLineageTracer
from services.workflows.observability import WorkflowObservabilityEngine


def test_workflow_registry_creation_and_versioning():
    registry = WorkflowRegistry()
    wf = registry.create_workflow(
        name="Test Workflow",
        description="Automated unit test workflow",
        owner="tester@aegis.enterprise",
    )
    assert wf.status == "DRAFT"
    assert wf.version == 1

    graph = {"nodes": [{"node_key": "step1"}], "edges": []}
    contracts = {"step1": "1.0.0"}
    ver = registry.publish_version(wf, graph, contracts)

    assert wf.status == "ACTIVE"
    assert wf.version == 1
    assert ver.is_active is True
    assert len(ver.definition_fingerprint) == 64


def test_ast_sandbox_evaluator():
    evaluator = RestrictedASTEvaluator()

    # Valid condition evaluation
    ctx = {"cpu": 90, "region": "us-east-1"}
    assert evaluator.evaluate_expression("cpu > 80 and region == 'us-east-1'", ctx) is True
    assert evaluator.evaluate_expression("cpu < 50", ctx) is False

    # Security check: forbidden import/exec
    with pytest.raises(ValueError):
        evaluator.validate_expression("__import__('os').system('ls')")


def test_workflow_validator_dag_cycle():
    validator = WorkflowValidator()
    nodes = [{"node_key": "A"}, {"node_key": "B"}]
    edges = [
        {"source_node_key": "A", "target_node_key": "B"},
        {"source_node_key": "B", "target_node_key": "A"},
    ]
    res = validator.validate_graph(nodes, edges)
    assert res["valid"] is False
    assert any("cycles" in err for err in res["errors"])


def test_worker_lease_fencing_protection():
    engine = WorkflowEngine()
    run = engine.start_workflow_run(
        workflow_id=str(uuid.uuid4()),
        workflow_version_id=str(uuid.uuid4()),
        definition_fingerprint="a" * 64,
        trigger_type="API",
        trigger_payload={"key": "val"},
        worker_id="worker-1",
    )
    assert run.fencing_token == 1
    assert run.worker_id == "worker-1"

    # Valid renewal
    renewed = engine.renew_worker_lease(run, worker_id="worker-1", fencing_token=1)
    assert renewed.fencing_token == 2

    # Stale fencing token rejected
    with pytest.raises(ValueError):
        engine.renew_worker_lease(run, worker_id="worker-1", fencing_token=1)


def test_retry_engine_backoff():
    retry = WorkflowRetryEngine()
    # Permanent error non-retryable
    should, delay, ftype = retry.should_retry(0, {"code": "ACTION_CONTRACT_VALIDATION_FAILED"}, {})
    assert should is False
    assert ftype == "PERMANENT"

    # Transient error retryable
    should, delay, ftype = retry.should_retry(0, {"code": "NETWORK_TIMEOUT", "message": "timed out"}, {"max_retries": 3, "initial_interval_seconds": 2})
    assert should is True
    assert delay >= 2.0


def test_saga_compensation_engine():
    comp = WorkflowCompensationEngine()
    engine = WorkflowEngine()
    run = engine.start_workflow_run("wf1", "ver1", "b" * 64, "API", {}, worker_id="w1")
    nr = engine.create_node_run(run.id, "node1", "ACTION", {})
    nr.status = "COMPLETED"

    nodes_dict = {"node1": {"compensation_node_key": "rollback_node1"}}
    res = comp.execute_compensation(run, [nr], nodes_dict)

    assert res["status"] == "COMPENSATED"
    assert res["compensated_nodes"] == 1


def test_governed_connector_ssrf_and_redaction():
    cm = GovernedConnectorManager()

    # Reject raw password in non_secret_config
    with pytest.raises(ValueError):
        cm.create_connector("DB", "DATABASE", "BASIC", {"password": "secret"}, {}, [])

    # SSRF blocking
    with pytest.raises(Exception):
        cm.validate_egress_url("http://169.254.169.254/latest/meta-data", [])

    # Redaction
    sanitized = cm.sanitize_for_logging({"user": "admin", "api_key": "sec_12345"})
    assert sanitized["api_key"] == "[REDACTED]"
