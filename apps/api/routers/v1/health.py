"""Health & Readiness Probe API Endpoints."""

from fastapi import APIRouter
from apps.api.services.health_service import health_service

router = APIRouter(tags=["Health & Probes"])


@router.get("/health/live", summary="Liveness Probe Check")
async def health_live():
    return await health_service.check_liveness()


@router.get("/health/ready", summary="Readiness Probe Check")
async def health_ready():
    return await health_service.check_readiness()
