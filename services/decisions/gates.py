"""Data-Health, Model-Health, Integrity, and Execution Eligibility Gates."""

from typing import Dict, Any, List


class DecisionIntegrityEvaluator:
    """Evaluates machine integrity state: VALID, DEGRADED, HUMAN_REVIEW_REQUIRED, BLOCKED."""

    @staticmethod
    def evaluate(
        data_quality_score: float,
        data_freshness_seconds: float,
        model_health_score: float,
        evidence_conflict_detected: bool,
        policy_result: str = "ALLOW"
    ) -> Dict[str, Any]:
        """Compute integrity status and rationale."""
        reasons = []

        if policy_result == "DENY":
            return {
                "status": "BLOCKED",
                "rationale": "Policy engine evaluated result as DENY.",
                "reasons": ["Policy DENY"]
            }

        if data_quality_score < 0.70:
            reasons.append(f"Low data quality score: {data_quality_score:.2f} < 0.70")
        
        if data_freshness_seconds > 86400:  # > 24 hours stale
            reasons.append(f"Stale data context: {data_freshness_seconds} seconds old")

        if model_health_score < 0.60:
            reasons.append(f"Low model health score: {model_health_score:.2f} < 0.60")

        if evidence_conflict_detected:
            reasons.append("Contradictory evidence detected across input sources")

        if len(reasons) >= 2 or data_quality_score < 0.50:
            return {
                "status": "BLOCKED",
                "rationale": "Severe integrity issues detected: " + "; ".join(reasons),
                "reasons": reasons
            }
        elif len(reasons) == 1:
            if evidence_conflict_detected or model_health_score < 0.75:
                return {
                    "status": "HUMAN_REVIEW_REQUIRED",
                    "rationale": "Human review required due to: " + "; ".join(reasons),
                    "reasons": reasons
                }
            else:
                return {
                    "status": "DEGRADED",
                    "rationale": "Decision operating in degraded state due to: " + "; ".join(reasons),
                    "reasons": reasons
                }

        return {
            "status": "VALID",
            "rationale": "Decision context, data quality, model health, and policy checks are valid.",
            "reasons": []
        }


class DecisionEligibilityEvaluator:
    """Evaluates execution eligibility: ANALYSIS_ONLY, RECOMMENDATION_ONLY, APPROVAL_REQUIRED, AUTO_EXECUTION_ELIGIBLE, EXECUTION_BLOCKED."""

    @staticmethod
    def evaluate(
        integrity_status: str,
        risk_tier: str,
        approval_status: str,
        execution_required: bool = True
    ) -> Dict[str, Any]:
        """Compute execution eligibility state and rationale."""
        if not execution_required:
            return {
                "status": "ANALYSIS_ONLY",
                "rationale": "Decision is configured for analysis only; no execution required."
            }

        if integrity_status == "BLOCKED":
            return {
                "status": "EXECUTION_BLOCKED",
                "rationale": "Execution blocked due to invalid decision integrity status."
            }

        if approval_status == "REJECTED":
            return {
                "status": "EXECUTION_BLOCKED",
                "rationale": "Execution blocked because decision approval was REJECTED."
            }

        if approval_status == "INVALIDATED":
            return {
                "status": "EXECUTION_BLOCKED",
                "rationale": "Execution blocked because decision approval was INVALIDATED due to material context changes."
            }

        if approval_status == "APPROVED":
            return {
                "status": "AUTO_EXECUTION_ELIGIBLE" if risk_tier == "LOW_RISK" else "APPROVAL_REQUIRED",
                "rationale": "Decision is approved and eligible for execution."
            }

        if risk_tier in ("HIGH_RISK", "CRITICAL_RISK", "MEDIUM_RISK"):
            return {
                "status": "APPROVAL_REQUIRED",
                "rationale": f"Execution requires explicit human signoff for {risk_tier} decision."
            }

        return {
            "status": "RECOMMENDATION_ONLY",
            "rationale": "Decision recommendation prepared; pending human authorization."
        }
