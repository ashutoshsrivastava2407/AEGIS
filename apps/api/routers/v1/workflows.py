"""Action & Workflow Automation Platform API Router."""

from fastapi import APIRouter, Depends, Body, Path
from typing import Dict, Any, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.workflow_service import workflow_service

router = APIRouter(prefix="/workflows", tags=["Workflow Automation Platform"])


@router.get("", summary="List Registered Workflows")
async def list_workflows(user: UserContext = Depends(get_current_user)):
    data = await workflow_service.list_workflows(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Workflows retrieved successfully"
    )


@router.post("", summary="Create Workflow Definition")
async def create_workflow(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await workflow_service.create_workflow(payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Workflow created successfully"
    )


@router.post("/runs/closed-loop", summary="Trigger 16-Stage Closed-Loop Execution")
async def trigger_closed_loop(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await workflow_service.execute_closed_loop(payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="16-stage closed loop workflow executed successfully"
    )


@router.get("/runs", summary="List Workflow Execution Runs")
async def list_workflow_runs(user: UserContext = Depends(get_current_user)):
    data = await workflow_service.get_workflow_runs(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Workflow execution runs retrieved successfully"
    )


@router.post("/tasks/{task_id}/submit", summary="Submit Generic Human Task")
async def submit_human_task(
    task_id: str = Path(...),
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await workflow_service.submit_human_task(task_id, payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Human task submitted successfully"
    )


@router.get("/observability/metrics", summary="Get Workflow Operational Metrics")
async def get_metrics(user: UserContext = Depends(get_current_user)):
    data = await workflow_service.get_observability_metrics(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Workflow observability metrics retrieved successfully"
    )
