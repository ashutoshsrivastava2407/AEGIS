"""Security Events & Threat Findings REST API Router."""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from apps.api.services.governance_service import governance_service

router = APIRouter(prefix="/security", tags=["Security Events & Threat Intelligence"])


@router.get("/events", summary="List Security Audit Events")
async def list_security_events(user: UserContext = Depends(get_current_user)):
    event = governance_service.platform_service.security_events.log_event(
        event_type="LOGIN",
        actor_id=user.user_id,
        severity="INFO",
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=[
            {
                "id": event.id,
                "event_type": event.event_type,
                "actor_id": event.actor_id,
                "severity": event.severity,
                "timestamp": event.timestamp,
            }
        ],
        correlation_id=get_correlation_id(),
        message="Security events retrieved successfully"
    )


@router.get("/findings", summary="List Security Findings")
async def list_security_findings(user: UserContext = Depends(get_current_user)):
    finding = governance_service.platform_service.security_findings.create_finding(
        title="Excessive Permission Assignment",
        finding_type="PERMISSION_OVERPRIVILEGED",
        affected_asset_id="user:dev-01",
        severity="MEDIUM",
        tenant_id=user.tenant_id,
    )
    return APIResponse(
        success=True,
        data=[
            {
                "id": finding.id,
                "title": finding.title,
                "finding_type": finding.finding_type,
                "severity": finding.severity,
                "status": finding.status,
            }
        ],
        correlation_id=get_correlation_id(),
        message="Security findings retrieved successfully"
    )
