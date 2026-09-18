"""Action Platform API Endpoints."""

from fastapi import APIRouter, Depends, Path
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.action_service import action_service

router = APIRouter(prefix="/actions", tags=["Action Platform"])


@router.get("", summary="List Governed Action Workflows")
async def list_actions(user: UserContext = Depends(get_current_user)):
    data = await action_service.list_actions(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Actions retrieved successfully"
    )


@router.post("/{action_id}/approve", summary="Approve Action Execution")
async def approve_action(
    action_id: str = Path(...),
    user: UserContext = Depends(get_current_user)
):
    data = await action_service.approve_action(action_id, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Action approved successfully"
    )
