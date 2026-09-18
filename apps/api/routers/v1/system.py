"""System Telemetry API Endpoints."""

from fastapi import APIRouter, Depends
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.system_service import system_service

router = APIRouter(prefix="/system", tags=["System Observability"])


@router.get("/telemetry", summary="Get Node Telemetry & System Metrics")
async def get_telemetry(user: UserContext = Depends(get_current_user)):
    data = await system_service.get_system_telemetry(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="System telemetry retrieved successfully"
    )
