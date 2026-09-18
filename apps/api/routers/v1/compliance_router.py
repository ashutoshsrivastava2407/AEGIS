"""Compliance Control Plane REST API Router."""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.governance_service import governance_service

router = APIRouter(prefix="/compliance", tags=["Compliance Control Plane"])


@router.get("/frameworks", summary="List Active Compliance Frameworks")
async def list_frameworks(user: UserContext = Depends(get_current_user)):
    return APIResponse(
        success=True,
        data=[
            {"id": "fw-soc2", "name": "SOC 2 Type II", "category": "SECURITY_TRUST", "status": "ACTIVE"},
            {"id": "fw-iso27001", "name": "ISO/IEC 27001:2022", "category": "ISMS", "status": "ACTIVE"},
            {"id": "fw-gdpr", "name": "GDPR Data Protection", "category": "PRIVACY", "status": "ACTIVE"},
        ],
        correlation_id=get_correlation_id(),
        message="Compliance frameworks retrieved successfully"
    )


@router.get("/posture", summary="Get Compliance Posture Score")
async def get_compliance_posture(user: UserContext = Depends(get_current_user)):
    posture = governance_service.platform_service.compliance.evaluate_compliance_posture(
        framework_name="SOC_2",
        active_controls=[{"status": "PASSED"}, {"status": "PASSED"}, {"status": "PASSED"}],
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=posture,
        correlation_id=get_correlation_id(),
        message="Compliance posture score evaluated successfully"
    )


@router.post("/packages/seal", summary="Seal Auditable Evidence Package")
async def seal_audit_package(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    pkg = governance_service.platform_service.evidence_collector.seal_audit_package(
        package_name=payload.get("package_name", "Q3 SOC 2 Audit Evidence Package"),
        framework_id="fw-soc2",
        evidence_ids=payload.get("evidence_ids", ["ev-1", "ev-2"]),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data={
            "package_id": pkg.id,
            "package_name": pkg.package_name,
            "sealed_checksum": pkg.sealed_checksum,
            "status": pkg.status,
            "sealed_at": pkg.sealed_at,
        },
        correlation_id=get_correlation_id(),
        message="Audit package sealed successfully"
    )
