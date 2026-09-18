"""LLM Gateway REST API Router."""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, Optional, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from services.llm.services import llm_gateway_service
from services.llm.safety.guardrails import ai_guardrails

router = APIRouter(prefix="/llm", tags=["LLM Gateway"])


@router.get("/status", summary="Get LLM Gateway Operational Status")
async def get_gateway_status(user: UserContext = Depends(get_current_user)):
    status_data = llm_gateway_service.get_gateway_status(user.tenant_id)
    return APIResponse(
        success=True,
        data=status_data,
        correlation_id=get_correlation_id(),
        message="LLM Gateway status retrieved successfully"
    )


@router.post("/generate", summary="Execute LLM Gateway Prompt Generation")
async def generate_completion(
    prompt: str = Body(..., embed=True),
    preferred_model: str = Body("aegis-llm-pro", embed=True),
    system_prompt: Optional[str] = Body(None, embed=True),
    user: UserContext = Depends(get_current_user)
):
    res = llm_gateway_service.generate(
        prompt=prompt,
        preferred_model=preferred_model,
        system_prompt=system_prompt,
        tenant_id=user.tenant_id
    )
    return APIResponse(
        success=True,
        data=res,
        correlation_id=get_correlation_id(),
        message="LLM Gateway generation completed"
    )


@router.get("/safety/events", summary="List AI Safety & Guardrail Events")
async def list_safety_events(user: UserContext = Depends(get_current_user)):
    events = ai_guardrails.list_events(user.tenant_id)
    return APIResponse(
        success=True,
        data=events,
        correlation_id=get_correlation_id(),
        message="AI safety events retrieved successfully"
    )
