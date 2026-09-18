"""Production Operations, Observability & Reliability Control Plane REST API Router."""

from fastapi import APIRouter, Depends, Body, Query
from typing import Dict, Any, List, Optional
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse

from services.operations import ProductionOperationsPlatformService

router = APIRouter(prefix="/operations", tags=["Production Operations Platform"])
ops_service = ProductionOperationsPlatformService()


@router.get("/overview", summary="Get Production Operations Overview")
async def get_operations_overview(user: UserContext = Depends(get_current_user)):
    data = ops_service.get_operations_overview(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=data,
        correlation_id=get_correlation_id(),
        message="Operations platform overview retrieved successfully"
    )


# --- HEALTH & SERVICE CATALOG ---

@router.get("/services", summary="List Registered Services")
async def list_services(user: UserContext = Depends(get_current_user)):
    services = ops_service.health.list_services(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=services,
        correlation_id=get_correlation_id(),
        message="Service catalog retrieved successfully"
    )


@router.post("/services", summary="Register Service in Catalog")
async def register_service(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    service = ops_service.health.register_service(
        service_id=payload.get("service_id", "service-main"),
        name=payload.get("name", "Core Platform Service"),
        owner_team=payload.get("owner_team", "Platform SRE"),
        tier=payload.get("tier", "TIER_1"),
        description=payload.get("description", ""),
        repository_url=payload.get("repository_url", ""),
        tech_stack=payload.get("tech_stack", []),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=service,
        correlation_id=get_correlation_id(),
        message="Service registered successfully"
    )


@router.post("/readiness/evaluate", summary="Evaluate Production Readiness Score")
async def evaluate_readiness(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    readiness = ops_service.health.evaluate_production_readiness(
        service_id=payload.get("service_id", "service-main"),
        checklist_evaluations=payload.get("checklist", {
            "has_metrics_telemetry": True,
            "has_distributed_tracing": True,
            "has_slo_defined": True,
            "has_runbook": True,
            "has_automated_backups": True,
            "passed_security_audit": True,
            "has_circuit_breakers": True,
            "has_rollback_plan": True,
        }),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=readiness,
        correlation_id=get_correlation_id(),
        message="Production readiness score evaluated successfully"
    )


# --- OBSERVABILITY & METRICS ---

@router.get("/metrics/summary", summary="Get Latency & Error Rate Metrics Summary")
async def get_metrics_summary(
    metric_name: str = Query("http_request_duration_ms"),
    service: Optional[str] = Query(None),
    user: UserContext = Depends(get_current_user)
):
    summary = ops_service.metrics.get_metrics_summary(
        name=metric_name,
        service=service,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=summary,
        correlation_id=get_correlation_id(),
        message="Metrics summary retrieved successfully"
    )


@router.post("/tracing/context", summary="Create Distributed Trace Context")
async def create_trace_context(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    ctx = ops_service.tracing.create_trace_context(
        tenant_id=user.tenant_id,
        correlation_id=payload.get("correlation_id"),
        service=payload.get("service", "aegis-platform"),
        environment=payload.get("environment", "production"),
        deployment_id=payload.get("deployment_id"),
        workflow_run_id=payload.get("workflow_run_id"),
        decision_id=payload.get("decision_id"),
        agent_run_id=payload.get("agent_run_id"),
    )
    return APIResponse(
        success=True,
        data=ctx,
        correlation_id=get_correlation_id(),
        message="Universal trace context created successfully"
    )


# --- SLO & ERROR BUDGETS ---

@router.get("/slo", summary="List Service Level Objectives")
async def list_slos(user: UserContext = Depends(get_current_user)):
    slos = ops_service.slo.list_slos(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=slos,
        correlation_id=get_correlation_id(),
        message="SLO target list retrieved successfully"
    )


@router.post("/slo", summary="Create Service Level Objective")
async def create_slo(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    slo = ops_service.slo.create_slo(
        service_id=payload.get("service_id", "service-main"),
        name=payload.get("name", "99.9% High Availability Latency SLO"),
        metric_name=payload.get("metric_name", "http_latency_ms"),
        target_percentage=payload.get("target_percentage", 99.9),
        evaluation_window_days=payload.get("evaluation_window_days", 30),
        description=payload.get("description", ""),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=slo,
        correlation_id=get_correlation_id(),
        message="SLO created successfully"
    )


# --- INCIDENTS ---

@router.get("/incidents", summary="List Incidents")
async def list_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    user: UserContext = Depends(get_current_user)
):
    incidents = ops_service.incidents.list_incidents(
        status=status,
        severity=severity,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=incidents,
        correlation_id=get_correlation_id(),
        message="Incident list retrieved successfully"
    )


@router.post("/incidents", summary="Declare Production Incident")
async def declare_incident(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    incident = ops_service.incidents.declare_incident(
        title=payload.get("title", "High Database CPU Saturation"),
        severity=payload.get("severity", "SEV2"),
        service_id=payload.get("service_id", "platform-db"),
        summary=payload.get("summary", ""),
        assigned_commander=payload.get("assigned_commander"),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=incident,
        correlation_id=get_correlation_id(),
        message="Incident declared successfully"
    )


@router.post("/incidents/{incident_id}/transition", summary="Transition Incident Status")
async def transition_incident(
    incident_id: str,
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    updated = ops_service.incidents.transition_incident_status(
        incident_id=incident_id,
        new_status=payload.get("new_status", "INVESTIGATING"),
        actor=payload.get("actor", user.user_id),
        reason=payload.get("reason", ""),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=updated,
        correlation_id=get_correlation_id(),
        message="Incident status updated successfully"
    )


# --- REMEDIATION & RUNBOOKS ---

@router.post("/remediation/execute", summary="Execute Policy-Governed Remediation")
async def execute_remediation(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    evidence = ops_service.remediation.execute_remediation(
        remediation_action=payload.get("action", "RESTART_POD"),
        target_service_id=payload.get("service_id", "service-main"),
        parameters=payload.get("parameters", {}),
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        user_role=user.roles[0] if user.roles else "ENTERPRISE_ADMIN",
    )
    return APIResponse(
        success=True,
        data=evidence,
        correlation_id=get_correlation_id(),
        message="Policy-governed remediation executed"
    )


# --- RESILIENCE & CIRCUIT BREAKERS ---

@router.post("/circuit-breaker/outcome", summary="Record Circuit Breaker Outcome")
async def record_circuit_outcome(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    status = ops_service.resilience.record_circuit_outcome(
        name=payload.get("name", "db-connection-pool"),
        success=payload.get("success", True),
    )
    return APIResponse(
        success=True,
        data=status,
        correlation_id=get_correlation_id(),
        message="Circuit breaker outcome recorded"
    )


# --- DISASTER RECOVERY & BACKUPS ---

@router.get("/recovery/backups", summary="List Disaster Recovery Backups")
async def list_backups(user: UserContext = Depends(get_current_user)):
    backups = ops_service.recovery.list_backups(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=backups,
        correlation_id=get_correlation_id(),
        message="Backups list retrieved successfully"
    )


@router.post("/recovery/backups", summary="Trigger Automated Backup Job")
async def create_backup(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    backup = ops_service.recovery.create_backup(
        backup_type=payload.get("backup_type", "FULL"),
        size_bytes=payload.get("size_bytes", 104857600),
        storage_location=payload.get("storage_location", "s3://aegis-backups/prod.tar.gz"),
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=backup,
        correlation_id=get_correlation_id(),
        message="Backup job created successfully"
    )


@router.post("/recovery/restore", summary="Verify and Trigger DR Restore")
async def trigger_restore(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    restore = ops_service.recovery.verify_and_trigger_restore(
        backup_id=payload.get("backup_id", "bkp-default"),
        target_environment=payload.get("target_environment", "dr-staging"),
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        user_role=user.roles[0] if user.roles else "ENTERPRISE_ADMIN",
    )
    return APIResponse(
        success=True,
        data=restore,
        correlation_id=get_correlation_id(),
        message="Disaster recovery restore processed"
    )


# --- DEPLOYMENTS & ROLLBACKS ---

@router.post("/deployments", summary="Trigger Deployment Release")
async def trigger_deployment(
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    dep = ops_service.deployments.trigger_deployment(
        service_id=payload.get("service_id", "service-main"),
        release_version=payload.get("release_version", "v1.2.0"),
        strategy=payload.get("strategy", "CANARY"),
        artifact_checksum=payload.get("artifact_checksum"),
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
        user_role=user.roles[0] if user.roles else "ENTERPRISE_ADMIN",
    )
    return APIResponse(
        success=True,
        data=dep,
        correlation_id=get_correlation_id(),
        message="Deployment release triggered"
    )


@router.post("/deployments/{deployment_id}/rollback", summary="Execute Immutable Release Rollback")
async def rollback_deployment(
    deployment_id: str,
    payload: Dict[str, Any] = Body(...),
    user: UserContext = Depends(get_current_user)
):
    rlb = ops_service.deployments.rollback_deployment(
        deployment_id=deployment_id,
        reason=payload.get("reason", "Health gate breach"),
        actor_id=user.user_id,
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=rlb,
        correlation_id=get_correlation_id(),
        message="Immutable release rollback executed successfully"
    )


# --- PLATFORM FINOPS ---

@router.get("/finops/summary", summary="Get Platform FinOps Summary")
async def get_finops_summary(user: UserContext = Depends(get_current_user)):
    summary = ops_service.finops.get_cost_summary(tenant_id=user.tenant_id)
    return APIResponse(
        success=True,
        data=summary,
        correlation_id=get_correlation_id(),
        message="Platform FinOps cost summary retrieved successfully"
    )
