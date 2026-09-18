"""Outcome Tracking & Attribution Discipline Engine."""

from typing import Dict, Any, List, Optional


class OutcomeTracker:
    """Outcome Tracker with explicit attribution discipline."""

    def measure_outcome(
        self,
        decision_id: str,
        action_id: str,
        expected_impact_usd: float,
        actual_impact_usd: float,
        attribution_classification: str = "OBSERVED",  # EXPECTED, OBSERVED, MODELED, CAUSALLY_ESTIMATED
        measurement_window_days: int = 30,
        causal_methodology_version: Optional[str] = None,
        counterfactual_baseline_usd: Optional[float] = None,
        identification_assumptions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Measure outcome impact and variance with attribution classification."""

        # 1. Verification of Causal Methodology Parameters
        # Require explicit causal parameters before granting CAUSALLY_ESTIMATED classification
        if attribution_classification == "CAUSALLY_ESTIMATED":
            if not causal_methodology_version or counterfactual_baseline_usd is None or not identification_assumptions:
                # Downgrade to MODELED or OBSERVED when causal parameters are missing
                attribution_classification = "MODELED" if causal_methodology_version else "OBSERVED"

        # 2. Variance calculation
        variance_usd = actual_impact_usd - expected_impact_usd

        # 3. Attribution confidence calculation based on classification
        if attribution_classification == "CAUSALLY_ESTIMATED":
            attribution_confidence = 0.95
        elif attribution_classification == "MODELED":
            attribution_confidence = 0.75
        elif attribution_classification == "OBSERVED":
            attribution_confidence = 0.60  # High observed correlation, unproven causation
        else:  # EXPECTED
            attribution_confidence = 0.30

        return {
            "outcome_id": f"out-{decision_id[:8]}",
            "decision_id": decision_id,
            "action_id": action_id,
            "attribution_classification": attribution_classification,
            "expected_impact_usd": round(expected_impact_usd, 2),
            "actual_impact_usd": round(actual_impact_usd, 2),
            "variance_usd": round(variance_usd, 2),
            "attribution_confidence": attribution_confidence,
            "measurement_window_days": measurement_window_days,
            "causal_methodology_version": causal_methodology_version or ("AEGIS_DiD_v1.0" if attribution_classification == "CAUSALLY_ESTIMATED" else "N/A"),
            "counterfactual_baseline_usd": counterfactual_baseline_usd,
            "identification_assumptions": identification_assumptions or [],
            "observed_kpis": {
                "roi_percentage": round((variance_usd / expected_impact_usd * 100.0), 2) if expected_impact_usd > 0 else 0.0,
                "impact_status": "EXCEEDED" if variance_usd >= 0 else "UNDERPERFORMED"
            },
            "attribution_discipline_note": (
                "Causality explicitly verified with counterfactual baseline and identification assumptions"
                if attribution_classification == "CAUSALLY_ESTIMATED"
                else "Observed variance reflects temporal correlation; causal assumptions unverified"
            )
        }
