"""Test suite for End-to-End Trace Explorer & Whole-System Production Readiness Gate."""

import pytest
from services.command_center.trace_explorer import EndToEndTraceExplorer
from services.command_center.readiness_gate import WholeSystemProductionReadinessGate


def test_trace_explorer_correlation_reconstruction():
    explorer = EndToEndTraceExplorer()
    
    trace = explorer.reconstruct_trace(correlation_id="corr-test-100", trace_id="trc-test-100")
    assert trace["correlation_id"] == "corr-test-100"
    assert trace["trace_id"] == "trc-test-100"
    assert trace["node_count"] >= 5
    assert trace["causality_chain_intact"] is True


def test_whole_system_production_readiness_gate():
    gate = WholeSystemProductionReadinessGate()
    
    readiness = gate.evaluate_system_readiness(tenant_id="tenant-alpha")
    assert readiness["overall_status"] == "READY_FOR_PRODUCTION"
    assert readiness["readiness_score"] == 100.0
    assert readiness["dimensions_evaluated_count"] == 19
    assert readiness["is_production_ready"] is True
