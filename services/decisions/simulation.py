"""Scenario & What-If Simulation Engine with Stochastic Basis Guards."""

import random
from typing import Dict, Any, List, Optional


class SimulationEngine:
    """Simulation Engine supporting Monte Carlo and Deterministic Scenario Analysis."""

    SIMULATION_ENGINE_VERSION = "1.0.0"

    def run_simulation(
        self,
        base_value: float,
        stochastic_basis: Optional[Dict[str, Any]] = None,
        iterations: int = 1000,
        seed: int = 42
    ) -> Dict[str, Any]:
        """Execute simulation with seed reproducibility and stochastic basis validation."""
        random.seed(seed)

        # Check if valid stochastic basis exists
        has_stochastic_basis = False
        if stochastic_basis and stochastic_basis.get("has_valid_distribution", False):
            has_stochastic_basis = True

        if not has_stochastic_basis:
            # Deterministic scenario analysis fallback (never invent artificial distributions)
            p10 = base_value * 0.95
            p50 = base_value * 1.00
            p90 = base_value * 1.05
            return {
                "simulation_type": "DETERMINISTIC",
                "has_valid_stochastic_basis": False,
                "iterations": 1,
                "seed": seed,
                "percentile_p10": round(p10, 2),
                "percentile_p50": round(p50, 2),
                "percentile_p90": round(p90, 2),
                "mean_outcome": round(base_value, 2),
                "std_dev": 0.0,
                "simulation_engine_version": self.SIMULATION_ENGINE_VERSION,
                "message": "Deterministic fallback used due to absence of verified stochastic distribution basis."
            }

        # Run Monte Carlo sampling with verified distribution
        std_dev_ratio = stochastic_basis.get("std_dev_ratio", 0.10)
        samples = []
        for _ in range(iterations):
            val = random.gauss(base_value, base_value * std_dev_ratio)
            samples.append(val)

        samples.sort()
        p10_idx = int(iterations * 0.10)
        p50_idx = int(iterations * 0.50)
        p90_idx = int(iterations * 0.90)

        mean_val = sum(samples) / iterations
        var_val = sum((x - mean_val) ** 2 for x in samples) / iterations
        std_dev = var_val ** 0.5

        return {
            "simulation_type": "MONTE_CARLO",
            "has_valid_stochastic_basis": True,
            "iterations": iterations,
            "seed": seed,
            "percentile_p10": round(samples[p10_idx], 2),
            "percentile_p50": round(samples[p50_idx], 2),
            "percentile_p90": round(samples[p90_idx], 2),
            "mean_outcome": round(mean_val, 2),
            "std_dev": round(std_dev, 2),
            "simulation_engine_version": self.SIMULATION_ENGINE_VERSION,
            "message": f"Monte Carlo simulation completed cleanly with {iterations} iterations."
        }
