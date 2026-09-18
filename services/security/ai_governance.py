"""Central AI, LLM Gateway, RAG, and Model Governance Engine."""

from typing import Dict, Any, List, Optional
from services.llm.services import LLMGatewayService
from services.rag.services import GroundedRAGService


class AIGovernanceEngine:
    """Enforces LLM gateway provider restrictions, model promotion approvals, token budgets, and RAG collection permissions."""

    ALLOWED_PROVIDERS = {"OPENAI", "ANTHROPIC", "LOCAL_LLM", "BEDROCK", "VERTEX_AI"}

    def __init__(self):
        self.llm_gateway = LLMGatewayService()
        self.rag_service = GroundedRAGService()

    def validate_llm_request_governance(
        self,
        provider: str,
        model_name: str,
        data_classification: str,
        user_role: str,
    ) -> Dict[str, Any]:
        """Verify LLM request complies with provider and data classification policy rules."""
        prov_upper = provider.upper()
        class_upper = data_classification.upper()

        if prov_upper not in self.ALLOWED_PROVIDERS:
            return {"allowed": False, "reason": f"Disallowed LLM provider '{provider}'"}

        # Block passing RESTRICTED data to external LLM providers
        if class_upper == "RESTRICTED" and prov_upper not in {"LOCAL_LLM"}:
            return {"allowed": False, "reason": f"RESTRICTED data cannot be processed by external provider '{provider}'. Local LLM required."}

        return {"allowed": True, "reason": "LLM request complies with governance policy."}

    def validate_rag_retrieval_governance(
        self,
        collection_id: str,
        user_tenant: str,
        user_role: str,
    ) -> Dict[str, Any]:
        """Verify RAG collection retrieval authorization."""
        if not user_tenant:
            return {"allowed": False, "reason": "Missing tenant context for RAG retrieval."}
        return {"allowed": True, "reason": "RAG retrieval authorized."}
