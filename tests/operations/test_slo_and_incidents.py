"""Test suite for SLO Error Budgets & Incident Management Lifecycle."""

import pytest
from services.operations.slo import SLOAndErrorBudgetService
from services.operations.incidents import IncidentManagementService


def test_slo_and_error_budget_burn_rates():
    slo_service = SLOAndErrorBudgetService()
    
    slo = slo_service.create_slo(
        service_id="payment-service",
        name="99.9% Payment Processing Availability",
        metric_name="payment_success_rate",
        target_percentage=99.9,
    )
    assert slo["target_percentage"] == 99.9

    budget = slo_service.evaluate_error_budget(
        slo_id=slo["id"],
        total_requests=100000,
        failed_requests=20,
    )
    assert budget["remaining_budget_percentage"] == 80.0
    assert budget["is_exhausted"] is False
    assert budget["burn_alert_level"] == "NORMAL"


def test_incident_lifecycle_and_timeline():
    inc_service = IncidentManagementService()
    
    # Declare SEV1 incident
    inc = inc_service.declare_incident(
        title="High Database Lock Contention",
        severity="SEV1",
        service_id="db-primary",
        summary="Transaction timeouts spike to 12%",
    )
    assert inc["status"] == "DETECTED"
    assert inc["severity"] == "SEV1"

    # Transition to TRIAGED then INVESTIGATING
    t1 = inc_service.transition_incident_status(inc["id"], "TRIAGED", actor="SRELead")
    assert t1["status"] == "TRIAGED"

    t2 = inc_service.transition_incident_status(inc["id"], "RESOLVED", actor="SRELead")
    assert t2["status"] == "RESOLVED"
    assert t2["resolved_at"] is not None

    details = inc_service.get_incident_details(inc["id"])
    assert details["incident"]["status"] == "RESOLVED"
    assert details["timeline_count"] >= 3  # DECLARED, STATUS_CHANGED, STATUS_CHANGED
