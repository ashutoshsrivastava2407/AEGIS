"""Test suite for Explainable Enterprise Health Aggregator & Authorized Global Search."""

import pytest
from packages.security import UserContext
from services.command_center.health_aggregator import ExplainableEnterpriseHealthAggregator
from services.command_center.search import GlobalEnterpriseSearchEngine


def test_explainable_enterprise_health_computation():
    agg = ExplainableEnterpriseHealthAggregator()
    
    # Partial telemetry input
    inputs = {
        "availability": {"score": 100.0, "status": "HEALTHY", "evidence": ["All services responding"]},
        "slo_compliance": {"score": 99.9, "status": "HEALTHY", "evidence": ["SLO burn rate nominal"]},
        "finops": {"score": 90.0, "status": "HEALTHY", "evidence": ["Cost within monthly budget"]},
    }

    health = agg.compute_enterprise_health(telemetry_inputs=inputs)
    assert health["calculation_version"] == "AEGIS_Health_v1.0"
    assert health["overall_status"] == "HEALTHY"
    assert health["health_score"] > 90.0
    assert "availability" in health["contributing_dimensions"]
    assert "finops" in health["contributing_dimensions"]
    assert len(health["underlying_evidence"]["availability"]) > 0
    # Subsystems missing from input are noted as unavailable
    assert isinstance(health["unavailable_dimensions"], list)


def test_authorized_global_enterprise_search():
    search_engine = GlobalEnterpriseSearchEngine()
    
    admin_user = UserContext(user_id="usr-admin", tenant_id="tenant-alpha", username="admin", email="admin@aegis.org", roles=["ENTERPRISE_ADMIN"])
    standard_user = UserContext(user_id="usr-std", tenant_id="tenant-alpha", username="user", email="user@aegis.org", roles=["USER"])
    other_tenant_user = UserContext(user_id="usr-other", tenant_id="tenant-beta", username="other", email="other@aegis.org", roles=["ENTERPRISE_ADMIN"])

    # 1. Admin search retrieves admin-only compliance document
    admin_res = search_engine.search(query="SOC 2", user=admin_user)
    assert admin_res["total_results"] >= 1
    assert any(r["id"] == "doc-sec-audit" for r in admin_res["results"])

    # 2. Standard user search filters out admin-only document (Zero Entity Existence Leakage)
    std_res = search_engine.search(query="SOC 2", user=standard_user)
    assert not any(r["id"] == "doc-sec-audit" for r in std_res["results"])

    # 3. Cross-tenant user search returns zero results for tenant-alpha assets
    other_res = search_engine.search(query="Revenue", user=other_tenant_user)
    assert not any(r["id"] == "ds-gold-rev" for r in other_res["results"])
