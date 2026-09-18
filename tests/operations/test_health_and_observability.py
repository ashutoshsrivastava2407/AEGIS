"""Test suite for Service Health, Readiness & Observability (Metrics/Tracing)."""

import pytest
from services.operations.health import HealthAndReadinessService
from services.operations.metrics import MetricsAggregationService
from services.operations.tracing import UniversalTraceContextService


def test_health_probes():
    service = HealthAndReadinessService()
    
    liveness = service.get_liveness_status()
    assert liveness["status"] == "HEALTHY"
    assert liveness["probe"] == "liveness"
    
    readiness = service.get_readiness_status()
    assert readiness["status"] == "READY"
    assert readiness["probe"] == "readiness"
    assert "database" in readiness["components"]

    startup = service.get_startup_status()
    assert startup["status"] == "STARTED"


def test_service_catalog_and_readiness_checklist():
    service = HealthAndReadinessService()
    
    srv = service.register_service(
        service_id="srv-test-1",
        name="Test Ingestion Gateway",
        owner_team="Data Platform",
        tier="TIER_1",
    )
    assert srv["service_id"] == "srv-test-1"
    assert srv["tier"] == "TIER_1"

    services = service.list_services()
    assert any(s["service_id"] == "srv-test-1" for s in services)

    # Production readiness checklist
    readiness = service.evaluate_production_readiness(
        service_id="srv-test-1",
        checklist_evaluations={
            "has_metrics_telemetry": True,
            "has_distributed_tracing": True,
            "has_slo_defined": True,
            "has_runbook": True,
            "has_automated_backups": True,
            "passed_security_audit": True,
            "has_circuit_breakers": True,
            "has_rollback_plan": True,
        }
    )
    assert readiness["score"] == 100.0
    assert readiness["is_ready"] is True


def test_metrics_percentiles_aggregation():
    metrics = MetricsAggregationService()
    
    # Record series of latency measurements
    for val in range(1, 101):
        metrics.record_metric("test_latency_ms", float(val), labels={"service": "test-api"})

    summary = metrics.get_metrics_summary("test_latency_ms", service="test-api")
    assert summary["count"] == 100
    assert summary["min"] == 1.0
    assert summary["max"] == 100.0
    assert 45.0 <= summary["p50"] <= 55.0
    assert 85.0 <= summary["p90"] <= 95.0
    assert 90.0 <= summary["p95"] <= 98.0
    assert summary["p99"] >= 98.0


def test_universal_trace_context_propagation():
    tracing = UniversalTraceContextService()
    
    ctx = tracing.create_trace_context(
        tenant_id="tenant-100",
        service="order-service",
        environment="production",
    )
    assert ctx["tenant_id"] == "tenant-100"
    assert ctx["trace_id"].startswith("trc-")
    assert ctx["span_id"].startswith("spn-")

    headers = tracing.inject_http_headers(ctx)
    assert headers["X-Tenant-Id"] == "tenant-100"
    assert "traceparent" in headers

    extracted = tracing.extract_http_headers(headers)
    assert extracted["tenant_id"] == "tenant-100"
