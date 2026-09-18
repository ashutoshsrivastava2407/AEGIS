"""Command & Executive Overview API Endpoints under /api/v1/command."""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from services.command_center import EnterpriseCommandCenterService

router = APIRouter(prefix="/command", tags=["Command Platform"])
command_service = EnterpriseCommandCenterService()


@router.get("/overview", summary="Get Executive Command Overview")
async def get_command_overview(user: UserContext = Depends(get_current_user)):
    data = command_service.get_command_center_overview(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Command overview retrieved successfully"
    )


@router.get("/health", summary="Get Explainable Enterprise Health Status")
async def get_command_health(user: UserContext = Depends(get_current_user)):
    health = command_service.health_aggregator.compute_enterprise_health(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=health,
        correlation_id=get_correlation_id(),
        message="Explainable enterprise health score retrieved"
    )


@router.get("/metrics", summary="Get Time-Series Event & Inference Latency Metrics")
async def get_command_metrics(
    time_range: str = Query("24h", description="Telemetry time window: 1h, 24h, 7d, 30d"),
    user: UserContext = Depends(get_current_user)
):
    metrics = command_service.get_metrics_telemetry(user, time_range=time_range)
    return APIResponse(
        success=True,
        data=metrics,
        correlation_id=get_correlation_id(),
        message="Command telemetry metrics retrieved"
    )


@router.get("/activity", summary="Get Correlated Command Activity Feed")
async def get_command_activity(
    limit: int = Query(15, ge=1, le=100),
    user: UserContext = Depends(get_current_user)
):
    activity = command_service.get_activity_feed(user, limit=limit)
    return APIResponse(
        success=True,
        data=activity,
        correlation_id=get_correlation_id(),
        message="Command activity stream retrieved"
    )


@router.get("/search", summary="Global System Search")
async def global_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(get_current_user)
):
    data = command_service.search_engine.search(query=q, user=user, limit=limit)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Search executed successfully"
    )


@router.get("/readiness", summary="Evaluate Evidence-Backed System Readiness Gate")
async def get_system_readiness(user: UserContext = Depends(get_current_user)):
    readiness = command_service.readiness_gate.evaluate_system_readiness(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=readiness,
        correlation_id=get_correlation_id(),
        message="Production readiness gate evaluated successfully"
    )


@router.get("/trace/{correlation_id}", summary="Reconstruct End-to-End Trace Tree")
async def reconstruct_trace_by_id(
    correlation_id: str,
    user: UserContext = Depends(get_current_user)
):
    tree = command_service.trace_explorer.reconstruct_trace(
        correlation_id=correlation_id,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=tree,
        correlation_id=get_correlation_id(),
        message="End-to-end trace correlation tree reconstructed"
    )
