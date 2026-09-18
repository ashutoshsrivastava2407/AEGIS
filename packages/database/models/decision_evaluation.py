"""Decision Evaluation, Criteria, and Constraint Database Models."""

from sqlalchemy import String, Text, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionCriterionModel(AEGISBaseModel):
    """Versioned MCDA Criterion model with units, scale, currency, and weight configuration."""

    __tablename__ = "decision_criteria"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    criterion_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), default="SCALAR", nullable=False)  # USD, INR, PERCENT, HOURS, RATIO, SCALAR
    scale: Mapped[str] = mapped_column(String(50), default="LINEAR", nullable=False)  # LINEAR, LOGARITHMIC, STEP
    currency: Mapped[str] = mapped_column(String(10), nullable=True)  # USD, EUR, INR
    time_period: Mapped[str] = mapped_column(String(50), default="ANNUAL", nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    normalization_method: Mapped[str] = mapped_column(String(50), default="MIN_MAX", nullable=False)
    normalization_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    criterion_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    owner: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class DecisionEvaluationModel(AEGISBaseModel):
    """MCDA evaluation output model per option."""

    __tablename__ = "decision_evaluations"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    option_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    mcda_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    expected_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    net_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_adjusted_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_pareto_efficient: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_dominated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sensitivity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    criterion_breakdown_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    evaluation_metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DecisionConstraintModel(AEGISBaseModel):
    """Hard business or policy constraint evaluation model."""

    __tablename__ = "decision_constraints"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    constraint_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    constraint_type: Mapped[str] = mapped_column(String(50), default="HARD", nullable=False)  # HARD, SOFT
    threshold_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    operator: Mapped[str] = mapped_column(String(20), default="<=", nullable=False)  # <=, >=, ==, !=
    is_satisfied: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
