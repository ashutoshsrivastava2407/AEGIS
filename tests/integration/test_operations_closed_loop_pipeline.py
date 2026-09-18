"""AEGIS End-to-End Closed-Loop Production Operations Pipeline Integration Test."""

import pytest
from services.operations.operations_service import ProductionOperationsPlatformService


def test_closed_loop_operations_pipeline():
    """Verify full end-to-end closed-loop operations, governance, resilience, and recovery pipeline."""
    ops = ProductionOperationsPlatformService()
    tenant_id = "tenant-enterprise-prod"
    service_id = "aegis-core-gateway"

    # 1. Register service and evaluate initial 100% readiness
    ops.health.register_service(
        service_id=service_id,
        name="AEGIS Core Gateway",
        owner_team="Platform Operations",
        tier="TIER_1",
        tenant_id=tenant_id,
    )
    readiness = ops.health.evaluate_production_readiness(
        service_id=service_id,
        checklist_evaluations={
            "has_metrics_telemetry": True,
            "has_distributed_tracing": True,
            "has_slo_defined": True,
            "has_runbook": True,
            "has_automated_backups": True,
            "passed_security_audit": True,
            "has_circuit_breakers": True,
            "has_rollback_plan": True,
        },
        tenant_id=tenant_id,
    )
    assert readiness["score"] == 100.0

    # 2. Record distributed trace context and telemetry metrics
    trace_ctx = ops.tracing.create_trace_context(
        tenant_id=tenant_id,
        service=service_id,
        environment="production",
    )
    assert trace_ctx["trace_id"].startswith("trc-")

    for lat in [45.0, 50.0, 55.0, 180.0, 220.0]:
        ops.metrics.record_metric(
            name="http_request_duration_ms",
            value=lat,
            labels={"service": service_id},
            tenant_id=tenant_id,
        )

    # 3. Create SLO and evaluate error budget
    slo = ops.slo.create_slo(
        service_id=service_id,
        name="99.9% Core Gateway Latency SLO",
        metric_name="http_request_duration_ms",
        target_percentage=99.9,
        tenant_id=tenant_id,
    )
    budget = ops.slo.evaluate_error_budget(
        slo_id=slo["id"],
        total_requests=1000,
        failed_requests=15,
        tenant_id=tenant_id,
    )
    assert budget["short_window_burn_rate"] > 0.0

    # 4. Declare SEV1 incident and match operational runbook
    inc = ops.incidents.declare_incident(
        title="Core Gateway High p99 Latency Breach",
        severity="SEV1",
        service_id=service_id,
        summary="p99 latency breached 200ms threshold",
        tenant_id=tenant_id,
    )
    ops.runbooks.register_runbook(
        title="Mitigate Core Gateway Latency Breach",
        service_id=service_id,
        trigger_condition="High p99 Latency Breach",
        steps=[{"step": 1, "action": "RESTART_POD"}],
        automated_remediation_action="RESTART_POD",
        tenant_id=tenant_id,
    )
    matched_runbook = ops.runbooks.match_runbook(service_id, "High p99 Latency Breach", tenant_id=tenant_id)
    assert matched_runbook is not None

    # 5. Execute policy-governed remediation
    rem_evidence = ops.remediation.execute_remediation(
        remediation_action="RESTART_POD",
        target_service_id=service_id,
        parameters={"risk_level": "MEDIUM"},
        incident_id=inc["id"],
        tenant_id=tenant_id,
        user_role="ENTERPRISE_ADMIN",
    )
    assert rem_evidence["policy_decision"] == "ALLOW"
    assert rem_evidence["execution_status"] == "SUCCESS"
    assert rem_evidence["evidence_hash"] is not None

    # 6. Resolve incident and update timeline
    ops.incidents.transition_incident_status(inc["id"], "RESOLVED", actor="AutomatedRemediationEngine", tenant_id=tenant_id)

    # 7. Create disaster recovery backup & verify restore
    bkp = ops.recovery.create_backup(backup_type="FULL", tenant_id=tenant_id)
    rst = ops.recovery.verify_and_trigger_restore(
        backup_id=bkp["id"],
        target_environment="dr-staging",
        tenant_id=tenant_id,
        user_role="ENTERPRISE_ADMIN",
    )
    assert rst["status"] == "COMPLETED"

    # 8. Trigger deployment canary rollout & execute immutable rollback
    dep = ops.deployments.trigger_deployment(
        service_id=service_id,
        release_version="v2.1.0-canary",
        strategy="CANARY",
        tenant_id=tenant_id,
        user_role="ENTERPRISE_ADMIN",
    )
    rlb = ops.deployments.rollback_deployment(
        deployment_id=dep["id"],
        reason="Canary metrics regression",
        tenant_id=tenant_id,
    )
    assert rlb["status"] == "COMPLETED"

    # 9. Record cost event & verify FinOps attribution summary
    ops.finops.record_cost_event(
        service_id=service_id,
        workload_id="gateway-pod-cluster",
        domain="COMPUTE",
        cost_usd=0.50,
        tenant_id=tenant_id,
    )
    finops_summary = ops.finops.get_cost_summary(tenant_id=tenant_id)
    assert finops_summary["total_cost_usd"] > 0.0

    # 10. Platform overview snapshot
    overview = ops.get_operations_overview(tenant_id=tenant_id)
    assert overview["status"] == "OPERATIONAL"
