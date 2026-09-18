"""Universal Distributed Tracing & Correlation Context Service."""

import uuid
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class UniversalTraceContextService:
    """Universal cross-platform trace context generator and propagator."""

    def __init__(self):
        self._active_spans: Dict[str, Dict[str, Any]] = {}

    def create_trace_context(
        self,
        tenant_id: str = "default",
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        service: str = "aegis-platform",
        environment: str = "production",
        deployment_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        agent_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate authoritative distributed trace context dictionary."""
        tid = trace_id or f"trc-{uuid.uuid4().hex[:16]}"
        cid = correlation_id or f"corr-{uuid.uuid4().hex[:16]}"
        sid = f"spn-{uuid.uuid4().hex[:12]}"

        return {
            "tenant_id": tenant_id,
            "correlation_id": cid,
            "trace_id": tid,
            "span_id": sid,
            "parent_span_id": None,
            "service": service,
            "environment": environment,
            "deployment_id": deployment_id or "dep-current",
            "workflow_run_id": workflow_run_id,
            "decision_id": decision_id,
            "agent_run_id": agent_run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def start_span(
        self,
        name: str,
        parent_context: Dict[str, Any],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start child span linked to parent trace context."""
        span_id = f"spn-{uuid.uuid4().hex[:12]}"

        span_context = {
            "tenant_id": parent_context.get("tenant_id", "default"),
            "correlation_id": parent_context.get("correlation_id"),
            "trace_id": parent_context.get("trace_id"),
            "span_id": span_id,
            "parent_span_id": parent_context.get("span_id"),
            "service": parent_context.get("service", "aegis-platform"),
            "environment": parent_context.get("environment", "production"),
            "deployment_id": parent_context.get("deployment_id"),
            "workflow_run_id": parent_context.get("workflow_run_id"),
            "decision_id": parent_context.get("decision_id"),
            "agent_run_id": parent_context.get("agent_run_id"),
            "name": name,
            "start_time_epoch_ms": int(time.time() * 1000),
            "attributes": attributes or {},
            "status": "RUNNING",
        }

        self._active_spans[span_id] = span_context
        return span_context

    def end_span(
        self,
        span_context: Dict[str, Any],
        status: str = "OK",
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """End span, recording duration and status."""
        span_id = span_context.get("span_id")
        end_time_ms = int(time.time() * 1000)
        start_time_ms = span_context.get("start_time_epoch_ms", end_time_ms)
        duration_ms = end_time_ms - start_time_ms

        completed_span = dict(span_context)
        completed_span.update({
            "end_time_epoch_ms": end_time_ms,
            "duration_ms": duration_ms,
            "status": status,
            "error": error,
        })

        if span_id in self._active_spans:
            del self._active_spans[span_id]

        return completed_span

    def inject_http_headers(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Inject trace context into standard HTTP headers (W3C tracecontext format)."""
        return {
            "X-Tenant-Id": str(context.get("tenant_id", "default")),
            "X-Correlation-Id": str(context.get("correlation_id", "")),
            "X-Trace-Id": str(context.get("trace_id", "")),
            "X-Span-Id": str(context.get("span_id", "")),
            "traceparent": f"00-{context.get('trace_id')}-{context.get('span_id')}-01",
        }

    def extract_http_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Extract trace context from incoming HTTP headers."""
        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-Id", "default")
        correlation_id = headers.get("x-correlation-id") or headers.get("X-Correlation-Id")
        trace_id = headers.get("x-trace-id") or headers.get("X-Trace-Id")
        span_id = headers.get("x-span-id") or headers.get("X-Span-Id")

        return self.create_trace_context(
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
        )
