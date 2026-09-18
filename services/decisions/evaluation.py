"""Unit-Aware Multi-Criteria Decision Analysis (MCDA), Pareto & Sensitivity Engine."""

import math
from typing import Dict, Any, List


class MCDAEvaluator:
    """Mathematical Multi-Criteria Decision Analysis (MCDA) engine."""

    def evaluate_options(
        self,
        options: List[Dict[str, Any]],
        criteria: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Evaluate options across criteria using Weighted Linear Combination, EV, RAV, Pareto & Sensitivity."""
        if not options or not criteria:
            return []

        evaluations = []
        total_weight = sum(c.get("weight", 1.0) for c in criteria)
        norm_weights = {c["criterion_key"]: (c.get("weight", 1.0) / total_weight) if total_weight > 0 else 1.0 / len(criteria) for c in criteria}

        # 1. Compute raw criteria scores per option
        for opt in options:
            breakdown = {}
            wlc_score = 0.0

            for c in criteria:
                ckey = c["criterion_key"]
                w = norm_weights[ckey]
                unit = c.get("unit", "SCALAR")
                
                # Extract value
                if ckey == "EXPECTED_BENEFIT":
                    raw_val = opt.get("expected_impact", {}).get("expected_revenue_delta_usd", 0.0)
                    norm_val = min(1.0, max(0.0, raw_val / 50000.0))
                elif ckey == "COST":
                    raw_val = opt.get("cost_estimate_usd", 0.0)
                    norm_val = max(0.0, 1.0 - (raw_val / 10000.0))
                elif ckey == "RISK":
                    raw_val = opt.get("risk_score", 0.0)
                    norm_val = max(0.0, 1.0 - raw_val)
                elif ckey == "REVERSIBILITY":
                    raw_val = opt.get("reversibility_score", 1.0)
                    norm_val = raw_val
                else:
                    raw_val = 1.0
                    norm_val = 1.0

                contribution = w * norm_val
                wlc_score += contribution
                breakdown[ckey] = {
                    "raw_value": round(raw_val, 4),
                    "unit": unit,
                    "normalized_value": round(norm_val, 4),
                    "weight": round(w, 4),
                    "contribution": round(contribution, 4)
                }

            benefit = opt.get("expected_impact", {}).get("expected_revenue_delta_usd", 0.0)
            cost = opt.get("cost_estimate_usd", 0.0)
            risk = opt.get("risk_score", 0.0)
            
            # Expected Value & Net Value calculations
            net_val = benefit - cost
            ev = benefit * (1.0 - risk)
            rav = net_val - (risk * cost * 1.5)  # explicit risk penalty formula

            evaluations.append({
                "option_key": opt["option_key"],
                "option_title": opt.get("title", ""),
                "mcda_score": round(wlc_score, 4),
                "expected_value": round(ev, 2),
                "net_value": round(net_val, 2),
                "risk_adjusted_value": round(rav, 2),
                "is_pareto_efficient": True,  # computed below
                "is_dominated": False,
                "sensitivity_score": 0.0,
                "criterion_breakdown": breakdown
            })

        # 2. Pareto Dominance Analysis
        for i in range(len(evaluations)):
            for j in range(len(evaluations)):
                if i == j:
                    continue
                e1 = evaluations[i]
                e2 = evaluations[j]

                # Check if e2 strictly dominates e1 (higher score, higher EV, lower cost/risk)
                if e2["mcda_score"] >= e1["mcda_score"] and \
                   e2["expected_value"] >= e1["expected_value"] and \
                   e2["risk_adjusted_value"] >= e1["risk_adjusted_value"] and \
                   (e2["mcda_score"] > e1["mcda_score"] or e2["risk_adjusted_value"] > e1["risk_adjusted_value"]):
                    e1["is_dominated"] = True
                    e1["is_pareto_efficient"] = False
                    break

        # 3. Sensitivity Analysis (perturb weights by +/- 20%)
        for ev_item in evaluations:
            base_score = ev_item["mcda_score"]
            var_sum = 0.0
            for ckey, bdata in ev_item["criterion_breakdown"].items():
                perturbed_w = bdata["weight"] * 1.2
                perturbed_contrib = perturbed_w * bdata["normalized_value"]
                var_sum += abs(perturbed_contrib - bdata["contribution"])
            ev_item["sensitivity_score"] = round(var_sum, 4)

        return evaluations
