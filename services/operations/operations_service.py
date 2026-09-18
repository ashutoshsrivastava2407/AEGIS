"""Central Production Operations Platform Service Facade.

Unifies Health, Observability, SLO, Incidents, Runbooks, Remediation, Resilience,
Disaster Recovery, Deployments, and FinOps into one coherent operations plane.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from services.operations.health import HealthAndReadinessService
from services.operations.metrics import MetricsAggregationService
from services.operations.tracing import UniversalTraceContextService
from services.operations.slo import SLOAndErrorBudgetService
from services.operations.incidents import IncidentManagementService
from services.operations.runbooks import RunbookRegistryService
from services.operations.remediation import PolicyGovernedRemediationService
from services.operations.circuit_breaker import CircuitBreakerAndResilienceService
from services.operations.recovery import DisasterRecoveryService
from services.operations.deployments import DeploymentReleaseService
from services.operations.finops import PlatformFinOpsService


class ProductionOperationsPlatformService:
    """Central unified Production Operations Platform Service facade."""

    def __init__(self, db_session=None):
        self.db = db_session
        self.health = HealthAndReadinessService(db_session)
        self.metrics = MetricsAggregationService()
        self.tracing = UniversalTraceContextService()
        self.slo = SLOAndErrorBudgetService(db_session)
        self.incidents = IncidentManagementService(db_session)
        self.runbooks = RunbookRegistryService(db_session)
        self.remediation = PolicyGovernedRemediationService(db_session)
        self.resilience = CircuitBreakerAndResilienceService()
        self.recovery = DisasterRecoveryService(db_session)
        self.deployments = DeploymentReleaseService(db_session)
        self.finops = PlatformFinOpsService(db_session)

    def get_operations_overview(self, tenant_id: str = "default") -> Dict[str, Any]:
        """Generate high-level production operations platform dashboard overview."""
        liveness = self.health.get_liveness_status()
        readiness = self.health.get_readiness_status()
        incidents = self.incidents.list_incidents(tenant_id=tenant_id)
        slos = self.slo.list_slos(tenant_id=tenant_id)
        backups = self.recovery.list_backups(tenant_id=tenant_id)
        cost_summary = self.finops.get_cost_summary(tenant_id=tenant_id)

        active_incidents = [i for i in incidents if i.get("status") not in ["RESOLVED", "CLOSED"]]

        return {
            "status": "OPERATIONAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "liveness": liveness,
            "readiness": readiness,
            "active_incidents_count": len(active_incidents),
            "total_incidents_count": len(incidents),
            "slo_count": len(slos),
            "backup_count": len(backups),
            "cost_summary": cost_summary,
            "tenant_id": tenant_id,
        }
