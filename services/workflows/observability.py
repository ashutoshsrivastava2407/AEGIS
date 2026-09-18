"""Workflow Observability and Real-time Operational Metrics Engine."""

from typing import Dict, Any, List
from packages.database.models.workflow_execution import WorkflowRunModel, WorkflowNodeRunModel


class WorkflowObservabilityEngine:
    """Aggregates operational metrics across workflow runs and node executions."""

    def get_operational_metrics(
        self,
        workflow_runs: List[WorkflowRunModel],
        node_runs: List[WorkflowNodeRunModel],
    ) -> Dict[str, Any]:
        """Compute system metrics: total_runs, success_rate, active_runs, failed_runs, total_cost_cents, node_status_counts."""
        total_runs = len(workflow_runs)
        if total_runs == 0:
            return {
                "total_runs": 0,
                "active_runs": 0,
                "completed_runs": 0,
                "failed_runs": 0,
                "success_rate_percent": 100.0,
                "total_cost_cents": 0.0,
                "node_runs_total": 0,
            }

        completed = sum(1 for r in workflow_runs if r.status == "COMPLETED")
        failed = sum(1 for r in workflow_runs if r.status in {"FAILED", "TIMED_OUT", "COMPENSATION_FAILED"})
        active = sum(1 for r in workflow_runs if r.status in {"RUNNING", "PENDING", "COMPENSATING"})
        total_cost = sum(r.cost_cents for r in workflow_runs)

        success_rate = (completed / total_runs) * 100.0 if total_runs > 0 else 0.0

        node_counts: Dict[str, int] = {}
        for nr in node_runs:
            node_counts[nr.status] = node_counts.get(nr.status, 0) + 1

        return {
            "total_runs": total_runs,
            "active_runs": active,
            "completed_runs": completed,
            "failed_runs": failed,
            "success_rate_percent": round(success_rate, 2),
            "total_cost_cents": round(total_cost, 4),
            "node_runs_total": len(node_runs),
            "node_status_breakdown": node_counts,
        }
