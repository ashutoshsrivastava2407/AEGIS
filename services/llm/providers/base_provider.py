"""LLM Provider Base Interface & Mock Adapter."""

import time
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


class BaseLLMProvider:
    """Abstract interface for LLM provider adapters."""

    def __init__(self, name: str, provider_type: str):
        self.name = name
        self.provider_type = provider_type

    def generate_chat(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError("Providers must implement generate_chat()")


class MockLLMProvider(BaseLLMProvider):
    """Deterministic, production-grade local provider execution supporting native tool calling."""

    def __init__(self, name: str = "mock-primary"):
        super().__init__(name, "MOCK")

    def generate_chat(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        start = time.time()
        input_tokens = len(prompt.split()) + (len(system_prompt.split()) if system_prompt else 0)

        tool_calls = []

        # If tools are provided and prompt implies an action/investigation, synthesize structured tool call
        if tools:
            prompt_lower = prompt.lower()
            if "investigate" in prompt_lower or "anomaly" in prompt_lower:
                tool_calls.append({
                    "call_id": f"call_{uuid.uuid4().hex[:12]}",
                    "tool_name": "investigate_anomaly",
                    "arguments": {"metric_id": "m_revenue_01", "min_severity": "HIGH"},
                    "provider": self.name,
                    "model": model,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif "query" in prompt_lower or "revenue" in prompt_lower or "analytics" in prompt_lower:
                tool_calls.append({
                    "call_id": f"call_{uuid.uuid4().hex[:12]}",
                    "tool_name": "query_analytics",
                    "arguments": {"sql": "SELECT region, product_line, SUM(amount) AS revenue FROM gold_revenue GROUP BY region, product_line"},
                    "provider": self.name,
                    "model": model,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif "search" in prompt_lower or "evidence" in prompt_lower or "knowledge" in prompt_lower:
                tool_calls.append({
                    "call_id": f"call_{uuid.uuid4().hex[:12]}",
                    "tool_name": "search_knowledge",
                    "arguments": {"query": "revenue outage incident Q3 policy", "top_k": 5},
                    "provider": self.name,
                    "model": model,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

        # Grounded response synthesis referencing context evidence
        context_words = [w for w in re.findall(r'\b\w+\b', prompt) if len(w) > 4 and w.lower() not in ["context", "question", "system", "assistant", "user", "source", "prompt"]]
        sample_excerpt = " ".join(context_words[:12]) if context_words else "financial governance policy and quarterly financial audits"

        response_text = (
            f"Based on the retrieved enterprise evidence context regarding {sample_excerpt}, here is the factual synthesis: "
            f"\n\n1. The documentation confirms that {sample_excerpt} rules are strictly enforced [cite_1]."
            f"\n2. Multi-tenant isolation and governance policies require server-side verification [cite_2]."
            f"\n\nIn conclusion, the retrieved evidence provides complete support for the analytical request."
        )

        output_tokens = len(response_text.split())
        latency_ms = (time.time() - start) * 1000.0 + 45.0  # Execution latency

        res = {
            "provider": self.name,
            "model": model,
            "content": response_text,
            "tool_calls": tool_calls,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "latency_ms": round(latency_ms, 2),
            "estimated_cost": round((input_tokens * 0.0000015) + (output_tokens * 0.000002), 6),
            "status": "SUCCESS"
        }
        return res
