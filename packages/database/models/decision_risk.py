"""Decision Risk Assessment and Uncertainty Database Models."""

from sqlalchemy import String, Text, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionRiskAssessmentModel(AEGISBaseModel):
    """Quantitative Risk Assessment model."""

    __tablename__ = "decision_risk_assessments"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    option_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    methodology_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    impact: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    severity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    expected_loss_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    blast_radius: Mapped[str] = mapped_column(String(50), default="LOCALIZED", nullable=False)  # LOCALIZED, REGIONAL, ENTERPRISE_WIDE
    reversibility: Mapped[str] = mapped_column(String(50), default="REVERSIBLE", nullable=False)  # REVERSIBLE, PARTIALLY_REVERSIBLE, IRREVERSIBLE
    policy_sensitivity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_factors_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DecisionUncertaintyModel(AEGISBaseModel):
    """Model-Specific Uncertainty Representation model with explicit provenance."""

    __tablename__ = "decision_uncertainties"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    adapter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    uncertainty_type: Mapped[str] = mapped_column(String(50), default="ALEATORIC", nullable=False)  # ALEATORIC, EPISTEMIC, UNCERTAINTY_UNAVAILABLE, PARTIAL_UNCERTAINTY
    aleatoric_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    epistemic_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence_interval_low: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence_interval_high: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    calibration_state: Mapped[str] = mapped_column(String(50), default="CALIBRATED", nullable=False)
    assumptions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
