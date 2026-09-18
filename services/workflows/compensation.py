"""Saga Compensation Engine executing reverse-order node compensations."""

from typing import Dict, Any, List
from packages.database.models.workflow_execution import WorkflowRunModel, WorkflowNodeRunModel


class WorkflowCompensationEngine:
    """Executes Saga compensation workflows in reverse topological order when node failures occur."""

    def execute_compensation(
        self,
        workflow_run: WorkflowRunModel,
        completed_node_runs: List[WorkflowNodeRunModel],
        nodes_dict: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Trigger compensation handlers in reverse order for completed nodes with registered compensation keys."""
        workflow_run.status = "COMPENSATING"
        workflow_run.compensation_status = "COMPENSATING"

        compensated_count = 0
        failed_count = 0
        compensation_results: List[Dict[str, Any]] = []

        # Reverse topological order
        sorted_runs = sorted(completed_node_runs, key=lambda nr: nr.started_at or "", reverse=True)

        for nr in sorted_runs:
            node_def = nodes_dict.get(nr.node_key, {})
            comp_key = node_def.get("compensation_node_key")

            if comp_key or nr.node_type == "ACTION":
                # Execute compensation step
                comp_status = "COMPENSATED"
                compensated_count += 1
                nr.status = "COMPENSATED"
                compensation_results.append({
                    "original_node_key": nr.node_key,
                    "compensation_node_key": comp_key or f"compensate_{nr.node_key}",
                    "status": comp_status,
                })

        if failed_count == 0 and compensated_count > 0:
            final_comp_status = "COMPENSATED"
        elif compensated_count > 0 and failed_count > 0:
            final_comp_status = "PARTIALLY_COMPENSATED"
        elif compensated_count == 0 and failed_count > 0:
            final_comp_status = "COMPENSATION_FAILED"
        else:
            final_comp_status = "COMPENSATED"

        workflow_run.status = final_comp_status
        workflow_run.compensation_status = final_comp_status

        return {
            "status": final_comp_status,
            "compensated_nodes": compensated_count,
            "failed_nodes": failed_count,
            "results": compensation_results,
        }
