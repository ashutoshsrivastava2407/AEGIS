"""AI Platform API Endpoints."""

from fastapi import APIRouter, Depends
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI & Agent Platform"])


@router.get("/gateway/status", summary="Get LLM Gateway Operational Status")
async def get_gateway_status(user: UserContext = Depends(get_current_user)):
    data = await ai_service.get_gateway_status(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="LLM Gateway status retrieved successfully"
    )


@router.get("/agents/runs", summary="List Agent Execution Runs")
async def list_agent_runs(user: UserContext = Depends(get_current_user)):
    data = await ai_service.list_agent_runs(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Agent runs retrieved successfully"
    )
