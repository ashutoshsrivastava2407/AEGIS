"""Decision Option Database Model."""

from sqlalchemy import String, Text, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionOptionModel(AEGISBaseModel):
    """Decision Option Model representing structured strategies & action proposals."""

    __tablename__ = "decision_options"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    option_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    option_type: Mapped[str] = mapped_column(String(50), default="CUSTOM", nullable=False, index=True)  # RECOMMENDED, BASELINE, CONSERVATIVE, AGGRESSIVE, CUSTOM
    actions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    assumptions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    expected_impact_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    cost_estimate_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reversibility_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    affected_resources_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    constraints_satisfied: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_feasible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
