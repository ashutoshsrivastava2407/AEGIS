"""Data Platform Comprehensive REST API Router."""

from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from typing import Optional, Dict, Any
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.data_service import data_service

router = APIRouter(prefix="/data", tags=["Data Platform"])


@router.post("/sources", summary="Register Tenant Data Source")
async def register_source(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    name = payload.get("name")
    source_type = payload.get("source_type")
    config = payload.get("config", {})

    if not name or not source_type:
        raise HTTPException(status_code=400, detail="Fields 'name' and 'source_type' are required")

    try:
        data = await data_service.register_source(name, source_type, config, user)
        return APIResponse(
            success=True,
            data=data,
            correlation_id=get_correlation_id(),
            message="Data source registered successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sources", summary="List Registered Data Sources")
async def list_sources(user: UserContext = Depends(get_current_user)):
    data = await data_service.list_sources(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Data sources retrieved successfully"
    )


@router.post("/sources/{source_id}/test", summary="Test Source Connectivity")
async def test_source(
    source_id: str = Path(...),
    user: UserContext = Depends(get_current_user)
):
    try:
        data = await data_service.test_source(source_id, user)
        return APIResponse(
            success=True,
            data=data,
            correlation_id=get_correlation_id(),
            message="Connection test completed"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/ingestions", summary="Trigger Ingestion Pipeline Run")
async def trigger_ingestion(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    source_id = payload.get("source_id")
    gold_transform = payload.get("gold_transform")

    if not source_id:
        raise HTTPException(status_code=400, detail="Field 'source_id' is required")

    try:
        data = await data_service.trigger_ingestion(source_id, user, gold_transform)
        return APIResponse(
            success=True,
            data=data,
            correlation_id=get_correlation_id(),
            message="Ingestion pipeline executed successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ingestions", summary="List Ingestion Execution Job Runs")
async def list_jobs(user: UserContext = Depends(get_current_user)):
    data = await data_service.list_jobs(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Ingestion job runs retrieved successfully"
    )


@router.get("/datasets", summary="List Catalog Datasets")
async def list_datasets(
    layer: Optional[str] = Query(None, description="Medallion layer filter (ALL, BRONZE, SILVER, GOLD)"),
    user: UserContext = Depends(get_current_user)
):
    data = await data_service.list_datasets(layer, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Datasets retrieved successfully"
    )


@router.get("/datasets/{dataset_id}/quality", summary="Get Dataset Data Health Score & Quality Checks")
async def get_dataset_quality(
    dataset_id: str = Path(...),
    user: UserContext = Depends(get_current_user)
):
    data = await data_service.get_dataset_quality(dataset_id, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Dataset quality report retrieved successfully"
    )


@router.get("/datasets/{resource_id}/lineage", summary="Get Resource Lineage DAG Graph")
async def get_lineage(
    resource_id: str = Path(...),
    user: UserContext = Depends(get_current_user)
):
    data = await data_service.get_lineage(resource_id, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Lineage DAG retrieved successfully"
    )


@router.get("/quarantine", summary="Inspect Quarantined Rejected Records")
async def list_quarantine(user: UserContext = Depends(get_current_user)):
    data = await data_service.list_quarantine(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Quarantined records retrieved successfully"
    )
