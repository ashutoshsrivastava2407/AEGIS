"""Policy-driven MFA and Step-Up Authentication Strength Evaluator."""

from typing import Dict, Any


class MFAPolicyManager:
    """Evaluates required authentication strength based on operation risk tier and resource sensitivity."""

    HIGH_RISK_OPERATIONS = {
        "CHANGE_GOVERNANCE_POLICY",
        "APPROVE_PRIVILEGED_ACTION",
        "MODIFY_SECURITY_CONFIG",
        "UPDATE_AGENT_PERMISSIONS",
        "CHANGE_RETENTION_POLICY",
        "BREAK_GLASS_ACTIVATE",
    }

    def evaluate_required_auth_strength(
        self,
        action: str,
        risk_tier: str = "LOW",
        data_classification: str = "INTERNAL",
    ) -> str:
        """Determine required auth strength (NORMAL_AUTH, MFA_REQUIRED, STEP_UP_REQUIRED, PRIVILEGED_AUTH)."""
        act_upper = action.upper()
        risk_upper = risk_tier.upper()
        class_upper = data_classification.upper()

        if act_upper in self.HIGH_RISK_OPERATIONS or risk_upper == "CRITICAL":
            return "PRIVILEGED_AUTH"
        elif risk_upper == "HIGH" or class_upper == "RESTRICTED":
            return "STEP_UP_REQUIRED"
        elif class_upper == "CONFIDENTIAL":
            return "MFA_REQUIRED"
        else:
            return "NORMAL_AUTH"
