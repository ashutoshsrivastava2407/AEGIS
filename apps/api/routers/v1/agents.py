"""AEGIS Autonomous Agent Platform REST API Router.

Exposes REST endpoints for agent catalog, tool platform, goal execution runs,
human-in-the-loop approval gates, trace events, and evaluation metrics.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.agents.services import agent_platform_service

router = APIRouter(prefix="/agents", tags=["agents"])

DEFAULT_TENANT_ID = "tenant-aegis-primary"


# Request / Response Schemas
class CreateAgentRequest(BaseModel):
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Agent type identifier")
    role_prompt: str = Field(..., description="Agent role system prompt")
    description: str = Field("", description="Agent description")
    risk_profile: str = Field("MEDIUM_RISK", description="Risk profile")


class StateTransitionRequest(BaseModel):
    new_state: str = Field(..., description="Target lifecycle state (e.g. ACTIVE, SUSPENDED)")


class ExecuteRunRequest(BaseModel):
    goal: str = Field(..., description="Enterprise intelligence goal or investigation prompt")
    agent_type: str = Field("SUPERVISOR", description="Target starting agent type")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional execution context")


class ApprovalActionRequest(BaseModel):
    operator: str = Field("admin", description="Operator identity performing approval/rejection")
    comments: str = Field("", description="Operational comments")


@router.get("/overview")
def get_agents_overview(tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
    """Retrieve Agent Platform executive summary metrics."""
    agents = agent_platform_service.list_agents()
    tools = agent_platform_service.list_tools()
    approvals = agent_platform_service.list_pending_approvals()

    return {
        "platform_status": "ACTIVE",
        "total_agents": len(agents),
        "active_agents": len([a for a in agents if a["lifecycle_state"] == "ACTIVE"]),
        "total_governed_tools": len(tools),
        "pending_human_approvals": len(approvals),
        "supported_agent_types": [
            "SUPERVISOR", "DATA", "SQL", "RESEARCH_RAG", "ML",
            "INVESTIGATION", "FORECASTING", "DECISION", "EXECUTION", "VERIFICATION"
        ]
    }


@router.get("/catalog")
def list_agents(
    lifecycle_state: Optional[str] = None,
    agent_type: Optional[str] = None
) -> Dict[str, Any]:
    """List registered agent definitions in catalog."""
    agents = agent_platform_service.list_agents(lifecycle_state, agent_type)
    return {"agents": agents, "total": len(agents)}


@router.post("/catalog", status_code=status.HTTP_201_CREATED)
def create_agent(payload: CreateAgentRequest) -> Dict[str, Any]:
    """Register new agent entity in DRAFT state."""
    return agent_platform_service.create_agent(
        name=payload.name,
        agent_type=payload.agent_type,
        role_prompt=payload.role_prompt,
        description=payload.description,
        risk_profile=payload.risk_profile
    )


@router.post("/catalog/{agent_id}/transition")
def transition_agent_state(agent_id: str, payload: StateTransitionRequest) -> Dict[str, Any]:
    """Transition agent lifecycle state."""
    try:
        return agent_platform_service.transition_agent_state(agent_id, payload.new_state)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


@router.get("/tools")
def list_tools(category: Optional[str] = None, risk_tier: Optional[str] = None) -> Dict[str, Any]:
    """List governed platform tools."""
    tools = agent_platform_service.list_tools(category, risk_tier)
    return {"tools": tools, "total": len(tools)}


@router.post("/runs", status_code=status.HTTP_201_CREATED)
def execute_agent_run(payload: ExecuteRunRequest, tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
    """Trigger an autonomous agent execution pipeline."""
    return agent_platform_service.execute_agent_run(
        goal=payload.goal,
        agent_type=payload.agent_type,
        tenant_id=tenant_id,
        context=payload.context
    )


@router.get("/approvals")
def list_pending_approvals(run_id: Optional[str] = None) -> Dict[str, Any]:
    """List pending human approval requests."""
    approvals = agent_platform_service.list_pending_approvals(run_id)
    return {"approvals": approvals, "total": len(approvals)}


@router.post("/approvals/{approval_id}/approve")
def approve_action(approval_id: str, payload: ApprovalActionRequest) -> Dict[str, Any]:
    """Approve a pending high-risk action request."""
    try:
        return agent_platform_service.approve_action(approval_id, payload.operator, payload.comments)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.post("/approvals/{approval_id}/reject")
def reject_action(approval_id: str, payload: ApprovalActionRequest) -> Dict[str, Any]:
    """Reject a pending high-risk action request."""
    try:
        return agent_platform_service.reject_action(approval_id, payload.operator, payload.comments)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))
