"""Governance & Policy Control Plane API Endpoints."""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.governance_service import governance_service

router = APIRouter(prefix="/governance", tags=["Governance & Security Control Plane"])


@router.get("/audit", summary="Get Tamper-Evident Hash-Chained Audit Trail")
async def list_audit_trail(user: UserContext = Depends(get_current_user)):
    data = await governance_service.list_audit_trail(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Audit trail retrieved successfully"
    )


@router.get("/policies", summary="Get Active Tenant Governance Policies")
async def get_tenant_policies(user: UserContext = Depends(get_current_user)):
    data = await governance_service.get_tenant_policies(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Tenant policies retrieved successfully"
    )


@router.post("/pipeline/run", summary="Trigger Full End-to-End Governed Pipeline")
async def run_governed_pipeline(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await governance_service.execute_governed_pipeline(payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Governed enterprise pipeline executed successfully"
    )


@router.post("/policies/simulate", summary="Run Non-Mutating Policy Simulator")
async def simulate_policy(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await governance_service.simulate_policy(payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Policy simulation executed successfully"
    )


@router.post("/break-glass", summary="Activate Emergency Break-Glass Session")
async def activate_break_glass(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await governance_service.activate_break_glass(payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Emergency break-glass session activated"
    )
