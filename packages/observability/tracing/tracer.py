"""Distributed trace context management for AEGIS."""

from typing import Optional, Dict
from packages.observability.correlation import get_correlation_id


class Tracer:
    """Trace context interface."""

    def get_trace_headers(self) -> Dict[str, str]:
        return {
            "x-correlation-id": get_correlation_id(),
        }


tracer = Tracer()
