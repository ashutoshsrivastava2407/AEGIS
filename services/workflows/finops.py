"""Workflow FinOps Engine for Cost Accounting and Budget Enforcement."""

from typing import Dict, Any, List
from packages.database.models.workflow_execution import WorkflowRunModel, WorkflowNodeRunModel


class WorkflowFinOpsEngine:
    """Calculates and tracks compute/API execution costs across workflow DAG runs."""

    # Base cost estimates in cents
    NODE_TYPE_BASE_COSTS = {
        "ACTION": 2.5,
        "DECISION": 5.0,
        "TRANSFORM": 0.5,
        "NOTIFICATION": 0.1,
        "WAIT": 0.0,
        "HUMAN_TASK": 1.0,
    }

    def calculate_node_cost(self, node_type: str, execution_time_seconds: float = 1.0) -> float:
        """Calculate node execution cost in cents based on node_type and duration."""
        base = self.NODE_TYPE_BASE_COSTS.get(node_type.upper(), 1.0)
        time_cost = max(0.01, execution_time_seconds * 0.1)
        return round(base + time_cost, 4)

    def record_run_cost(self, run: WorkflowRunModel, node_runs: List[WorkflowNodeRunModel]) -> float:
        """Sum and record total cost in cents for a completed workflow run."""
        total_cents = 0.0
        for nr in node_runs:
            c = self.calculate_node_cost(nr.node_type)
            total_cents += c

        run.cost_cents = round(total_cents, 4)
        return run.cost_cents
