"""Workflow Recovery, Stale Worker Lease Fencing Cleanup, and DLQ Handler."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from packages.database.models.workflow_execution import WorkflowRunModel, WorkflowNodeRunModel
from packages.database.models.dlq_record import DLQRecordModel


class WorkflowRecoveryEngine:
    """Handles checkpoint recovery, stale worker fencing cleanup, and dead-letter queue routing."""

    def scan_and_recover_stale_workers(
        self,
        active_runs: List[WorkflowRunModel],
        current_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Identify runs with expired worker leases and bump fencing tokens to reclaim execution."""
        now = current_time or datetime.now(timezone.utc)
        recovered: List[Dict[str, Any]] = []

        for run in active_runs:
            if run.status == "RUNNING" and run.lease_expires_at:
                expires_dt = datetime.fromisoformat(run.lease_expires_at.replace("Z", "+00:00"))
                if now > expires_dt:
                    old_worker = run.worker_id
                    run.worker_id = "recovery-worker"
                    run.fencing_token += 1
                    run.lease_expires_at = None
                    recovered.append({
                        "run_id": run.id,
                        "old_worker": old_worker,
                        "new_fencing_token": run.fencing_token,
                        "action": "RECLAIMED_LEASE",
                    })

        return recovered

    def route_to_dlq(self, run: WorkflowRunModel, error: Dict[str, Any], tenant_id: str = "default") -> DLQRecordModel:
        """Route unrecoverable workflow run failures to Dead Letter Queue."""
        import uuid
        run.status = "FAILED"
        return DLQRecordModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            source_system="WORKFLOW_ENGINE",
            payload_json={"workflow_run_id": run.id, "workflow_id": run.workflow_id, "error": error},
            error_message=str(error.get("message", "Workflow run failed permanently")),
            status="UNPROCESSED",
            created_by="system",
            updated_by="system",
        )
