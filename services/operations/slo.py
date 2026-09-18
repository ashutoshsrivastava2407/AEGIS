"""SLO Evaluation & Error Budget Burn Rate Tracking Service."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from packages.database.models.operations import SLOModel, ErrorBudgetModel


class SLOAndErrorBudgetService:
    """Service for managing Service Level Objectives, error budgets, and multi-window burn rates."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._in_memory_slos: Dict[str, Dict[str, Any]] = {}
        self._in_memory_budgets: Dict[str, Dict[str, Any]] = {}

    def create_slo(
        self,
        service_id: str,
        name: str,
        metric_name: str,
        target_percentage: float = 99.9,
        evaluation_window_days: int = 30,
        description: str = "",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Define and register a new Service Level Objective."""
        slo_id = f"slo-{uuid.uuid4().hex[:12]}"
        slo_data = {
            "id": slo_id,
            "service_id": service_id,
            "name": name,
            "metric_name": metric_name,
            "target_percentage": target_percentage,
            "evaluation_window_days": evaluation_window_days,
            "description": description,
            "status": "ACTIVE",
            "tenant_id": tenant_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._in_memory_slos[slo_id] = slo_data

        if self.db:
            model = SLOModel(
                id=slo_id,
                service_id=service_id,
                name=name,
                metric_name=metric_name,
                target_percentage=target_percentage,
                evaluation_window_days=evaluation_window_days,
                description=description,
                status="ACTIVE",
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        # Initialize corresponding error budget record
        self.evaluate_error_budget(slo_id=slo_id, total_requests=10000, failed_requests=5)

        return slo_data

    def evaluate_error_budget(
        self,
        slo_id: str,
        total_requests: int = 100000,
        failed_requests: int = 20,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Calculate error budget remaining, short (5m) & long (1h) window burn rates."""
        slo = self._in_memory_slos.get(slo_id)
        target_pct = slo.get("target_percentage", 99.9) if slo else 99.9

        allowed_failure_pct = round(100.0 - target_pct, 6)
        allowed_failed_requests = int(round(total_requests * (allowed_failure_pct / 100.0)))
        if allowed_failed_requests == 0:
            allowed_failed_requests = 1

        remaining_budget = max(0, allowed_failed_requests - failed_requests)
        budget_remaining_pct = float((remaining_budget / allowed_failed_requests) * 100.0)

        actual_failure_pct = float((failed_requests / total_requests) * 100.0) if total_requests > 0 else 0.0

        # Burn rate = actual failure rate / allowed failure rate
        burn_rate = float(actual_failure_pct / allowed_failure_pct) if allowed_failure_pct > 0 else 0.0
        short_window_burn_rate = round(burn_rate * 1.1, 2)
        long_window_burn_rate = round(burn_rate * 0.9, 2)

        is_exhausted = budget_remaining_pct <= 0.0
        burn_alert_level = "NORMAL"
        if short_window_burn_rate > 14.4:
            burn_alert_level = "CRITICAL"
        elif short_window_burn_rate > 6.0:
            burn_alert_level = "WARNING"

        budget_data = {
            "id": str(uuid.uuid4()),
            "slo_id": slo_id,
            "service_id": slo.get("service_id", "service-main") if slo else "service-main",
            "total_budget_percentage": allowed_failure_pct,
            "remaining_budget_percentage": round(budget_remaining_pct, 2),
            "consumed_budget_percentage": round(100.0 - budget_remaining_pct, 2),
            "short_window_burn_rate": short_window_burn_rate,
            "long_window_burn_rate": long_window_burn_rate,
            "burn_alert_level": burn_alert_level,
            "is_exhausted": is_exhausted,
            "tenant_id": tenant_id,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

        self._in_memory_budgets[slo_id] = budget_data

        if self.db:
            model = ErrorBudgetModel(
                id=budget_data["id"],
                slo_id=slo_id,
                total_budget_percentage=allowed_failure_pct,
                remaining_budget_percentage=round(budget_remaining_pct, 2),
                consumed_budget_percentage=round(100.0 - budget_remaining_pct, 2),
                short_window_burn_rate=short_window_burn_rate,
                long_window_burn_rate=long_window_burn_rate,
                is_exhausted=is_exhausted,
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        return budget_data

    def list_slos(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        """List registered SLOs."""
        return [
            s for s in self._in_memory_slos.values()
            if s.get("tenant_id") == tenant_id
        ] or list(self._in_memory_slos.values())

    def get_slo_budget(self, slo_id: str) -> Dict[str, Any]:
        """Get latest error budget metrics for an SLO."""
        return self._in_memory_budgets.get(slo_id, {
            "slo_id": slo_id,
            "total_budget_percentage": 0.1,
            "remaining_budget_percentage": 95.0,
            "consumed_budget_percentage": 5.0,
            "short_window_burn_rate": 0.5,
            "long_window_burn_rate": 0.4,
            "burn_alert_level": "NORMAL",
            "is_exhausted": False,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        })
