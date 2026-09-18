"""Deterministic Data Health Score Calculator."""

from typing import Dict, Any, List


class DataHealthScorer:
    """Calculates Data Health Score (0.0 to 100.0) from quality check pass rates."""

    DEFAULT_WEIGHTS: Dict[str, float] = {
        "COMPLETENESS": 0.25,
        "VALIDITY": 0.25,
        "UNIQUENESS": 0.20,
        "FRESHNESS": 0.15,
        "CONSISTENCY": 0.10,
        "VOLUME": 0.05,
    }

    def calculate_health_score(self, check_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not check_results:
            return {
                "overall_score": 100.0,
                "dimension_scores": {dim: 100.0 for dim in self.DEFAULT_WEIGHTS},
                "status": "HEALTHY",
            }

        dimension_totals: Dict[str, int] = {}
        dimension_passed: Dict[str, int] = {}

        for result in check_results:
            check_type = result.get("check_type", "VALIDITY").upper()
            status = result.get("check_status", "PASSED").upper()

            dimension_totals[check_type] = dimension_totals.get(check_type, 0) + 1
            if status == "PASSED":
                dimension_passed[check_type] = dimension_passed.get(check_type, 0) + 1

        dimension_scores: Dict[str, float] = {}
        total_weight = 0.0
        weighted_score_sum = 0.0

        for dim, weight in self.DEFAULT_WEIGHTS.items():
            tot = dimension_totals.get(dim, 0)
            if tot > 0:
                pass_rate = dimension_passed.get(dim, 0) / tot
                score = pass_rate * 100.0
            else:
                score = 100.0  # Default un-checked dimensions pass baseline

            dimension_scores[dim] = round(score, 1)
            weighted_score_sum += score * weight
            total_weight += weight

        overall_score = round(weighted_score_sum / total_weight, 1) if total_weight > 0 else 100.0

        status = "HEALTHY"
        if overall_score < 70.0:
            status = "CRITICAL"
        elif overall_score < 90.0:
            status = "WARNING"

        return {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "status": status,
        }


health_scorer = DataHealthScorer()
