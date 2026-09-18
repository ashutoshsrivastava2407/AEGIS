"""AI Platform Application Service."""

from typing import Dict, Any, List
from packages.security import UserContext


class AIService:
    async def get_gateway_status(self, user: UserContext) -> Dict[str, Any]:
        return {
            "status": "OPERATIONAL",
            "provider_routes": ["PRIMARY_LLM", "FALLBACK_LLM"],
            "token_budget_remaining": 1000000,
        }

    async def list_agent_runs(self, user: UserContext) -> List[Dict[str, Any]]:
        return []

    async def list_knowledge_collections(self, user: UserContext) -> List[Dict[str, Any]]:
        return []


ai_service = AIService()
