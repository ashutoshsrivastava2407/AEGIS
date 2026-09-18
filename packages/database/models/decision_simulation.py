"""Decision Simulation and Scenario Database Models."""

from sqlalchemy import String, Text, JSON, Float, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionSimulationModel(AEGISBaseModel):
    """Scenario & What-If Simulation Run model."""

    __tablename__ = "decision_simulations"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    option_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    simulation_type: Mapped[str] = mapped_column(String(50), default="MONTE_CARLO", nullable=False)  # MONTE_CARLO, DETERMINISTIC
    has_valid_stochastic_basis: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    iterations: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    seed: Mapped[int] = mapped_column(Integer, default=42, nullable=False)
    percentile_p10: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentile_p50: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentile_p90: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    mean_outcome: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    std_dev: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    simulation_engine_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    results_distribution_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DecisionScenarioModel(AEGISBaseModel):
    """What-if scenario parameter configuration model."""

    __tablename__ = "decision_scenarios"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scenario_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parameter_overrides_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    probability_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
