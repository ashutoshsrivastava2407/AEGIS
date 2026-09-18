"""Generic Human Task Manager separated from Central Governance Approval Authority."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from packages.database.models.workflow_execution import WorkflowHumanTaskModel


class WorkflowHumanTaskManager:
    """Manages generic human form and task interactions separate from central governance authority."""

    def create_human_task(
        self,
        workflow_run_id: str,
        node_run_id: str,
        task_key: str,
        form_schema_json: Dict[str, Any],
        assignee: Optional[str] = None,
        role: Optional[str] = None,
        timeout_hours: int = 24,
        tenant_id: str = "default",
    ) -> WorkflowHumanTaskModel:
        """Create a human task requiring user form submission or manual action."""
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=timeout_hours)).isoformat()

        return WorkflowHumanTaskModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            node_run_id=node_run_id,
            task_key=task_key,
            assignee=assignee,
            role=role,
            form_schema_json=form_schema_json,
            submitted_data_json={},
            status="PENDING",
            expires_at=expires_at,
            escalated_to=None,
            completed_at=None,
            created_by="system",
            updated_by="system",
        )

    def submit_task(
        self,
        task: WorkflowHumanTaskModel,
        submitted_data: Dict[str, Any],
        submitted_by: str,
    ) -> WorkflowHumanTaskModel:
        """Submit data and complete human task with TOCTOU expiration check."""
        if task.status != "PENDING" and task.status != "IN_PROGRESS":
            raise ValueError(f"Task {task.id} is not in submittable state: {task.status}")

        if task.expires_at:
            exp_dt = datetime.fromisoformat(task.expires_at.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > exp_dt:
                task.status = "TIMED_OUT"
                task.updated_by = submitted_by
                raise ValueError(f"Task {task.id} has expired.")

        task.submitted_data_json = submitted_data
        task.status = "COMPLETED"
        task.completed_at = datetime.now(timezone.utc).isoformat()
        task.updated_by = submitted_by
        return task

    def escalate_task(self, task: WorkflowHumanTaskModel, escalate_to: str) -> WorkflowHumanTaskModel:
        """Escalate overdue or unassigned human task."""
        task.status = "ESCALATED"
        task.escalated_to = escalate_to
        task.updated_by = "system"
        return task
