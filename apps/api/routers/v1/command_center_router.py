"""Enterprise Command Center & Continuous Learning REST API Router."""

from fastapi import APIRouter, Depends, Body, Query
from typing import Dict, Any, List, Optional
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse

from services.command_center import EnterpriseCommandCenterService
from services.learning import ContinuousLearningService

router = APIRouter(prefix="", tags=["Enterprise Command Center & Learning"])
command_service = EnterpriseCommandCenterService()
learning_service = ContinuousLearningService()


# --- GLOBAL SEARCH & CONTINUOUS LEARNING ---

@router.get("/search", summary="Execute Authorized Global Enterprise Search")
async def global_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(get_current_user)
):
    res = command_service.search_engine.search(query=q, user=user, limit=limit)
    return APIResponse(
        success=True,
        data=res,
        correlation_id=get_correlation_id(),
        message="Global enterprise search executed"
    )


# --- CONTINUOUS LEARNING ---

@router.get("/learning/signals", summary="List Operational Learning Signals")
async def list_learning_signals(
    dimension: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    user: UserContext = Depends(get_current_user)
):
    signals = learning_service.signals.list_signals(
        dimension=dimension,
        severity=severity,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=signals,
        correlation_id=get_correlation_id(),
        message="Operational learning signals retrieved"
    )


@router.post("/learning/signals", summary="Record Learning Signal")
async def record_learning_signal(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    sig = learning_service.signals.record_signal(
        dimension=payload.get("dimension", "OPERATIONS"),
        signal_type=payload.get("signal_type", "REMEDIATION_EFFICACY"),
        source_component=payload.get("source_component", "RemediationEngine"),
        payload=payload.get("payload", {}),
        severity=payload.get("severity", "MEDIUM"),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=sig,
        correlation_id=get_correlation_id(),
        message="Learning signal recorded successfully"
    )


@router.get("/learning/candidates", summary="List Governed Improvement Candidates")
async def list_improvement_candidates(
    subsystem: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    user: UserContext = Depends(get_current_user)
):
    candidates = learning_service.lifecycle.list_candidates(
        target_subsystem=subsystem,
        status=status,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=candidates,
        correlation_id=get_correlation_id(),
        message="Governed improvement candidates retrieved"
    )


@router.post("/learning/candidates", summary="Propose Improvement Candidate")
async def propose_improvement_candidate(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    cand = learning_service.lifecycle.propose_candidate(
        title=payload.get("title", "Optimize Vector Search Top-K Reranking"),
        target_subsystem=payload.get("target_subsystem", "RAG"),
        description=payload.get("description", "Improve retrieval precision by tuning cross-encoder weights."),
        proposal=payload.get("proposal", {}),
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=cand,
        correlation_id=get_correlation_id(),
        message="Improvement candidate proposed successfully"
    )


@router.post("/learning/candidates/{candidate_id}/transition", summary="Transition Governed Improvement Candidate Stage")
async def transition_candidate_stage(
    candidate_id: str,
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    cand = learning_service.lifecycle.transition_candidate(
        candidate_id=candidate_id,
        target_status=payload.get("target_status", "APPROVED"),
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        user_role=user.roles[0] if user.roles else "ENTERPRISE_ADMIN",
    )
    return APIResponse(
        success=True,
        data=cand,
        correlation_id=get_correlation_id(),
        message="Improvement candidate stage transitioned"
    )


# --- OUTCOME ATTRIBUTION ---

@router.post("/outcomes/attribute", summary="Attribute Outcome via AEGIS_DiD_v1.0")
async def attribute_outcome(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    obs = learning_service.attribution.attribute_outcome(
        action_id=payload.get("action_id", "act-001"),
        treatment_pre_avg=payload.get("treatment_pre_avg", 100.0),
        treatment_post_avg=payload.get("treatment_post_avg", 80.0),
        control_pre_avg=payload.get("control_pre_avg", 100.0),
        control_post_avg=payload.get("control_post_avg", 95.0),
        decision_id=payload.get("decision_id"),
        sample_size=payload.get("sample_size", 1000),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=obs,
        correlation_id=get_correlation_id(),
        message="Outcome attribution processed"
    )


# --- EXECUTIVE INTELLIGENCE & SCENARIOS ---

@router.get("/executive/reports", summary="Generate Executive Intelligence Report")
async def get_executive_reports(user: UserContext = Depends(get_current_user)):
    report = learning_service.executive.generate_executive_report(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=report,
        correlation_id=get_correlation_id(),
        message="Executive intelligence report generated"
    )


@router.get("/scenarios", summary="Get Strategic Scenario Simulations")
async def get_scenarios(user: UserContext = Depends(get_current_user)):
    scenario = learning_service.executive.create_scenario_analysis(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=scenario,
        correlation_id=get_correlation_id(),
        message="Strategic decision scenario simulation generated"
    )


# --- GOVERNED TOOL CALLING TELEMETRY & SSE STREAM ---

@router.get("/command/tools/telemetry", summary="Get Governed Tool Calling Realtime Telemetry")
async def get_tool_telemetry(user: UserContext = Depends(get_current_user)):
    from services.agents.tools.executor import tool_executor
    from services.agents.tools.tool_registry import tool_registry

    durable_calls = tool_executor.list_durable_calls(tenant_id=user.tenant_id)
    registered_tools = tool_registry.list_tools()

    total_calls = len(durable_calls)
    succeeded_calls = len([c for c in durable_calls if c.get("execution_status") == "SUCCEEDED"])
    failed_calls = len([c for c in durable_calls if c.get("execution_status") in ["EXECUTION_FAILED", "VALIDATION_FAILED", "UNAUTHORIZED", "POLICY_DENIED"]])
    approval_required_calls = len([c for c in durable_calls if c.get("approval_status") in ["APPROVAL_REQUIRED", "APPROVED"]])

    avg_latency = round(sum(c.get("duration_ms", 0) for c in durable_calls) / total_calls, 2) if total_calls > 0 else 28.5

    return APIResponse(
        success=True,
        data={
            "total_registered_tools": len(registered_tools),
            "total_tool_calls": total_calls,
            "succeeded_tool_calls": succeeded_calls,
            "failed_tool_calls": failed_calls,
            "approval_required_calls": approval_required_calls,
            "tool_success_rate": round(succeeded_calls / total_calls, 4) if total_calls > 0 else 1.0,
            "average_latency_ms": avg_latency,
            "recent_calls": durable_calls[-10:]
        },
        correlation_id=get_correlation_id(),
        message="Governed tool calling telemetry retrieved"
    )


@router.get("/command/tools/stream", summary="Stream Realtime Tool Execution Events (SSE)")
async def stream_tool_events(user: UserContext = Depends(get_current_user)):
    """Server-Sent Events (SSE) stream for real-time tool execution state machine events."""
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    from services.agents.tools.executor import tool_executor

    async def event_generator():
        sent_ids = set()
        while True:
            events = tool_executor.get_events(tenant_id=user.tenant_id, limit=20)
            for event in events:
                e_id = event.get("event_id")
                if e_id not in sent_ids:
                    sent_ids.add(e_id)
                    yield f"event: {event['event_type']}\ndata: {json.dumps(event)}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

