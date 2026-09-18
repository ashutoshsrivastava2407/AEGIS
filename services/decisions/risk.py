"""Quantitative Risk Engine & Hazard Classification."""

from typing import Dict, Any, List


class QuantitativeRiskEngine:
    """Calculates explicit quantitative risk scores, expected loss, blast radius, and reversibility."""

    METHODOLOGY_VERSION = "1.0.0"

    def assess_risk(
        self,
        probability: float,
        impact_usd: float,
        affected_services_count: int = 1,
        is_irreversible: bool = False,
        policy_rules_count: int = 0
    ) -> Dict[str, Any]:
        """Compute quantitative risk assessment."""
        prob = min(1.0, max(0.0, probability))
        impact = max(0.0, impact_usd)
        
        # Expected Financial Loss = P * Impact
        expected_loss = prob * impact

        # Severity Score calculation (0.0 to 1.0)
        base_severity = (prob * 0.4) + (min(1.0, impact / 50000.0) * 0.6)
        
        # Blast Radius classification
        if affected_services_count > 5:
            blast_radius = "ENTERPRISE_WIDE"
            base_severity = min(1.0, base_severity * 1.3)
        elif affected_services_count > 1:
            blast_radius = "REGIONAL"
            base_severity = min(1.0, base_severity * 1.1)
        else:
            blast_radius = "LOCALIZED"

        reversibility = "IRREVERSIBLE" if is_irreversible else "REVERSIBLE"
        if is_irreversible:
            base_severity = min(1.0, base_severity * 1.25)

        # Risk Tier Classification
        if base_severity >= 0.75:
            risk_tier = "CRITICAL_RISK"
        elif base_severity >= 0.50:
            risk_tier = "HIGH_RISK"
        elif base_severity >= 0.25:
            risk_tier = "MEDIUM_RISK"
        else:
            risk_tier = "LOW_RISK"

        return {
            "methodology_version": self.METHODOLOGY_VERSION,
            "probability": round(prob, 4),
            "impact_usd": round(impact, 2),
            "severity_score": round(base_severity, 4),
            "expected_loss_usd": round(expected_loss, 2),
            "blast_radius": blast_radius,
            "reversibility": reversibility,
            "risk_tier": risk_tier,
            "policy_sensitivity": round(policy_rules_count * 0.1, 2)
        }
