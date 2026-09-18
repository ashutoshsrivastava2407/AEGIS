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


# --- COMMAND CENTER ---

@router.get("/command-center/overview", summary="Get Enterprise Command Center Overview")
async def get_command_center_overview(user: UserContext = Depends(get_current_user)):
    overview = command_service.get_command_center_overview(user)
    return APIResponse(
        success=True,
        data=overview,
        correlation_id=get_correlation_id(),
        message="Enterprise Command Center overview retrieved successfully"
    )


@router.get("/command-center/readiness", summary="Evaluate Evidence-Backed System Readiness Gate")
async def get_system_readiness(user: UserContext = Depends(get_current_user)):
    readiness = command_service.readiness_gate.evaluate_system_readiness(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=readiness,
        correlation_id=get_correlation_id(),
        message="Production readiness gate evaluated successfully"
    )


@router.get("/command-center/trace", summary="Reconstruct End-to-End Trace Tree")
async def reconstruct_trace(
    correlation_id: Optional[str] = Query(None),
    trace_id: Optional[str] = Query(None),
    user: UserContext = Depends(get_current_user)
):
    tree = command_service.trace_explorer.reconstruct_trace(
        correlation_id=correlation_id,
        trace_id=trace_id,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=tree,
        correlation_id=get_correlation_id(),
        message="End-to-end trace correlation tree reconstructed"
    )


# --- GLOBAL SEARCH ---

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
