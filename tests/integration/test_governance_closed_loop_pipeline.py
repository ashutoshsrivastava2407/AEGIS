"""Integration Test for AEGIS Enterprise Governed Closed-Loop Pipeline."""

import pytest
from services.security.governance_service import EnterpriseGovernancePlatformService


def test_full_governed_enterprise_pipeline_execution():
    service = EnterpriseGovernancePlatformService()
    result = service.run_governed_enterprise_pipeline(
        user_id="integration-admin@aegis.enterprise",
        user_role="ENTERPRISE_ADMIN",
        action="SCALE_SERVICE_WORKERS",
        resource_id="cluster-prod-01",
        data_classification="RESTRICTED",
        tenant_id="default",
    )

    assert result["status"] == "COMPLETED"
    assert result["auth_strength_required"] == "STEP_UP_REQUIRED"
    assert result["authorization"]["authorized"] is True
    assert result["policy_evaluation"]["decision"] == "REQUIRE_APPROVAL"
    assert result["workflow_closed_loop"]["operating_loop"] == "16-STAGE_CANONICAL_CLOSED_LOOP"
    assert result["audit_chain_verified"] is True
    assert result["governance_lineage"]["lineage_depth"] == 7
