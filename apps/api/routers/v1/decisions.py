"""Decision Platform API Endpoints."""

from fastapi import APIRouter, Depends, Body, Path
from typing import Dict, Any
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.decision_service import decision_service

router = APIRouter(prefix="/decisions", tags=["Decision Platform"])


@router.get("", summary="List Governed Decision Runs")
async def list_decisions(user: UserContext = Depends(get_current_user)):
    data = await decision_service.list_decisions(user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Decisions retrieved successfully"
    )


@router.post("", summary="Create & Execute Full 14-Stage Decision Pipeline")
async def create_decision(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await decision_service.create_decision(payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Decision pipeline executed successfully"
    )


@router.get("/{decision_id}", summary="Get Decision Details & Manifest Dossier")
async def get_decision(
    decision_id: str = Path(...),
    user: UserContext = Depends(get_current_user)
):
    data = await decision_service.get_decision(decision_id, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Decision details retrieved successfully"
    )


@router.post("/simulation", summary="Run What-If Scenario Simulation")
async def run_simulation(
    parameters: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await decision_service.run_simulation(parameters, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Scenario simulation executed successfully"
    )


@router.post("/{decision_id}/approve", summary="Approve or Reject Decision")
async def approve_decision(
    decision_id: str = Path(...),
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await decision_service.approve_decision(decision_id, payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Decision approval processed successfully"
    )


@router.post("/{decision_id}/execute", summary="Execute Governed Action")
async def execute_action(
    decision_id: str = Path(...),
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await decision_service.execute_action(decision_id, payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Decision action execution completed"
    )


@router.post("/{decision_id}/feedback", summary="Submit Calibration Proposal")
async def submit_feedback(
    decision_id: str = Path(...),
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    data = await decision_service.submit_feedback(decision_id, payload, user)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Feedback calibration proposal submitted successfully"
    )
