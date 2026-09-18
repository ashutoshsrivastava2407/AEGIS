"""LLM Gateway Token & Cost Accounting Engine."""

import uuid
from typing import Dict, Any, List


class CostAccountingEngine:
    """Tracks token consumption, execution latency, and cost allocation per tenant."""

    def __init__(self):
        self._usage_logs: List[Dict[str, Any]] = []

    def record_usage(
        self,
        tenant_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        cost: float
    ) -> Dict[str, Any]:
        record = {
            "id": f"usg_{uuid.uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "latency_ms": latency_ms,
            "estimated_cost": cost
        }
        self._usage_logs.append(record)
        return record

    def get_tenant_usage_summary(self, tenant_id: str = "default") -> Dict[str, Any]:
        tenant_logs = [l for l in self._usage_logs if l["tenant_id"] == tenant_id]
        total_requests = len(tenant_logs)
        total_tokens = sum(l["total_tokens"] for l in tenant_logs)
        total_cost = sum(l["estimated_cost"] for l in tenant_logs)
        avg_latency = (sum(l["latency_ms"] for l in tenant_logs) / total_requests) if total_requests > 0 else 0.0

        return {
            "tenant_id": tenant_id,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6),
            "avg_latency_ms": round(avg_latency, 2)
        }


cost_accounting_engine = CostAccountingEngine()
