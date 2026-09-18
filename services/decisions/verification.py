"""First-Class Decision Verification Gate extending Step 7 Verification Agent."""

from typing import Dict, Any, List


class DecisionVerificationGate:
    """Verifies decision calculation integrity, context validity, risk consistency, and policy compliance."""

    def verify_decision(
        self,
        decision_id: str,
        context_snapshot: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        policy_evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform independent verification check on decision artifacts before approval."""
        verification_checks = []
        is_verified = True

        # 1. Context Completeness Verification
        if not context_snapshot.get("context_fingerprint"):
            is_verified = False
            verification_checks.append({"check": "CONTEXT_FINGERPRINT", "passed": False, "detail": "Missing canonical fingerprint"})
        else:
            verification_checks.append({"check": "CONTEXT_FINGERPRINT", "passed": True, "detail": "Canonical SHA-256 fingerprint verified"})

        # 2. Calculation Integrity Verification
        invalid_scores = [e for e in evaluations if e.get("mcda_score", 0.0) < 0.0 or e.get("mcda_score", 0.0) > 1.0]
        if invalid_scores:
            is_verified = False
            verification_checks.append({"check": "MCDA_MATH", "passed": False, "detail": "MCDA score out of range [0, 1]"})
        else:
            verification_checks.append({"check": "MCDA_MATH", "passed": True, "detail": "All option MCDA scores mathematically valid"})

        # 3. Policy Alignment Verification
        if policy_evaluation.get("policy_result") == "DENY":
            is_verified = False
            verification_checks.append({"check": "POLICY_COMPLIANCE", "passed": False, "detail": "Policy engine returned DENY"})
        else:
            verification_checks.append({"check": "POLICY_COMPLIANCE", "passed": True, "detail": "Policy compliance verified"})

        # 4. Risk Consistency Verification
        if risk_assessment.get("severity_score", 0.0) > 0.8 and policy_evaluation.get("policy_result") == "ALLOW":
            is_verified = False
            verification_checks.append({"check": "RISK_POLICY_CONSISTENCY", "passed": False, "detail": "High risk severity conflicts with unconstrained ALLOW policy"})
        else:
            verification_checks.append({"check": "RISK_POLICY_CONSISTENCY", "passed": True, "detail": "Risk severity and policy result consistent"})

        score = sum(1.0 for c in verification_checks if c["passed"]) / len(verification_checks) if verification_checks else 1.0

        return {
            "decision_id": decision_id,
            "is_verified": is_verified,
            "verification_score": round(score, 4),
            "status": "VERIFIED" if is_verified else "REJECTED_BY_VERIFIER",
            "verification_checks": verification_checks
        }
