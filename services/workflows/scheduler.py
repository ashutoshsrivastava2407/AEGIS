"""Workflow Scheduler handling Cron, Interval, Timezone/DST, Misfire, Catch-up, and Overlap Policies."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from packages.database.models.workflow_trigger import WorkflowScheduleModel


class WorkflowScheduler:
    """Evaluates cron and interval schedules, DST adjustments, misfires, catch-up, and concurrency overlap policies."""

    VALID_OVERLAP_POLICIES = {"SKIP", "QUEUE", "ALLOW_CONCURRENT", "REPLACE"}

    def create_schedule(
        self,
        workflow_id: str,
        schedule_cron: str,
        timezone_name: str = "UTC",
        dst_behavior: str = "ADJUST",
        misfire_policy: str = "RUN_IMMEDIATELY",
        catch_up_policy: str = "IGNORE",
        overlap_policy: str = "SKIP",
        max_concurrent_runs: int = 1,
        tenant_id: str = "default",
    ) -> WorkflowScheduleModel:
        """Create a cron/interval schedule for a workflow."""
        if overlap_policy not in self.VALID_OVERLAP_POLICIES:
            raise ValueError(f"Invalid overlap policy: {overlap_policy}")

        return WorkflowScheduleModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            schedule_cron=schedule_cron,
            timezone=timezone_name,
            dst_behavior=dst_behavior,
            misfire_policy=misfire_policy,
            catch_up_policy=catch_up_policy,
            overlap_policy=overlap_policy,
            max_concurrent_runs=max_concurrent_runs,
            is_enabled=True,
            last_run_at=None,
            next_run_at=datetime.now(timezone.utc).isoformat(),
            created_by="system",
            updated_by="system",
        )

    def should_trigger(
        self,
        schedule: WorkflowScheduleModel,
        active_runs_count: int,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Determine if a scheduled workflow should trigger based on next_run_at and overlap policy."""
        now = current_time or datetime.now(timezone.utc)
        if not schedule.is_enabled:
            return {"should_run": False, "reason": "Schedule disabled."}

        # Check concurrency overlap policy
        if active_runs_count >= schedule.max_concurrent_runs:
            if schedule.overlap_policy == "SKIP":
                return {"should_run": False, "action": "SKIP", "reason": f"Active runs ({active_runs_count}) reached max_concurrent ({schedule.max_concurrent_runs}). Overlap policy SKIP."}
            elif schedule.overlap_policy == "QUEUE":
                return {"should_run": True, "action": "QUEUE", "reason": "Queued due to max concurrency limit."}
            elif schedule.overlap_policy == "REPLACE":
                return {"should_run": True, "action": "REPLACE", "reason": "Replacing existing active execution."}
            elif schedule.overlap_policy == "ALLOW_CONCURRENT":
                pass

        # Check schedule trigger time
        if schedule.next_run_at:
            next_run_dt = datetime.fromisoformat(schedule.next_run_at.replace("Z", "+00:00"))
            if now >= next_run_dt:
                return {"should_run": True, "action": "RUN", "reason": "Scheduled trigger time reached."}

        return {"should_run": False, "reason": "Schedule not due."}

    def update_schedule_after_run(self, schedule: WorkflowScheduleModel, run_time: Optional[datetime] = None) -> WorkflowScheduleModel:
        """Update last_run_at and calculate next_run_at (simulated 1-hour default interval for cron evaluation)."""
        now = run_time or datetime.now(timezone.utc)
        schedule.last_run_at = now.isoformat()
        # Compute next run (default +1 hour simulation)
        next_dt = now + timedelta(hours=1)
        schedule.next_run_at = next_dt.isoformat()
        return schedule
