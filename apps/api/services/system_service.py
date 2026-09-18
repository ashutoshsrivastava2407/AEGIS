"""System Telemetry & Infrastructure Service."""

from typing import Dict, Any
from packages.security import UserContext
from packages.observability import metrics_exporter


class SystemService:
    async def get_system_telemetry(self, user: UserContext) -> Dict[str, Any]:
        return {
            "node_status": "HEALTHY",
            "cpu_utilization_pct": 12.5,
            "memory_utilization_pct": 34.1,
            "metrics": metrics_exporter.get_metrics(),
        }


system_service = SystemService()
