"""Identity Platform REST API Router (Users, Service Identities, Roles)."""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.governance_service import governance_service

router = APIRouter(prefix="/identity", tags=["Identity & Authorization Platform"])


@router.get("/users", summary="List Tenant Users")
async def list_users(user: UserContext = Depends(get_current_user)):
    return APIResponse(
        success=True,
        data=[
            {
                "user_id": user.user_id,
                "email": f"{user.user_id}@aegis.enterprise",
                "tenant_id": user.tenant_id,
                "roles": user.roles,
                "status": "ACTIVE",
            }
        ],
        correlation_id=get_correlation_id(),
        message="Users retrieved successfully"
    )


@router.get("/services", summary="List Non-Human Service Identities")
async def list_service_identities(user: UserContext = Depends(get_current_user)):
    si = governance_service.platform_service.service_identity.create_service_identity(
        name="Workflow Execution Engine",
        identity_type="WORKFLOW",
        description="Non-human service account for workflow execution",
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=[
            {
                "id": si.id,
                "name": si.name,
                "identity_type": si.identity_type,
                "risk_ceiling": si.risk_ceiling,
                "is_active": si.is_active,
            }
        ],
        correlation_id=get_correlation_id(),
        message="Service identities retrieved successfully"
    )


@router.get("/roles", summary="List Security Roles & Capabilities")
async def list_roles(user: UserContext = Depends(get_current_user)):
    roles = governance_service.platform_service.rbac.SYSTEM_ROLES
    return APIResponse(
        success=True,
        data=roles,
        correlation_id=get_correlation_id(),
        message="Security roles retrieved successfully"
    )
