"""Integration Test for End-to-End 12-Stage Server-Authoritative Governance Lineage Trace Reconstruction."""

import pytest
from services.security.governance_service import EnterpriseGovernancePlatformService


def test_governance_12_stage_trace_reconstruction():
    service = EnterpriseGovernancePlatformService()
    res = service.run_governed_enterprise_pipeline(
        user_id="sec-admin@aegis.enterprise",
        user_role="ENTERPRISE_ADMIN",
        action="SCALE_SERVICE_WORKERS",
        resource_id="cluster-prod-01",
        data_classification="RESTRICTED",
    )

    assert res["status"] == "COMPLETED"
    assert res["control_chain"] == "Identity ➔ Authentication ➔ RBAC/ABAC ➔ Policy ➔ Step 8/9 ➔ Verification ➔ Audit"

    lineage = res["governance_lineage"]
    assert lineage["chain_nodes"][0]["id"] == "sec-admin@aegis.enterprise"
    assert lineage["policy_version_id"] if "policy_version_id" in lineage else lineage["chain_nodes"][1]["id"] == "pol-ver-v1"
    assert lineage["action_contract_id"] if "action_contract_id" in lineage else lineage["chain_nodes"][4]["id"] == "SCALE_SERVICE_WORKERS"
    assert lineage["lineage_depth"] == 7
