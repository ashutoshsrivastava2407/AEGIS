"""Test suite for Deployment Release Orchestration, Canary Rollouts & Immutable Rollbacks."""

import pytest
from services.operations.deployments import DeploymentReleaseService


def test_canary_deployment_and_promotion():
    dep_service = DeploymentReleaseService()
    
    dep = dep_service.trigger_deployment(
        service_id="aegis-decision-engine",
        release_version="v2.4.0",
        strategy="CANARY",
        artifact_checksum="sha256-a9b8c7d6e5f4",
        user_role="ENTERPRISE_ADMIN",
    )
    assert dep["status"] == "IN_PROGRESS"
    assert dep["traffic_weight_pct"] == 10

    # Promote to 100% after health gates pass
    promoted = dep_service.promote_deployment(
        deployment_id=dep["id"],
        target_weight_pct=100,
        health_check_passed=True,
    )
    assert promoted["status"] == "PROMOTED"
    assert promoted["traffic_weight_pct"] == 100


def test_immutable_release_rollback():
    dep_service = DeploymentReleaseService()

    # Establish known good baseline
    dep1 = dep_service.trigger_deployment("payment-service", "v1.0.0", strategy="BLUE_GREEN")
    dep_service.promote_deployment(dep1["id"], 100)

    # Deploy new release that fails health gates
    dep2 = dep_service.trigger_deployment("payment-service", "v1.1.0-buggy", strategy="CANARY")
    
    # Execute immutable rollback
    rlb = dep_service.rollback_deployment(
        deployment_id=dep2["id"],
        reason="Elevated 5xx error rate detected during 10% canary window",
    )
    assert rlb["status"] == "COMPLETED"
    assert rlb["restored_release_version"] == "v1.0.0"
    assert rlb["restored_artifact_checksum"] is not None


def test_feature_flag_management():
    dep_service = DeploymentReleaseService()
    
    flag = dep_service.set_feature_flag(
        name="enable_step11_finops",
        enabled=True,
        rollout_percentage=50,
    )
    assert flag["name"] == "enable_step11_finops"
    assert flag["is_enabled"] is True
    assert flag["rollout_percentage"] == 50
