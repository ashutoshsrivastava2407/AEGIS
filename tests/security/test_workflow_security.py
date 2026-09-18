"""Security Test Suite for Worker Lease Fencing, AST Sandbox, Connector Secrets, and SSRF Egress Defense."""

import pytest
import uuid
from services.workflows.engine import WorkflowEngine
from services.workflows.validation import RestrictedASTEvaluator
from services.workflows.connectors import GovernedConnectorManager, SecurityError as EgressSecurityError


def test_stale_worker_lease_fencing_rejection():
    engine = WorkflowEngine()
    run = engine.start_workflow_run(
        workflow_id=str(uuid.uuid4()),
        workflow_version_id=str(uuid.uuid4()),
        definition_fingerprint="c" * 64,
        trigger_type="EVENT",
        trigger_payload={},
        worker_id="worker-01",
    )
    # Valid renewal advances fencing token to 2
    engine.renew_worker_lease(run, worker_id="worker-01", fencing_token=1)

    # Attempted commit by old stale worker with token 1 must be rejected
    assert engine.validate_fencing_token(run, fencing_token=1) is False
    with pytest.raises(ValueError, match="Stale worker fencing token"):
        engine.renew_worker_lease(run, worker_id="worker-01", fencing_token=1)


def test_ast_sandbox_security_rejections():
    evaluator = RestrictedASTEvaluator()

    forbidden_expressions = [
        "__import__('os').system('cat /etc/passwd')",
        "eval('1 + 1')",
        "exec('import sys')",
        "open('/etc/hosts').read()",
    ]

    for expr in forbidden_expressions:
        with pytest.raises(ValueError):
            evaluator.validate_expression(expr)


def test_connector_raw_secret_persistence_prevention():
    cm = GovernedConnectorManager()
    # Cannot store raw secret/token/password in non_secret_config
    with pytest.raises(ValueError, match="Raw sensitive key"):
        cm.create_connector("BadConnector", "HTTP", "BEARER", {"api_token": "secret_123"}, {}, [])


def test_ssrf_egress_defense_blocking():
    cm = GovernedConnectorManager()

    forbidden_urls = [
        "http://127.0.0.1:8080/admin",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost/metrics",
        "http://10.0.0.1/internal",
    ]

    for url in forbidden_urls:
        with pytest.raises(Exception):
            cm.validate_egress_url(url, ["api.aegis.enterprise"])


def test_sensitive_data_log_redaction():
    cm = GovernedConnectorManager()
    data = {
        "event": "login",
        "password": "supersecretpassword",
        "nested": {
            "auth_token": "bearer_abc123",
            "public_id": 42
        }
    }
    redacted = cm.sanitize_for_logging(data)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["auth_token"] == "[REDACTED]"
    assert redacted["nested"]["public_id"] == 42
