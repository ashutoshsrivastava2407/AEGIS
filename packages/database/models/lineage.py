"""Data & Decision Lineage Edge Database Model."""

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class LineageEdgeModel(AEGISBaseModel):
    __tablename__ = "lineage_edges"

    upstream_entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    upstream_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SOURCE, INGESTION, DATASET, MODEL, DECISION
    downstream_entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    downstream_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), default="TRANSFORMS_TO", nullable=False)
    transformation_job: Mapped[str] = mapped_column(String(255), nullable=True)
    execution_run_id: Mapped[str] = mapped_column(String(255), nullable=True)
    edge_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
