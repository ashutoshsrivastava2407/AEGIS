"""Decision Evidence Database Model."""

from sqlalchemy import String, Text, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class DecisionEvidenceModel(AEGISBaseModel):
    """Decision Evidence Model tracking multi-source evidence, freshness, authority, and conflict flags."""

    __tablename__ = "decision_evidences"

    decision_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # OBSERVED, CALCULATED, PREDICTED, DOCUMENT, POLICY, AGENT, SIMULATED
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    source_authority: Mapped[str] = mapped_column(String(50), default="SECONDARY", nullable=False)  # AUTHORITATIVE, SECONDARY, INFERRED
    freshness_timestamp: Mapped[str] = mapped_column(String(50), nullable=False)
    is_fresh: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_conflicting: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    conflict_details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
