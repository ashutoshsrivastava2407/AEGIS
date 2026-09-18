"""Distributed Lineage Tracer logging span trace events across workflow DAG executions."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from packages.database.models.workflow_execution import WorkflowTraceEventModel


class WorkflowLineageTracer:
    """Manages distributed correlation trace spans and lineage logging for workflow runs."""

    def start_trace_span(
        self,
        workflow_run_id: str,
        event_type: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        node_run_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> WorkflowTraceEventModel:
        """Create a new distributed trace span event."""
        span_id = str(uuid.uuid4())
        tid = trace_id or str(uuid.uuid4())

        return WorkflowTraceEventModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            node_run_id=node_run_id,
            trace_id=tid,
            span_id=span_id,
            parent_span_id=parent_span_id,
            event_type=event_type,
            details_json=details or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
            created_by="system",
            updated_by="system",
        )
