"""Compliance Framework Abstraction and Posture Assessment Engine."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from packages.database.models.compliance import ComplianceFrameworkModel, ComplianceAssessmentModel


class ComplianceEngine:
    """Manages compliance framework control mappings and calculates real-time posture scores."""

    FRAMEWORKS = {"SOC_2", "ISO_27001", "GDPR", "INTERNAL_CONTROLS"}

    def evaluate_compliance_posture(
        self,
        framework_name: str,
        active_controls: List[Dict[str, Any]],
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Compute posture score and control pass/fail counts for framework."""
        fname = framework_name.upper()
        total = len(active_controls)
        if total == 0:
            return {
                "assessment_id": str(uuid.uuid4()),
                "framework": fname,
                "score_percent": 100.0,
                "passed_controls": 0,
                "failed_controls": 0,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }

        passed = sum(1 for c in active_controls if c.get("status") in {"PASSED", "SATISFIED", "COMPLIANT"})
        failed = total - passed
        score = (passed / total) * 100.0

        return {
            "assessment_id": str(uuid.uuid4()),
            "framework": fname,
            "score_percent": round(score, 2),
            "passed_controls": passed,
            "failed_controls": failed,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
