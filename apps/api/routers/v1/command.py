"""Command & Executive Overview API Endpoints."""

from fastapi import APIRouter, Depends, Query
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.command_service import command_service

router = APIRouter(prefix="/command", tags=["Command Platform"])


@router.get("/overview", summary="Get Executive Command Overview")
async def get_command_overview(user: UserContext = Depends(get_current_user)):
    data = await command_service.get_overview(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Command overview retrieved successfully"
    )


@router.get("/search", summary="Global System Search")
async def global_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    user: UserContext = Depends(get_current_user)
):
    data = await command_service.global_search(q, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Search executed successfully"
    )
