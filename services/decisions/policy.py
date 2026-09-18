"""Server-Side Decision Policy Engine & Authority Evaluator."""

from typing import Dict, Any, List


class ServerDecisionPolicyEngine:
    """Server-Authoritative Policy Engine enforcing enterprise governance boundaries."""

    POLICY_VERSION = "1.0.0"

    def evaluate_policy(
        self,
        tenant_id: str,
        user_role: str,
        decision_type: str,
        cost_usd: float,
        risk_tier: str,
        affected_resources: List[str]
    ) -> Dict[str, Any]:
        """Evaluate policy constraints server-side ignoring client-provided overrides."""
        matched_rules = []
        result = "ALLOW"
        rationale = "Decision complies with standard policy boundaries."

        # 1. Financial Exposure Limits
        if cost_usd > 50000.0:
            matched_rules.append("FINANCIAL_EXPOSURE_EXCEEDS_50K")
            result = "REQUIRE_ESCALATION"
            rationale = f"Cost estimate ${cost_usd:,.2f} exceeds standard $50,000 authority threshold."
        elif cost_usd > 10000.0:
            matched_rules.append("FINANCIAL_EXPOSURE_EXCEEDS_10K")
            if result != "REQUIRE_ESCALATION":
                result = "REQUIRE_APPROVAL"
                rationale = f"Cost estimate ${cost_usd:,.2f} requires approval signoff."

        # 2. Risk Tier Boundaries
        if risk_tier == "CRITICAL_RISK":
            matched_rules.append("CRITICAL_RISK_TIER_POLICY")
            result = "REQUIRE_ESCALATION"
            rationale = "Critical risk tier requires multi-party executive approval."
        elif risk_tier == "HIGH_RISK":
            matched_rules.append("HIGH_RISK_TIER_POLICY")
            if result != "REQUIRE_ESCALATION":
                result = "REQUIRE_APPROVAL"
                rationale = "High risk tier requires dual approval signoff."

        # 3. Protected Infrastructure Resources
        protected_prefixes = ["db:prod", "network:core", "sec:auth"]
        for res in affected_resources:
            if any(res.startswith(prefix) for prefix in protected_prefixes):
                matched_rules.append("PROTECTED_INFRASTRUCTURE_RESOURCE")
                result = "REQUIRE_APPROVAL"
                rationale = f"Affected resource '{res}' requires explicit infrastructure signoff."

        # 4. Strict Tenant Isolation Guard
        if not tenant_id or tenant_id == "invalid":
            matched_rules.append("INVALID_TENANT_BOUNDARY")
            result = "DENY"
            rationale = "Tenant ID is invalid or missing."

        return {
            "policy_name": "AEGIS_Enterprise_Decision_Policy",
            "policy_version": self.POLICY_VERSION,
            "policy_result": result,
            "matched_rules": matched_rules,
            "rationale": rationale,
            "evaluated_conditions": {
                "tenant_id": tenant_id,
                "user_role": user_role,
                "decision_type": decision_type,
                "cost_usd": cost_usd,
                "risk_tier": risk_tier,
                "affected_resources_count": len(affected_resources)
            }
        }
