"""Test suite for Resilience Controls (Circuit Breaker, Rate Limiter) & Policy-Governed Remediation."""

import pytest
from services.operations.circuit_breaker import CircuitBreakerAndResilienceService
from services.operations.remediation import PolicyGovernedRemediationService


def test_circuit_breaker_state_transitions():
    resilience = CircuitBreakerAndResilienceService()
    cb_name = "test-db-pool"

    # Initially CLOSED
    assert resilience.check_circuit(cb_name) is True

    # Record 5 consecutive failures to trip circuit
    for _ in range(5):
        resilience.record_circuit_outcome(cb_name, success=False)

    # Circuit should now be OPEN (rejecting requests)
    status = resilience.record_circuit_outcome(cb_name, success=False)
    assert status["state"] == "OPEN"
    assert resilience.check_circuit(cb_name) is False


def test_token_bucket_rate_limiter():
    resilience = CircuitBreakerAndResilienceService()
    key = "user-api-limiter"

    # Consume 5 tokens out of capacity 5
    for _ in range(5):
        assert resilience.check_rate_limit(key, capacity=5, refill_rate_per_sec=0.1) is True

    # 6th request should be rate-limited
    assert resilience.check_rate_limit(key, capacity=5, refill_rate_per_sec=0.1) is False


def test_backpressure_and_load_shedding():
    resilience = CircuitBreakerAndResilienceService()
    
    # 50% depth -> normal
    eval1 = resilience.evaluate_backpressure(current_queue_depth=500, max_capacity=1000)
    assert eval1["should_shed_load"] is False
    assert eval1["action"] == "PROCESS_NORMAL"

    # 90% depth -> shed traffic
    eval2 = resilience.evaluate_backpressure(current_queue_depth=900, max_capacity=1000)
    assert eval2["should_shed_load"] is True
    assert eval2["action"] == "SHED_TRAFFIC"


def test_policy_governed_remediation_execution():
    rem_service = PolicyGovernedRemediationService()

    # Allowed remediation execution
    res = rem_service.execute_remediation(
        remediation_action="RESTART_SERVICE",
        target_service_id="aegis-api",
        parameters={"risk_level": "MEDIUM"},
        user_role="ENTERPRISE_ADMIN",
    )
    assert res["policy_decision"] == "ALLOW"
    assert res["execution_status"] == "SUCCESS"
    assert res["evidence_hash"] is not None
    assert len(res["evidence_hash"]) == 64  # SHA-256 hex string

    # High risk action blocked for non-admin user
    blocked = rem_service.execute_remediation(
        remediation_action="DRAIN_CLUSTER",
        target_service_id="aegis-cluster",
        parameters={"risk_level": "CRITICAL"},
        user_role="READONLY_USER",
    )
    assert blocked["policy_decision"] == "DENY"
    assert blocked["execution_status"] == "BLOCKED_BY_POLICY"
