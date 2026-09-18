"""Workflow Execution Engine with Worker Lease Fencing and Immutable Manifest Hashing."""

import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from packages.database.models.workflow_execution import WorkflowRunModel, WorkflowNodeRunModel


class WorkflowEngine:
    """Core durable workflow execution engine with worker fencing protection and manifest hashing."""

    LEASE_DURATION_SECONDS = 30

    def compute_workflow_manifest_hash(
        self,
        workflow_version_id: str,
        definition_fingerprint: str,
        trigger_payload: Dict[str, Any],
    ) -> str:
        """Compute SHA-256 execution manifest hash pinning the immutable execution contract."""
        payload_str = json.dumps(trigger_payload, sort_keys=True)
        raw = f"{workflow_version_id}:{definition_fingerprint}:{payload_str}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def start_workflow_run(
        self,
        workflow_id: str,
        workflow_version_id: str,
        definition_fingerprint: str,
        trigger_type: str,
        trigger_payload: Dict[str, Any],
        tenant_id: str = "default",
        worker_id: str = "worker-primary",
    ) -> WorkflowRunModel:
        """Start a new workflow execution run instance with active fencing lease."""
        run_id = str(uuid.uuid4())
        manifest_hash = self.compute_workflow_manifest_hash(workflow_version_id, definition_fingerprint, trigger_payload)
        now = datetime.now(timezone.utc)
        lease_expires = now + timedelta(seconds=self.LEASE_DURATION_SECONDS)

        return WorkflowRunModel(
            id=run_id,
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            workflow_version_id=workflow_version_id,
            trigger_type=trigger_type,
            trigger_payload_json=trigger_payload,
            status="RUNNING",
            current_step_key=None,
            workflow_manifest_hash=manifest_hash,
            worker_id=worker_id,
            lease_id=str(uuid.uuid4()),
            lease_expires_at=lease_expires.isoformat(),
            fencing_token=1,
            started_at=now.isoformat(),
            completed_at=None,
            error_message=None,
            compensation_status=None,
            cost_cents=0.0,
            created_by="system",
            updated_by="system",
        )

    def renew_worker_lease(self, run: WorkflowRunModel, worker_id: str, fencing_token: int) -> WorkflowRunModel:
        """Renew worker lease using fencing token validation to prevent split-brain execution."""
        if run.worker_id != worker_id:
            raise ValueError(f"Worker ID mismatch: current={run.worker_id}, expected={worker_id}")
        if run.fencing_token != fencing_token:
            raise ValueError(f"Stale worker fencing token! Current={run.fencing_token}, provided={fencing_token}")

        now = datetime.now(timezone.utc)
        run.lease_expires_at = (now + timedelta(seconds=self.LEASE_DURATION_SECONDS)).isoformat()
        run.fencing_token += 1
        run.updated_by = worker_id
        return run

    def validate_fencing_token(self, run: WorkflowRunModel, fencing_token: int) -> bool:
        """Verify worker fencing token is current and lease has not expired."""
        if run.fencing_token != fencing_token:
            return False

        if run.lease_expires_at:
            expires_dt = datetime.fromisoformat(run.lease_expires_at.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires_dt:
                return False

        return True

    def create_node_run(
        self,
        workflow_run_id: str,
        node_key: str,
        node_type: str,
        inputs: Dict[str, Any],
        worker_id: str = "worker-primary",
        fencing_token: int = 1,
        action_contract_id: Optional[str] = None,
    ) -> WorkflowNodeRunModel:
        """Initialize DAG node execution run record."""
        return WorkflowNodeRunModel(
            id=str(uuid.uuid4()),
            tenant_id="default",
            workflow_run_id=workflow_run_id,
            node_key=node_key,
            node_type=node_type,
            status="RUNNING",
            inputs_json=inputs,
            outputs_json={},
            error_json={},
            started_at=datetime.now(timezone.utc).isoformat(),
            completed_at=None,
            retry_count=0,
            worker_id=worker_id,
            fencing_token=fencing_token,
            action_contract_id=action_contract_id,
            governed_execution_id=None,
            postcondition_verified=False,
            created_by=worker_id,
            updated_by=worker_id,
        )

    def complete_node_run(
        self,
        node_run: WorkflowNodeRunModel,
        outputs: Dict[str, Any],
        governed_execution_id: Optional[str] = None,
        postcondition_verified: bool = True,
    ) -> WorkflowNodeRunModel:
        """Complete a node run with outputs and verification status."""
        node_run.status = "COMPLETED"
        node_run.outputs_json = outputs
        node_run.governed_execution_id = governed_execution_id
        node_run.postcondition_verified = postcondition_verified
        node_run.completed_at = datetime.now(timezone.utc).isoformat()
        return node_run

    def fail_node_run(self, node_run: WorkflowNodeRunModel, error: Dict[str, Any]) -> WorkflowNodeRunModel:
        """Fail a node run with error details."""
        node_run.status = "FAILED"
        node_run.error_json = error
        node_run.completed_at = datetime.now(timezone.utc).isoformat()
        return node_run
