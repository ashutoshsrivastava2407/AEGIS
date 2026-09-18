"""LLM Gateway Model Routing Engine."""

import time
from typing import Dict, Any, Optional, List
from services.llm.providers.base_provider import BaseLLMProvider, MockLLMProvider


class ModelRouter:
    """Configurable model router supporting primary and fallback providers with circuit breakers."""

    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {
            "primary": MockLLMProvider("primary"),
            "fallback": MockLLMProvider("fallback")
        }
        self.circuit_breaker_open = False
        self.failure_count = 0
        self.max_failures = 3

    def route_and_execute(
        self,
        prompt: str,
        preferred_model: str = "aegis-llm-pro",
        system_prompt: Optional[str] = None,
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        # Try Primary Provider
        if not self.circuit_breaker_open:
            try:
                res = self._providers["primary"].generate_chat(
                    model=preferred_model,
                    prompt=prompt,
                    system_prompt=system_prompt
                )
                res["routing_execution"] = "PRIMARY"
                res["tenant_id"] = tenant_id
                return res
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= self.max_failures:
                    self.circuit_breaker_open = True

        # Fallback Routing Execution
        res = self._providers["fallback"].generate_chat(
            model=f"{preferred_model}-fallback",
            prompt=prompt,
            system_prompt=system_prompt
        )
        res["routing_execution"] = "FALLBACK"
        res["tenant_id"] = tenant_id
        return res


model_router = ModelRouter()
