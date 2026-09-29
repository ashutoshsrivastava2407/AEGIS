"""LLM Gateway Subsystem Service Facade."""

from typing import Dict, Any, Optional, List
from services.llm.routing.model_router import model_router
from services.llm.prompts.prompt_manager import prompt_manager
from services.llm.safety.guardrails import ai_guardrails
from services.llm.usage.cost_accounting import cost_accounting_engine


class LLMGatewayService:
    """Centralized LLM Gateway Service."""

    def generate(
        self,
        prompt: str,
        preferred_model: str = "aegis-llm-pro",
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        # 1. Inspect Prompt for Safety
        is_safe, sanitized_prompt, safety_events = ai_guardrails.inspect_prompt(prompt, tenant_id=tenant_id)
        if not is_safe:
            return {
                "status": "BLOCKED",
                "content": sanitized_prompt,
                "safety_events": safety_events,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "latency_ms": 0.0,
                "estimated_cost": 0.0
            }

        # 2. Route & Execute LLM Request
        execution_res = model_router.route_and_execute(
            prompt=sanitized_prompt,
            preferred_model=preferred_model,
            system_prompt=system_prompt,
            tools=tools,
            tenant_id=tenant_id
        )

        # 3. Cost & Usage Accounting
        cost_accounting_engine.record_usage(
            tenant_id=tenant_id,
            provider=execution_res["provider"],
            model=execution_res["model"],
            input_tokens=execution_res["input_tokens"],
            output_tokens=execution_res["output_tokens"],
            latency_ms=execution_res["latency_ms"],
            cost=execution_res["estimated_cost"]
        )

        execution_res["safety_events"] = safety_events
        return execution_res

    def get_prompt_template(self, name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        return prompt_manager.get_prompt(name, variables)

    def get_gateway_status(self, tenant_id: str = "default") -> Dict[str, Any]:
        usage_summary = cost_accounting_engine.get_tenant_usage_summary(tenant_id)
        return {
            "status": "OPERATIONAL",
            "circuit_breaker_open": model_router.circuit_breaker_open,
            "providers": ["mock-primary", "mock-fallback"],
            "usage_summary": usage_summary,
            "safety_events_count": len(ai_guardrails.list_events(tenant_id))
        }


llm_gateway_service = LLMGatewayService()
